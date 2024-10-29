import json
import uuid
from datetime import datetime
from kubernetes import client, config

def lambda_handler(event, context):
    # Extract operation ID from the incoming request or generate if not provided
    operation_id = event.get("operation_id", str(uuid.uuid4()))
    request_id = str(uuid.uuid4())  # Unique ID for tracking this specific request
    start_time = datetime.utcnow()
    timestamp = start_time.isoformat() + "Z"  # UTC start timestamp in ISO format

    # Load Kubernetes config
    config.load_kube_config()
    v1_core = client.CoreV1Api()

    # Extract other parameters
    namespace = event.get("namespace", "default")
    pod_name = event.get("pod_name")
    response_steps = []

    # Step 1: Attempt to delete the specified pod
    try:
        step_detail = {"step": "delete_pod", "request_id": request_id}
        step_detail["request"] = f"Delete pod '{pod_name}' in namespace '{namespace}' with operation ID '{operation_id}'."
        v1_core.delete_namespaced_pod(name=pod_name, namespace=namespace)
        step_detail["response"] = f"Pod '{pod_name}' deleted successfully."
        response_steps.append(step_detail)

        # Step 2: Monitor for replacement pod
        new_pod_list = v1_core.list_namespaced_pod(namespace=namespace, label_selector=f"app={pod_name.split('-')[0]}").items
        replacement_pod_names = [p.metadata.name for p in new_pod_list if p.metadata.name != pod_name]
        
        # Calculate end time and duration
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        # Step 3: Summary
        response_steps.append({
            "step": "summary",
            "operation_id": operation_id,
            "request_id": request_id,
            "timestamp": timestamp,
            "start_time": start_time.isoformat() + "Z",
            "end_time": end_time.isoformat() + "Z",
            "duration_seconds": duration,
            "replaced_pod": pod_name,
            "replacement_pods": replacement_pod_names,
            "response": f"Pod '{pod_name}' recycled. Replacement pod(s): {replacement_pod_names}"
        })

    except client.exceptions.ApiException as e:
        response_steps.append({"step": "delete_pod", "response": f"Error deleting pod '{pod_name}': {str(e)}", "request_id": request_id})
        return {"statusCode": e.status, "body": json.dumps({"operation_id": operation_id, "request_id": request_id, "timestamp": timestamp, "steps": response_steps})}

    return {"statusCode": 200, "body": json.dumps({"operation_id": operation_id, "request_id": request_id, "timestamp": timestamp, "steps": response_steps})}
