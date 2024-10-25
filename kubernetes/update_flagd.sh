# run from root of the project
# updates the flagd deployment and creates a new pod
# ./kubernetes/update_flagd.sh


export $(grep -v '^#' .env | xargs)
envsubst < ./kubernetes/opentelemetry-flags.yaml  |  kubectl apply -n otel-demo -f  - 
alias podname="kubectl --namespace otel-demo get pods -o custom-columns=:metadata.name | grep `$1`"
kubectl -n otel-demo delete pod `podname flagd`