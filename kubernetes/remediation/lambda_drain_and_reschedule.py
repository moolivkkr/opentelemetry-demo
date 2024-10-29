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

    # Extract parameters
    node_name = event.get("node_name")
    namespace = event.get("namespace", "default")
    response_steps = []

    # Step 1: Cordon the specified node to prevent new pods from scheduling
    try:
        step_detail = {"step": "cordon_node", "request_id": request_id}
        step_detail["request"] = f"Cordon node '{node_name}' with operation ID '{operation_id}'."
        body = {"spec": {"unschedulable": True}}
        v1_core.patch_node(name=node_name, body=body)
        step_detail["response"] = f"Node '{node_name}' cordoned successfully."
        response_steps.append(step_detail)

        # Step 2: Drain all pods from the node
        step_detail = {"step": "drain_pods", "request_id": request_id}
        step_detail["request"] = f"Drain all pods from node '{node_name}' in namespace '{namespace}'."
        pods_to_drain = v1_core.list_namespaced_pod(namespace=namespace, field_selector=f"spec.nodeName={node_name}").items
        drained_pod_names = []

        for pod in pods_to_drain:
            v1_core.delete_namespaced_pod(name=pod.metadata.name, namespace=namespace)
            drained_pod_names.append(pod.metadata.name)
            response_steps.append({
                "step": "evict_pod",
                "request_id": request_id,
                "request": f"Evict pod '{pod.metadata.name}' from node '{node_name}'.",
                "response": f"Pod '{pod.metadata.name}' evicted successfully."
            })

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
            "node": node_name,
            "drained_pods": drained_pod_names,
            "response": f"Node '{node_name}' cordoned and drained. Drained pod(s): {drained_pod_names}"
        })

    except client.exceptions.ApiException as e:
        response_steps.append({"step": "cordon_node", "response": f"Error cordoning or draining node '{node_name}': {str(e)}", "request_id": request_id})
        return {"statusCode": e.status, "body": json.dumps({"operation_id": operation_id, "request_id": request_id, "timestamp": timestamp, "steps": response_steps})}

    return {"statusCode": 200, "body": json.dumps({"operation_id": operation_id, "request_id": request_id, "timestamp": timestamp, "steps": response_steps})}
