# Drain and Reschedule Lambda Function

## Purpose
This function cordons a specified node to prevent new pods from being scheduled on it, and drains all pods from the node, allowing Kubernetes to reschedule them on other nodes.

## Input Parameters
- **operation_id** (string, optional): Unique operation ID to track the operation; a new ID will be generated if not provided.
- **namespace** (string, required): Kubernetes namespace where the pods reside.
- **node_name** (string, required): The name of the node to drain and reschedule.

## Example Requests

1. **Drain and reschedule pods on a specified node with an operation ID**:
   ```json
   {
     "operation_id": "d53b5c5d-8473-4a9b-8f0e-e28a9b35d3a7",
     "namespace": "default",
     "node_name": "my-node-123"
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
        "step": "cordon_node",
        "request_id": "a1234b5c-d567-8ef0-9gh1-i2345jklm678",
        "request": "Cordon node 'my-node-123' with operation ID 'd53b5c5d-8473-4a9b-8f0e-e28a9b35d3a7'.",
        "response": "Node 'my-node-123' cordoned successfully."
      },
      {
        "step": "evict_pod",
        "request_id": "a1234b5c-d567-8ef0-9gh1-i2345jklm678",
        "request": "Evict pod 'my-app-pod-12345' from node 'my-node-123'.",
        "response": "Pod 'my-app-pod-12345' evicted successfully."
      },
      {
        "step": "evict_pod",
        "request_id": "a1234b5c-d567-8ef0-9gh1-i2345jklm678",
        "request": "Evict pod 'my-app-pod-12346' from node 'my-node-123'.",
        "response": "Pod 'my-app-pod-12346' evicted successfully."
      },
      {
        "step": "summary",
        "operation_id": "d53b5c5d-8473-4a9b-8f0e-e28a9b35d3a7",
        "request_id": "a1234b5c-d567-8ef0-9gh1-i2345jklm678",
        "start_time": "2023-01-02T14:30:00Z",
        "end_time": "2023-01-02T14:30:15Z",
        "duration_seconds": 15,
        "node": "my-node-123",
        "drained_pods": ["my-app-pod-12345", "my-app-pod-12346"],
        "response": "Node 'my-node-123' cordoned and drained. Drained pod(s): ['my-app-pod-12345', 'my-app-pod-12346']"
      }
    ]
  }
}
```

## Sample Failure Response
If the requested node cannot be cordoned or if an error occurs during the drain process, the response will indicate an error.

```json
{
  "statusCode": 404,
  "body": {
    "operation_id": "d53b5c5d-8473-4a9b-8f0e-e28a9b35d3a7",
    "request_id": "e9876fgh-1234-ijkl-5678-mnopqrstuvwx",
    "timestamp": "2023-01-03T16:00:00Z",
    "steps": [
      {
        "step": "cordon_node",
        "request_id": "e9876fgh-1234-ijkl-5678-mnopqrstuvwx",
        "request": "Cordon node 'non-existent-node' with operation ID 'd53b5c5d-8473-4a9b-8f0e-e28a9b35d3a7'.",
        "response": "Error: Node 'non-existent-node' not found."
      }
    ]
  }
}
```
