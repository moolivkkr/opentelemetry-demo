kubectl apply -f opentelemetry-demo.yaml
kubectl apply -f opensearch-deployment.yaml
kubectl apply -f data-prepper-deployment.yaml

export KUBECONFIG=/Users/kishoremooli/development/opentelemetry-demo/workload-cluster/workload-cluster-eks-a-cluster.kubeconfig
export CLUSTER_NAME=workload-cluster
export AWS_DEFAULT_REGION=us-east-1
alias k="kubectl --namespace otel-demo"
alias kgp="kubectl --namespace otel-demo get pods"
alias kgd="kubectl --namespace otel-demo get deployments"
alias kgs="kubectl --namespace otel-demo get services"
alias kdp="kubectl --namespace otel-demo delete pods --all"
alias kdd="kubectl --namespace otel-demo delete deployments --all"
alias kds="kubectl --namespace otel-demo delete services --all"
alias kl="kubectl --namespace otel-demo logs"
alias podnames="kubectl --namespace otel-demo get pods -o custom-columns=:metadata.name"
alias kdps="kubectl --namespace otel-demo delete pod %1"
export $(grep -v '^#' .env | xargs)

envsubst < opentelemetry-opensearch.yaml | kubectl apply -f -

docker push ghcr.io/moolivkkr/open-telemetry/demo/frontendproxy:latest
docker push ghcr.io/moolivkkr/open-telemetry/demo/loadgenerator:latest
docker push ghcr.io/moolivkkr/open-telemetry/demo/frontend:latest
docker push ghcr.io/moolivkkr/open-telemetry/demo/checkoutservice:latest
docker push ghcr.io/moolivkkr/open-telemetry/demo/frauddetectionservice:latest
docker push ghcr.io/moolivkkr/open-telemetry/demo/adservice:latest
docker push ghcr.io/moolivkkr/open-telemetry/demo/recommendationservice:latest
docker push ghcr.io/moolivkkr/open-telemetry/demo/shippingservice:latest
docker push ghcr.io/moolivkkr/open-telemetry/demo/currencyservice:latest
docker push ghcr.io/moolivkkr/open-telemetry/demo/quoteservice:latest
docker push ghcr.io/moolivkkr/open-telemetry/demo/productcatalogservice:latest
docker push ghcr.io/moolivkkr/open-telemetry/demo/emailservice:latest
docker push ghcr.io/moolivkkr/open-telemetry/demo/cartservice:latest
docker push ghcr.io/moolivkkr/open-telemetry/demo/accountingservice:latest
docker push ghcr.io/moolivkkr/open-telemetry/demo/paymentservice:latest
docker push ghcr.io/moolivkkr/open-telemetry/demo/imageprovider:latest
docker push ghcr.io/moolivkkr/open-telemetry/demo/kafka:latest


docker push  ghcr.io/moolivkkr/open-telemetry/demo/frontendproxy:1.11.3
docker push  ghcr.io/ghcr.io/moolivkkr/open-telemetry/demo/frontendproxy:1.11.3
docker push  ghcr.io/moolivkkr/open-telemetry/demo/loadgenerator:1.11.3
docker push  ghcr.io/ghcr.io/moolivkkr/open-telemetry/demo/loadgenerator:1.11.3
docker push  ghcr.io/moolivkkr/open-telemetry/demo/frontend:1.11.3
docker push  ghcr.io/ghcr.io/moolivkkr/open-telemetry/demo/frontend:1.11.3
docker push  ghcr.io/moolivkkr/open-telemetry/demo/checkoutservice:1.11.3
docker push  ghcr.io/ghcr.io/moolivkkr/open-telemetry/demo/checkoutservice:1.11.3
docker push  ghcr.io/moolivkkr/open-telemetry/demo/frauddetectionservice:1.11.3
docker push  ghcr.io/ghcr.io/moolivkkr/open-telemetry/demo/frauddetectionservice:1.11.3
docker push  ghcr.io/moolivkkr/open-telemetry/demo/adservice:1.11.3
docker push  ghcr.io/ghcr.io/moolivkkr/open-telemetry/demo/adservice:1.11.3
docker push  ghcr.io/moolivkkr/open-telemetry/demo/recommendationservice:1.11.3
docker push  ghcr.io/ghcr.io/moolivkkr/open-telemetry/demo/recommendationservice:1.11.3
docker push  ghcr.io/moolivkkr/open-telemetry/demo/shippingservice:1.11.3
docker push  ghcr.io/ghcr.io/moolivkkr/open-telemetry/demo/shippingservice:1.11.3
docker push  ghcr.io/moolivkkr/open-telemetry/demo/currencyservice:1.11.3
docker push  ghcr.io/ghcr.io/moolivkkr/open-telemetry/demo/currencyservice:1.11.3
docker push  ghcr.io/ghcr.io/moolivkkr/open-telemetry/demo/quoteservice:1.11.3
docker push  ghcr.io/moolivkkr/open-telemetry/demo/quoteservice:1.11.3
docker push  ghcr.io/moolivkkr/open-telemetry/demo/productcatalogservice:1.11.3
docker push  ghcr.io/ghcr.io/moolivkkr/open-telemetry/demo/productcatalogservice:1.11.3
docker push  ghcr.io/moolivkkr/open-telemetry/demo/emailservice:1.11.3
docker push  ghcr.io/ghcr.io/moolivkkr/open-telemetry/demo/emailservice:1.11.3
docker push  ghcr.io/ghcr.io/moolivkkr/open-telemetry/demo/cartservice:1.11.3
docker push  ghcr.io/moolivkkr/open-telemetry/demo/cartservice:1.11.3
docker push  ghcr.io/moolivkkr/open-telemetry/demo/accountingservice:1.11.3
docker push  ghcr.io/ghcr.io/moolivkkr/open-telemetry/demo/accountingservice:1.11.3
docker push  ghcr.io/ghcr.io/moolivkkr/open-telemetry/demo/paymentservice:1.11.3
docker push  ghcr.io/moolivkkr/open-telemetry/demo/paymentservice:1.11.3
docker push  ghcr.io/moolivkkr/open-telemetry/demo/imageprovider:1.11.3
docker push  ghcr.io/ghcr.io/moolivkkr/open-telemetry/demo/imageprovider:1.11.3
docker push  ghcr.io/moolivkkr/open-telemetry/demo/kafka:1.11.3
docker push  ghcr.io/ghcr.io/moolivkkr/open-telemetry/demo/kafka:1.11.3