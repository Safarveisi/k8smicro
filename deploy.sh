# op can be apply or delete
op=$1

kubectl --kubeconfig kubeconfig.yaml $op -f deploy_postgres.yaml
envsubst < deploy_app.yaml | kubectl --kubeconfig kubeconfig.yaml $op -f -