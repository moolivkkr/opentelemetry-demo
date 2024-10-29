# Increase Resource Limits/Requests Lambda Function

## Purpose
This function adjusts the CPU resource limits and requests of a Kubernetes deployment based on a specified percentage.

## Input Parameters
- **namespace** (string, required): Kubernetes namespace where the pod resides.
- **pod_name** (string, required): The name of the pod.
- **increase_by** (integer, optional): The percentage to increase CPU limits by (default is 25%).

## Example Requests

1. **Increase CPU limits by 50%**:
   ```json
   {
     "namespace": "default",
     "pod_name": "my-app-pod-12345",
     "increase_by": 50
   }
   ```

## Sample Success Response

```json
{
  "statusCode": 200,
  "body": {
    "operation_id": "d53b5c5d-8473-4a9b-8f0e-e28a9b35d3a7",
    "timestamp": "2023-01-01T12:00:00Z",
    "steps": [
      {
        "step": "identify_resources",
        "request": "Retrieve pod 'my-app-pod-12345' in namespace 'default'.",
        "response": "Found ReplicaSet 'my-app-replicaset' for pod 'my-app-pod-12345'."
      },
      {
        "step": "update_resources",
        "request": "Increase CPU limits of 'my-app-replicaset' by 50% for pod 'my-app-pod-12345'.",
        "response": "CPU limits increased to 750m from 500m."
      },
      {
        "step": "summary",
        "operation_id": "d53b5c5d-8473-4a9b-8f0e-e28a9b35d3a7",
        "start_time": "2023-01-01T12:00:00Z",
        "end_time": "2023-01-01T12:00:02Z",
        "duration_seconds": 2,
        "replica_set": "my-app-replicaset",
        "deployment": "my-app-deployment",
        "added_pods": [],
        "removed_pods": [],
        "untouched_pods": ["my-app-pod-12345"],
        "response": "CPU limits updated successfully."
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
    "operation_id": "e9876fgh-1234-ijkl-5678-mnopqrstuvwx",
    "timestamp": "2023-01-03T16:00:00Z",
    "steps": [
      {
        "step": "identify_resources",
        "request": "Retrieve pod 'non-existent-pod' in namespace 'default'.",
        "response": "Error: ReplicaSet not found for pod 'non-existent-pod'."
      }
    ]
  }
}
```
