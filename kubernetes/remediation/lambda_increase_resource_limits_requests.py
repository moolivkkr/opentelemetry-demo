import json
import uuid
from datetime import datetime
from kubernetes import client, config

def lambda_handler(event, context):
    # Generate a unique operation ID and capture start time
    operation_id = str(uuid.uuid4())
    start_time = datetime.utcnow()
    timestamp = start_time.isoformat() + "Z"  # UTC start timestamp in ISO format

    # Load Kubernetes config
    config.load_kube_config()
    v1_core = client.CoreV1Api()
    v1_apps = client.AppsV1Api()

    # Extract parameters
    namespace = event.get("namespace", "default")
    pod_name = event.get("pod_name")
    increase_by = event.get("increase_by", 25)  # percentage to increase
    response_steps = []

    # Step 1: Identify Deployment and ReplicaSet
    try:
        step_detail = {"step": "identify_resources"}
        step_detail["request"] = f"Retrieve pod '{pod_name}' in namespace '{namespace}'."
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

        # Step 2: Update Resource Limits
        step_detail = {"step": "update_resources"}
        container = deployment.spec.template.spec.containers[0]
        current_limits = container.resources.limits["cpu"]
        updated_limits = str(int(current_limits.rstrip("m")) * (1 + increase_by / 100)) + "m"
        container.resources.limits["cpu"] = updated_limits

        v1_apps.patch_namespaced_replica_set(name=replica_set_name, namespace=namespace, body=deployment)
        step_detail["request"] = f"Increase CPU limits of '{replica_set_name}' by {increase_by}% for pod '{pod_name}'."
        step_detail["response"] = f"CPU limits increased to {updated_limits} from {current_limits}."
        response_steps.append(step_detail)

        # Step 3: Calculate time and duration
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        response_steps.append({
            "step": "summary",
            "operation_id": operation_id,
            "timestamp": timestamp,
            "start_time": start_time.isoformat() + "Z",
            "end_time": end_time.isoformat() + "Z",
            "duration_seconds": duration,
            "replica_set": replica_set_name,
            "deployment": deployment_name,
            "added_pods": [],
            "removed_pods": [],
            "untouched_pods": [pod_name],
            "response": "CPU limits updated successfully."
        })

    except client.exceptions.ApiException as e:
        response_steps.append({"step": "update_resources", "response": f"Error for pod '{pod_name}': {str(e)}"})
        return {"statusCode": e.status, "body": json.dumps({"operation_id": operation_id, "timestamp": timestamp, "steps": response_steps})}

    return {"statusCode": 200, "body": json.dumps({"operation_id": operation_id, "timestamp": timestamp, "steps": response_steps})}
