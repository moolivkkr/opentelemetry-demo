# Recycle Containers Lambda Function

## Purpose
This function temporarily increases the number of replicas for a deployment to add new pods (2x the current replicas), ensuring no performance impact during the recycling process. After the new pods are healthy, it scales down the deployment back to its original number of replicas.

## Input Parameters
- **operation_id** (string, optional): Unique operation ID to track the operation; a new ID will be generated if not provided.
- **namespace** (string, required): Kubernetes namespace where the pods reside.
- **pod_name** (string, required): The name of a pod to identify the ReplicaSet for recycling all associated pods.

## Example Requests

1. **Recycle all pods in the ReplicaSet associated with the specified pod**:
   ```json
   {
     "operation_id": "d53b5c5d-8473-4a9b-8f0e-e28a9b35d3a7",
     "namespace": "default",
     "pod_name": "my-app-pod-12345"
   }
   ```

## Sample Success Response

```json
{
  "statusCode": 200,
  "body": {
    "operation_id": "d53b5c5d-8473-4a9b-8f0e-e28a9b35d3a7",
    "request_id": "a1234b5c-d567-8ef0-9gh1-i2345jklm678",
    "timestamp": "2023-01-02T14:30:00Z",
    "steps": [
      {
        "step": "identify_resources",
        "request_id": "a1234b5c-d567-8ef0-9gh1-i2345jklm678",
        "request": "Retrieve pod 'my-app-pod-12345' in namespace 'default' to identify associated ReplicaSet.",
        "response": "Found ReplicaSet 'my-app-replicaset' for pod 'my-app-pod-12345'."
      },
      {
        "step": "scale_up",
        "request_id": "a1234b5c-d567-8ef0-9gh1-i2345jklm678",
        "request": "Increasing replicas for deployment 'my-app-deployment' in namespace 'default' by doubling the current number of replicas.",
        "response": "Scaled up deployment 'my-app-deployment' to 4 replicas."
      },
      {
        "step": "scale_down",
        "request_id": "a1234b5c-d567-8ef0-9gh1-i2345jklm678",
        "request": "Decreasing replicas for deployment 'my-app-deployment' in namespace 'default' to 2.",
        "response": "Scaled down deployment 'my-app-deployment' to 2 replicas."
      },
      {
        "step": "summary",
        "operation_id": "d53b5c5d-8473-4a9b-8f0e-e28a9b35d3a7",
        "request_id": "a1234b5c-d567-8ef0-9gh1-i2345jklm678",
        "start_time": "2023-01-02T14:30:00Z",
        "end_time": "2023-01-02T14:30:10Z",
        "duration_seconds": 10,
        "new_pods": ["my-app-pod-67891", "my-app-pod-67892"],
        "response": "New pods created: ['my-app-pod-67891', 'my-app-pod-67892']"
      }
    ]
  }
}
```

## Sample Failure Response
If the requested pod cannot be found or deleted, the response will indicate an error.

```json
{
  "statusCode": 404,
  "body": {
    "operation_id": "d53b5c5d-8473-4a9b-8f0e-e28a9b35d3a7",
    "request_id": "e9876fgh-1234-ijkl-5678-mnopqrstuvwx",
    "timestamp": "2023-01-03T16:00:00Z",
    "steps": [
      {
        "step": "identify_resources",
        "request_id": "e9876fgh-1234-ijkl-5678-mnopqrstuvwx",
        "request": "Retrieve pod 'non-existent-pod' in namespace 'default' to identify associated ReplicaSet.",
        "response": "Error: ReplicaSet not found for pod 'non-existent-pod'."
      }
    ]
  }
}
```
