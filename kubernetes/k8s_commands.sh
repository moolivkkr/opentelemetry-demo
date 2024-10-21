kubectl apply -f opentelemetry-demo.yaml
kubectl apply -f opensearch-deployment.yaml
kubectl apply -f data-prepper-deployment.yaml

export KUBECONFIG=/Users/kishoremooli/development/opentelemetry-demo/workload-cluster/workload-cluster-eks-a-cluster.kubeconfig
export CLUSTER_NAME=workload-cluster
export AWS_DEFAULT_REGION=us-east-1
alias k="kubectl --namespace otel-demo"
alias kgp="kubectl --namespace otel-demo get pods"
alias kdp="kubectl --namespace otel-demo delete pods --all"
alias kdd="kubectl --namespace otel-demo delete deployments --all"
alias kds="kubectl --namespace otel-demo delete services --all"
alias kl="kubectl --namespace otel-demo logs"
export $(grep -v '^#' .env | xargs)

envsubst < opentelemetry-opensearch.yaml | kubectl apply -f -