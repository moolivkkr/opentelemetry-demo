Create cluster
    eksctl create cluster -f eks_cluster.yaml  (file available in ./opentelemetry-demo/kubernetes)

connect kubectl 
    aws eks update-kubeconfig --region $AWS_DEFAULT_REGION --name eksoteldemo

validate connectivity
kubectl get ns
kubectl get services

Create namespace
   kubectl create namespace otel-demo --save-config


setup the terminal with all envs --
export $(grep -v '^#' .env | xargs)

-- Install all services
envsubst < ./opentelemetry-demo.yaml  |  kubectl apply -n otel-demo -f - 

-- install kubernetes daemon 
envsubst < ./kubernetes/opentelemetry_k8_daemonset_agent.yaml  |  kubectl apply -n otel-demo -f  -

envsubst < ./kubernetes/opentelemetry_k8_daemonset_agent.yaml  |  kubectl apply -n otel-demo -f  -


