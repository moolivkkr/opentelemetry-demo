import json
import uuid
import time
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

    # Extract parameters
    namespace = event.get("namespace", "default")
    pod_name = event.get("pod_name")
    replica_count = event.get("replica_count", 1)  # Default to 1 if not specified
    response_steps = []

    # Step 1: Attempt to identify the pod and its ReplicaSet
    try:
        step_detail = {"step": "identify_resources", "request_id": request_id}
        step_detail["request"] = f"Retrieve pod '{pod_name}' in namespace '{namespace}' to identify associated ReplicaSet."
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

        # Step 2: Scale Up the Deployment by replica_count
        step_detail = {"step": "scale_up", "request_id": request_id}
        step_detail["request"] = f"Increasing replicas for deployment '{deployment_name}' in namespace '{namespace}' by {replica_count}."
        deployment = v1_apps.read_namespaced_deployment(name=deployment_name, namespace=namespace)
        current_replicas = deployment.spec.replicas
        new_replicas = current_replicas + replica_count  # Scale up by specified replica_count
        deployment.spec.replicas = new_replicas
        v1_apps.patch_namespaced_deployment(name=deployment_name, namespace=namespace, body=deployment)
        step_detail["response"] = f"Scaled up deployment '{deployment_name}' to {new_replicas} replicas."
        response_steps.append(step_detail)

        # Wait for the new pod to become healthy
        new_pod_names = wait_for_new_pods(namespace, deployment_name, replica_count, v1_core)

        # Step 3: Delete old pods one at a time until all are restarted
        pods_to_recycle = v1_core.list_namespaced_pod(namespace=namespace, label_selector=f"app={pod.metadata.labels['app']}").items
        recycled_pod_names = []

        for pod in pods_to_recycle:
            if pod.metadata.name not in new_pod_names:  # Skip the new pods
                v1_core.delete_namespaced_pod(name=pod.metadata.name, namespace=namespace)
                recycled_pod_names.append(pod.metadata.name)
                response_steps.append({
                    "step": "delete_pod",
                    "request_id": request_id,
                    "request": f"Delete pod '{pod.metadata.name}' in namespace '{namespace}'.",
                    "response": f"Pod '{pod.metadata.name}' deleted successfully."
                })

                # Wait for the deleted pod to be healthy
                wait_for_health(namespace, pod.metadata.name, v1_core)

        # Step 4: Scale Down the Deployment to the original replica count
        step_detail = {"step": "scale_down", "request_id": request_id}
        step_detail["request"] = f"Decreasing replicas for deployment '{deployment_name}' in namespace '{namespace}' to {current_replicas}."
        deployment.spec.replicas = current_replicas  # Scale back down
        v1_apps.patch_namespaced_deployment(name=deployment_name, namespace=namespace, body=deployment)
        step_detail["response"] = f"Scaled down deployment '{deployment_name}' to {current_replicas} replicas."
        response_steps.append(step_detail)

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
            "recycled_pods": recycled_pod_names,
            "new_pods": new_pod_names,
            "response": f"Recycled pods: {recycled_pod_names}, New pods created: {new_pod_names}"
        })

    except client.exceptions.ApiException as e:
        response_steps.append({"step": "identify_resources", "response": f"Error processing pod '{pod_name}': {str(e)}", "request_id": request_id})
        return {"statusCode": e.status, "body": json.dumps({"operation_id": operation_id, "request_id": request_id, "timestamp": timestamp, "steps": response_steps})}

    return {"statusCode": 200, "body": json.dumps({"operation_id": operation_id, "request_id": request_id, "timestamp": timestamp, "steps": response_steps})}

def wait_for_new_pods(namespace, deployment_name, count, v1_core, timeout=300, interval=5):
    start_time = time.time()
    new_pods = []
    while len(new_pods) < count:
        pods = v1_core.list_namespaced_pod(namespace=namespace, label_selector=f"app={deployment_name}").items
        for pod in pods:
            if pod.status.phase == "Running" and all(container.ready for container in pod.status.container_statuses):
                new_pods.append(pod.metadata.name)
        if time.time() - start_time > timeout:
            raise Exception(f"Timeout waiting for new pods in deployment '{deployment_name}' to become healthy.")
        time.sleep(interval)
    return new_pods

def wait_for_health(namespace, pod_name, v1_core, timeout=300, interval=5):
    start_time = time.time()
    while True:
        pod = v1_core.read_namespaced_pod(name=pod_name, namespace=namespace)
        if pod.status.phase == "Running" and all(container.ready for container in pod.status.container_statuses):
            break
        if time.time() - start_time > timeout:
            raise Exception(f"Timeout waiting for pod '{pod_name}' to become healthy.")
        time.sleep(interval)
