op=$1

# Apply or delete 
envsubst < kube-deploy.yaml | kubectl --kubeconfig kubeconfig.yaml $op -f -