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
    v1_apps = client.AppsV1Api()

    # Extract other parameters
    namespace = event.get("namespace", "default")
    pod_name = event.get("pod_name")
    additional_replicas = event.get("additional_replicas", 1)
    response_steps = []

    # Step 1: Identify ReplicaSet and Deployment
    try:
        step_detail = {"step": "identify_resources", "request_id": request_id}
        step_detail["request"] = f"Retrieve pod '{pod_name}' in namespace '{namespace}' with operation ID '{operation_id}'."
        pod = v1_core.read_namespaced_pod(name=pod_name, namespace=namespace)
        replica_set_name = next((owner.name for owner in pod.metadata.owner_references if owner.kind == "ReplicaSet"), None)

        if not replica_set_name:
            step_detail["response"] = f"Error: ReplicaSet not found for pod '{pod_name}'."
            response_steps.append(step_detail)
            return {"statusCode": 404, "body": json.dumps({"operation_id": operation_id, "timestamp": timestamp, "steps": response_steps})}

        step_detail["response"] = f"Found ReplicaSet '{replica_set_name}' for pod '{pod_name}'."
        response_steps.append(step_detail)

        # Get deployment name if available
        deployment = v1_apps.read_namespaced_replica_set(name=replica_set_name, namespace=namespace)
        deployment_name = next((owner.name for owner in deployment.metadata.owner_references if owner.kind == "Deployment"), None)

        # Step 2: Get initial pod list
        initial_pods = v1_core.list_namespaced_pod(namespace=namespace, label_selector=f"app={replica_set_name}").items
        initial_pod_names = [p.metadata.name for p in initial_pods]

        # Step 3: Calculate New Replica Count
        step_detail = {"step": "calculate_replicas", "request_id": request_id}
        current_replicas = deployment.spec.replicas
        new_replicas = current_replicas + additional_replicas
        step_detail["request"] = f"Increase replicas of '{replica_set_name}' by {additional_replicas} for pod '{pod_name}' with operation ID '{operation_id}'."

        # Apply the new replica count
        deployment.spec.replicas = new_replicas
        v1_apps.patch_namespaced_replica_set(name=replica_set_name, namespace=namespace, body=deployment)
        step_detail["response"] = f"Scaled to {new_replicas} replicas from {current_replicas} for pod '{pod_name}'."
        response_steps.append(step_detail)

        # Step 4: Get final pod list and identify affected pods
        final_pods = v1_core.list_namespaced_pod(namespace=namespace, label_selector=f"app={replica_set_name}").items
        final_pod_names = [p.metadata.name for p in final_pods]

        # Identify added, removed, and untouched pods
        added_pods = list(set(final_pod_names) - set(initial_pod_names))
        removed_pods = list(set(initial_pod_names) - set(final_pod_names))
        untouched_pods = list(set(final_pod_names) & set(initial_pod_names))

        # Calculate end time and duration
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        response_steps.append({
            "step": "summary",
            "operation_id": operation_id,
            "request_id": request_id,
            "timestamp": timestamp,
            "start_time": start_time.isoformat() + "Z",
            "end_time": end_time.isoformat() + "Z",
            "duration_seconds": duration,
            "replica_set": replica_set_name,
            "deployment": deployment_name,
            "added_pods": added_pods,
            "removed_pods": removed_pods,
            "untouched_pods": untouched_pods,
            "response": f"{len(added_pods)} pods added, {len(removed_pods)} pods removed, {len(untouched_pods)} pods untouched."
        })

    except client.exceptions.ApiException as e:
        response_steps.append({"step": "calculate_replicas", "response": f"Error for pod '{pod_name}': {str(e)}", "request_id": request_id})
        return {"statusCode": e.status, "body": json.dumps({"operation_id": operation_id, "request_id": request_id, "timestamp": timestamp, "steps": response_steps})}

    return {"statusCode": 200, "body": json.dumps({"operation_id": operation_id, "request_id": request_id, "timestamp": timestamp, "steps": response_steps})}
