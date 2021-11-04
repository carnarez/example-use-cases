microk8s.kubectl delete configmap --all
microk8s.kubectl delete cronjob --all
microk8s.kubectl delete deployment --all
microk8s.kubectl delete horizontalpodautoscaler --all
microk8s.kubectl delete ingress --all
microk8s.kubectl delete job --all
microk8s.kubectl delete statefulset --all

microk8s.kubectl delete service trainingk8s-pass 2>/dev/null
microk8s.kubectl delete service trainingk8s-pick 2>/dev/null
microk8s.kubectl delete service trainingk8s-pile 2>/dev/null
microk8s.kubectl delete service trainingk8s-show 2>/dev/null

microk8s.kubectl delete persistentvolumeclaim --all

microk8s.kubectl delete service trainingk8s-load 2>/dev/null

if [ `microk8s.helm3 list --short 2>/dev/null | wc -l | tail -1` != "0" ]; then
    microk8s.helm3 delete `microk8s.helm3 list --short`
fi
