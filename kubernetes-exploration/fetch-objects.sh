microk8s.kubectl get all
echo
microk8s.kubectl get configmap | sed 's:^:configmap/:g;s:configmap/NAME:NAME          :g'
echo
microk8s.kubectl get ingress | sed 's:^:ingress.extensions/:g;s:ingress.extensions/NAME:NAME                   :g'
echo
microk8s.kubectl get storageclass
