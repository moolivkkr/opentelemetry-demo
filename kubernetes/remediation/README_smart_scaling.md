# Smart Scaling Lambda Function

## Purpose
This function dynamically scales a Kubernetes deployment up or down based on either a percentage or a fixed number, identified by pod name and namespace only.

## Input Parameters
- **operation_id** (string, optional): Unique operation ID to track the operation; a new ID will be generated if not provided.
- **namespace** (string, required): Kubernetes namespace where the pod resides.
- **pod_name** (string, required): The name of the pod within the deployment to scale.
- **scale_type** (string, optional): Type of scaling, either "increase" or "decrease" (default is "increase").
- **scale_by** (integer, optional): Percentage or fixed number to scale by (default is 25).
- **is_percentage** (boolean, optional): If true,  is treated as a percentage; if false,  is treated as a fixed number (default is true).

## Example Requests

1. **Increase replicas by 25% with a specified operation ID**:
   ```json
   {
     "operation_id": "d53b5c5d-8473-4a9b-8f0e-e28a9b35d3a7",
     "namespace": "default",
     "pod_name": "my-app-pod-12345",
     "scale_type": "increase",
     "scale_by": 25,
     "is_percentage": true
   }
   ```

2. **Decrease replicas by 2**:
   ```json
   {
     "namespace": "default",
     "pod_name": "my-app-pod-12345",
     "scale_type": "decrease",
     "scale_by": 2,
     "is_percentage": false
   }
   ```

## Sample Success Response
### Success
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
        "request": "Retrieve pod 'my-app-pod-12345' in namespace 'default'.",
        "response": "Found Deployment 'my-app-deployment' for pod 'my-app-pod-12345'."
      },
      {
        "step": "retrieve_replicas",
        "request_id": "a1234b5c-d567-8ef0-9gh1-i2345jklm678",
        "request": "Retrieve current replicas for deployment 'my-app-deployment'.",
        "response": "Current replicas for 'my-app-deployment': 4."
      },
      {
        "step": "calculate_replicas",
        "request_id": "a1234b5c-d567-8ef0-9gh1-i2345jklm678",
        "request": "Scale increase by 25% for 'my-app-deployment'.",
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
        "deployment": "my-app-deployment",
        "scaled_to": 5,
        "response": "Smart scaling applied to 'my-app-deployment': scaled increase to 5 replicas."
      }
    ]
  }
}
```
