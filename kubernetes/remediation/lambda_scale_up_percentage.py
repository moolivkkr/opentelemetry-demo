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
    v1_apps = client.AppsV1Api()

    # Extract parameters
    namespace = event.get("namespace", "default")
    pod_name = event.get("pod_name")
    scale_percentage = event.get("scale_percentage", 25)  # Default to 25%
    response_steps = []

    try:
        # Step 1: Identify ReplicaSet and Deployment from the Pod
        step_detail = {"step": "identify_resources", "request_id": request_id}
        step_detail["request"] = f"Retrieve pod '{pod_name}' in namespace '{namespace}' to identify associated ReplicaSet and Deployment."
        pod = v1_core.read_namespaced_pod(name=pod_name, namespace=namespace)
        replica_set_name = next((owner.name for owner in pod.metadata.owner_references if owner.kind == "ReplicaSet"), None)

        if not replica_set_name:
            step_detail["response"] = f"Error: ReplicaSet not found for pod '{pod_name}'."
            response_steps.append(step_detail)
            return {"statusCode": 404, "body": json.dumps({"operation_id": operation_id, "timestamp": timestamp, "steps": response_steps})}

        # Retrieve deployment name from the replica set
        replica_set = v1_apps.read_namespaced_replica_set(name=replica_set_name, namespace=namespace)
        deployment_name = next((owner.name for owner in replica_set.metadata.owner_references if owner.kind == "Deployment"), None)

        if not deployment_name:
            step_detail["response"] = f"Error: Deployment not found for ReplicaSet '{replica_set_name}'."
            response_steps.append(step_detail)
            return {"statusCode": 404, "body": json.dumps({"operation_id": operation_id, "timestamp": timestamp, "steps": response_steps})}

        step_detail["response"] = f"Found Deployment '{deployment_name}' for pod '{pod_name}'."
        response_steps.append(step_detail)

        # Step 2: Retrieve the current number of replicas
        step_detail = {"step": "retrieve_replicas", "request_id": request_id}
        step_detail["request"] = f"Retrieve current replicas for deployment '{deployment_name}' in namespace '{namespace}'."
        deployment = v1_apps.read_namespaced_deployment(name=deployment_name, namespace=namespace)
        current_replicas = deployment.spec.replicas
        step_detail["response"] = f"Current replicas for '{deployment_name}': {current_replicas}."
        response_steps.append(step_detail)

        # Step 3: Calculate the new replica count
        scale_amount = int(current_replicas * (scale_percentage / 100))
        new_replicas = current_replicas + scale_amount  # Increase the replicas
        deployment.spec.replicas = new_replicas

        # Step 4: Apply the new replica count
        v1_apps.patch_namespaced_deployment(name=deployment_name, namespace=namespace, body=deployment)
        response_steps.append({
            "step": "apply_replicas",
            "request_id": request_id,
            "request": f"Set replicas of '{deployment_name}' to {new_replicas}.",
            "response": f"Successfully scaled deployment '{deployment_name}' to {new_replicas} replicas."
        })

        # Calculate end time and duration
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        # Step 5: Summary
        response_steps.append({
            "step": "summary",
            "operation_id": operation_id,
            "request_id": request_id,
            "timestamp": timestamp,
            "start_time": start_time.isoformat() + "Z",
            "end_time": end_time.isoformat() + "Z",
            "duration_seconds": duration,
            "deployment": deployment_name,
            "scaled_to": new_replicas,
            "scale_percentage": scale_percentage,
            "response": f"Scaled up '{deployment_name}' by {scale_percentage}%. New replicas: {new_replicas}."
        })

    except client.exceptions.ApiException as e:
        response_steps.append({"step": "retrieve_replicas", "response": f"Error scaling deployment '{deployment_name}': {str(e)}", "request_id": request_id})
        return {"statusCode": e.status, "body": json.dumps({"operation_id": operation_id, "request_id": request_id, "timestamp": timestamp, "steps": response_steps})}

    return {"statusCode": 200, "body": json.dumps({"operation_id": operation_id, "request_id": request_id, "timestamp": timestamp, "steps": response_steps})}
