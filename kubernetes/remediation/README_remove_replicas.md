# Remove Replicas Lambda Function

## Purpose
This function removes a specified number of replicas from a Kubernetes deployment, ensuring at least one replica remains.

## Input Parameters
- **operation_id** (string, optional): Unique operation ID to track the operation; a new ID will be generated if not provided.
- **namespace** (string, required): Kubernetes namespace where the pod resides.
- **pod_name** (string, required): The name of the pod.
- **remove_replicas** (integer, optional): Number of replicas to remove (default is 1).

## Example Requests

1. **Remove 2 replicas with a specified operation ID**:
   ```json
   {
     "operation_id": "d53b5c5d-8473-4a9b-8f0e-e28a9b35d3a7",
     "namespace": "default",
     "pod_name": "my-app-pod-12345",
     "remove_replicas": 2
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
        "request": "Retrieve pod 'my-app-pod-12345' in namespace 'default' with operation ID 'd53b5c5d-8473-4a9b-8f0e-e28a9b35d3a7'.",
        "response": "Found ReplicaSet 'my-app-replicaset' for pod 'my-app-pod-12345'."
      },
      {
        "step": "calculate_replicas",
        "request_id": "a1234b5c-d567-8ef0-9gh1-i2345jklm678",
        "request": "Decrease replicas of 'my-app-replicaset' by 2 for pod 'my-app-pod-12345' with operation ID 'd53b5c5d-8473-4a9b-8f0e-e28a9b35d3a7'.",
        "response": "Scaled to 2 replicas from 4 for pod 'my-app-pod-12345'."
      },
      {
        "step": "summary",
        "operation_id": "d53b5c5d-8473-4a9b-8f0e-e28a9b35d3a7",
        "request_id": "a1234b5c-d567-8ef0-9gh1-i2345jklm678",
        "start_time": "2023-01-02T14:30:00Z",
        "end_time": "2023-01-02T14:30:01Z",
        "duration_seconds": 1,
        "replica_set": "my-app-replicaset",
        "deployment": "my-app-deployment",
        "added_pods": [],
        "removed_pods": ["my-app-pod-67890", "my-app-pod-67891"],
        "untouched_pods": ["my-app-pod-12345", "my-app-pod-12346"],
        "response": "0 pods added, 2 pods removed, 2 pods untouched."
      }
    ]
  }
}
```

## Sample Failure Response
If the requested pod or ReplicaSet is not found, the response will indicate an error.

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
        "request": "Retrieve pod 'non-existent-pod' in namespace 'default' with operation ID 'd53b5c5d-8473-4a9b-8f0e-e28a9b35d3a7'.",
        "response": "Error: ReplicaSet not found for pod 'non-existent-pod'."
      }
    ]
  }
}
```
