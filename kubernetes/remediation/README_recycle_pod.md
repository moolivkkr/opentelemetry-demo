# Recycle Pod Lambda Function

## Purpose
This function recycles a specific pod by deleting it, allowing Kubernetes to replace it with a new instance based on the deployment configuration.

## Input Parameters
- **operation_id** (string, optional): Unique operation ID to track the operation; a new ID will be generated if not provided.
- **namespace** (string, required): Kubernetes namespace where the pod resides.
- **pod_name** (string, required): The name of the pod to recycle.

## Example Requests

1. **Recycle a pod with a specified operation ID**:
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
        "step": "delete_pod",
        "request_id": "a1234b5c-d567-8ef0-9gh1-i2345jklm678",
        "request": "Delete pod 'my-app-pod-12345' in namespace 'default' with operation ID 'd53b5c5d-8473-4a9b-8f0e-e28a9b35d3a7'.",
        "response": "Pod 'my-app-pod-12345' deleted successfully."
      },
      {
        "step": "summary",
        "operation_id": "d53b5c5d-8473-4a9b-8f0e-e28a9b35d3a7",
        "request_id": "a1234b5c-d567-8ef0-9gh1-i2345jklm678",
        "start_time": "2023-01-02T14:30:00Z",
        "end_time": "2023-01-02T14:30:10Z",
        "duration_seconds": 10,
        "replaced_pod": "my-app-pod-12345",
        "replacement_pods": ["my-app-pod-67890"],
        "response": "Pod 'my-app-pod-12345' recycled. Replacement pod(s): ['my-app-pod-67890']"
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
        "step": "delete_pod",
        "request_id": "e9876fgh-1234-ijkl-5678-mnopqrstuvwx",
        "request": "Delete pod 'non-existent-pod' in namespace 'default' with operation ID 'd53b5c5d-8473-4a9b-8f0e-e28a9b35d3a7'.",
        "response": "Error: Pod 'non-existent-pod' not found."
      }
    ]
  }
}
```
