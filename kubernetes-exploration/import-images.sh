for service in pull push show; do
  docker save trainingk8s-$service > trainingk8s-$service.tar
  microk8s.ctr image import trainingk8s-$service.tar
  rm trainingk8s-$service.tar
done
