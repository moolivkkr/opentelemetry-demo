# Scale Up Percentage Lambda Function

## Purpose
This function scales a Kubernetes deployment up by a specified percentage based on the pod name and namespace.

## Input Parameters
- **operation_id** (string, optional): Unique operation ID to track the operation; a new ID will be generated if not provided.
- **namespace** (string, required): Kubernetes namespace where the pod resides.
- **pod_name** (string, required): The name of the pod to scale up.
- **scale_percentage** (integer, optional): Percentage to scale up by (default is 25).

## Example Requests

1. **Scale up replicas by 25% with a specified operation ID**:
   ```json
   {
     "operation_id": "d53b5c5d-8473-4a9b-8f0e-e28a9b35d3a7",
     "namespace": "default",
     "pod_name": "my-app-pod-12345",
     "scale_percentage": 25
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
        "request": "Retrieve pod 'my-app-pod-12345' in namespace 'default' to identify associated ReplicaSet and Deployment.",
        "response": "Found Deployment 'my-app-deployment' for pod 'my-app-pod-12345'."
      },
      {
        "step": "retrieve_replicas",
        "request_id": "a1234b5c-d567-8ef0-9gh1-i2345jklm678",
        "request": "Retrieve current replicas for deployment 'my-app-deployment' in namespace 'default'.",
        "response": "Current replicas for 'my-app-deployment': 4."
      },
      {
        "step": "calculate_replicas",
        "request_id": "a1234b5c-d567-8ef0-9gh1-i2345jklm678",
        "request": "Scale up by 25% for 'my-app-deployment'.",
        "response": "Calculated new replica count: 5."
      },
      {
        "step": "apply_replicas",
        "request_id": "a1234b5c-d567-8ef0-9gh1-i2345jklm678",
        "request": "Set replicas of 'my-app-deployment' to 5.",
        "response": "Successfully scaled deployment 'my-app-deployment' to 5 replicas."
      },
      {
        "step": "summary",
        "operation_id": "d53b5c5d-8473-4a9b-8f0e-e28a9b35d3a7",
        "request_id": "a1234b5c-d567-8ef0-9gh1-i2345jklm678",
        "start_time": "2023-01-02T14:30:00Z",
        "end_time": "2023-01-02T14:30:01Z",
        "duration_seconds": 1,
        "deployment": "my-app-deployment",
        "scaled_to": 5,
        "scale_percentage": 25,
        "response": "Scaled up 'my-app-deployment' by 25%. New replicas: 5."
      }
    ]
  }
}
```

## Sample Failure Response
If the requested deployment cannot be scaled, the response will indicate an error.

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
        "request": "Retrieve pod 'non-existent-pod' in namespace 'default' to identify associated ReplicaSet and Deployment.",
        "response": "Error: ReplicaSet not found for pod 'non-existent-pod'."
      }
    ]
  }
}
```
