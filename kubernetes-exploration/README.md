# Kubernetes exploration

First of all, [how can one has access to a `Kubernetes` cluster?](#how-can-i-have-access-to-a-kubernetes-cluster)

## Part 1: vanilla deployment

Below some content to play with the following `Kubernetes` objects:

* `Deployment` ([docs](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#creating-a-deployment)),
* `ConfigMap` ([docs](https://kubernetes.io/docs/concepts/configuration/configmap/#configmap-object)),
* `Job` ([docs](https://kubernetes.io/docs/concepts/workloads/controllers/jobs-run-to-completion/#writing-a-job-spec)) & `CronJob` ([docs](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/#cronjob); might also want to check the quick [cheat sheet](https://www.codementor.io/@akul08/the-ultimate-crontab-cheatsheet-5op0f7o4r) and [generator](https://crontab.guru/) for `cron` syntax as a reminder),
* `Service` ([docs](https://kubernetes.io/docs/concepts/services-networking/service/#defining-a-service)),
* `Ingress` ([docs](https://kubernetes.io/docs/concepts/services-networking/ingress/#the-ingress-resource)),
* `StatefulSet` ([docs](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/#components)),
* `PersistentVolumeClaim` ([docs](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#persistentvolumeclaims)).

`kubectl` ([cheat sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)) will be used as the main utility throughout the exercise.

> _Remember to **add the `microk8s.` prefix** to your commands if using that implementation._

### `docker-compose`

To get the hang of the whole "infrastructure" deployed, a `docker-compose.yaml` is also provided:

```bash
$ docker-compose up --build
```

and a few:

```bash
$ docker-compose start push
$ docker-compose start push
$ docker-compose start push
```

to publish some messages. Visit the [http://localhost:5000/](http://localhost:5000/) page if the if the API is running (Exercise 2). Below what happened in a few words:

1. The `push` service **pub**lishes a [message]([https://www.lipsum.com/](https://www.lipsum.com/)) on the broker (`Redis`), on the `lispum` channel; the broker is here coined `pass` (because _passing_ messages).
2. The `pull` service is **sub**scribed to the said channel, and fetches -_e.g._, _pulls_- the messages every so often (defined through the `INTERVAL` environment variable).
3. If requested so (_via_ the `HOARD` environment variable) the `pull` service will store -_pile_ on- the record in a database (`PostgreSQL`).
4. The `show` frontend service request the backend API running on the `pull` service to _pick_ at the store and retrieve [specific] messages.

```text
                             +------+      +------+
 +------+      +------+      | pull |----> |      |
 | push |----> | pass |----> +------+      | pile |
 +------+      +------+      | pick | <----|      |
                             +------+      +------+
                                  \
                                   \
                                 +------+
                                 | show |
                                 +------+
```

> _It is not up to me to decide if you should want to transform this into a simple chatting app with distributed storage._

### `Kubernetes`

#### Exercise 1: _Stream_

1. Run a `pass` service (broker). (Think about what objects need to be defined...)
2. Create a `ConfigMap`, making sure we are not trying to write to any database yet to be deployed (`HOARD` environment variable).
3. Run a `push` service as a `Job` (check the `docker-compose.yaml` for the entrypoint command; see [this page](https://kubernetes.io/docs/concepts/workloads/controllers/jobs-run-to-completion/#writing-a-job-spec) for docs).
4. Run a `push` service as a `CronJob`; see [that page](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/#cronjob) for more information.
5. Run a `pull` service.

#### Exercise 2: _Stream & Log_

1. Run a `pile` (`PostgreSQL`) service to log the messages.
2. Modify the `ConfigMap` to start storing in the dedicated service (`HOARD` and `POSTGRES_*` environment variables); on the way, secure the broker?
3. Update the existing `pass`, `push` and `pull` services according to the new `ConfigMap`; the `pick` service (part of the `pull` container; are you even listening?) should be accessible from the [http://localhost/pick/](http://localhost/pick) endpoint (port 80).
4. Scale up the `pull` service (here you have two options: either you rewrite a `YAML` or you use the `kubectl scale deployment trainingk8s-pull --replicas=<...>` command), and check the modified `Deployment`/`ReplicaSet`.
5. Run the `show` service to query the stored messages _via_ the API (running in the `pull` container); this service should be accessible from the [http://localhost/](http://localhost/) endpoint (port 80).

#### Exercise 3: _Stream & Store_ (for posterity)

1. Create a `PersistentVolumeClaim`; the `StorageClass` to be used is described in the FAQ below (as a solution for `microk8s`; for other implementations, see their respective documentation sections).
2. Grant the `pile` service that persistent storage (keep it mind this service will use a persistent storage, and therefore a `Deployment` might not be the correct solution anymore).
3. Update the service(s).

## Part 2: `Helm` deployment

In this second hands-on part, we will use [`Helm`](https://helm.sh/) to package and deploy the set of microservices described before. `Helm` offers a rich API to interact with stacks deployed on `Kubernetes` ([docs](https://helm.sh/docs/helm/)); together with a simple but powerful templating logic ([docs](https://helm.sh/docs/chart_template_guide/)).

#### Exercise 4: _Exploration_ (hybrid deployment)

1. Using the API of `Helm` (run the `microk8s.helm3` command for help and usage), find and deploy a `Redis` instance (`pass` service). (_Bitnami_ is a trusted source.)
2. Expose the deployed chart.
3. Deploy the rest of the services we used in the previous exercises.

#### Exercise 5: _Stream_ [_Stream & Log_ [_Stream & Store_]]

1. Create a chart for a given version of the previous stack.
2. Tweak the chart for piece that are redundant (naming, label, _etc._) using the `Helm` moustache notation ([docs](https://helm.sh/docs/chart_template_guide/)).
3. Roll in, roll out. Profit.

#### Exercise 6: _Bring your own_

You have a set of microservices you need to/could deploy as a single stack, `docker-compose`-style? You should now be able to do it using `Helm`. Let's have at it.

# FAQ

* [How can I have access to a `Kubernetes` cluster?](#how-can-i-have-access-to-a-kubernetes-cluster)
* [Add local images to `microk8s` registry](#add-local-images-to-microk8s-registry)
* [Check/remove defined objects](#checkremove-defined-objects)
* [Quickly create a `ConfigMap` from a `key=value` file](#quickly-create-a-configmap-from-a-keyvalue-file)
* [Stream logs from a `Pod` as they come](#stream-logs-from-a-pod-as-they-come)
* [Make storage available to your `Kubernetes` cluster](#make-storage-available-to-your-kubernetes-cluster)
* [It is 2020, can't we have a dashboard for this?](#it-is-2020-cant-we-have-a-dashboard-for-this)
* [`Helm`?](#helm)
* [Add a `Helm` repo](#add-a-helm-repo)
* [I need the `metrics-server` service to allow autoscaling!](#i-need-the-metrics-server-service-to-allow-autoscaling)
* [Got any more of them hints?](#got-any-more-of-them-hints)

## How can I have access to a `Kubernetes` cluster?

My personal favourite is [`microk8s`](https://microk8s.io/), single-node `Kubernetes` cluster. It is pretty light (about 10% of the real deal), and provide with its own `microk8s.kubectl` to avoid confusing it with the regular utility. It does not use any virtualization. The complete `Kubernetes` API is available, together with some interesting [addons](https://microk8s.io/docs/addons). A simple quickstart with random example can be found [there](https://logz.io/blog/getting-started-with-kubernetes-using-microk8s/).

```bash
$ snap install microk8s --classic
$ microk8s.start
$ microk8s.enable dns ingress registry
$ # [...] play with it
$ microk8s.stop
```

The enabled addons are persistent upon restart of `microk8s`.

> _**Fair warning: documentation is severely lacking.** But the Kubernetes one should suffice. And figuring things out is half the fun. And `minikube` documentation is not much better._

> _**Important warning: `microk8s` is local development only!** Nothing ready for production, regardless of what they are claiming. Related story [here](https://medium.com/faun/an-overview-of-microk8s-and-why-using-it-in-the-cloud-was-a-terrible-idea-9ba8506dc467) (from more than a year ago, they surely patched things up in between)._

Other solutions include:

* [`kubeadm` + `kubelet` + `kubectl`](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/install-kubeadm/), the classic [manual] installation of Kubernetes (check [this](https://linuxacademy.com/blog/containers/building-a-three-node-kubernetes-cluster-quick-guide/) out, could be fun).
* [`minikube`](https://minikube.sigs.k8s.io/), relies on virtualization to deploy a kubernetes cluster in a Linux VM (works under all OS).
* [`kind`](https://kind.sigs.k8s.io/) _aka_ Kubernetes-in-Docker, official tool used by Kubernetes maintainers; I personally find the concept, and its use a bit [convoluted](https://www.imdb.com/title/tt1375666/).
* [`k3s`](https://k3s.io/), altered (!) [lightweight] Kubernetes distribution; interesting once confident with the regular thing.

And of course, [your](https://cloud.google.com/kubernetes-engine) [favourite](https://aws.amazon.com/eks/) [Cloud](https://azure.microsoft.com/en-us/services/kubernetes-service/) [provider](https://www.digitalocean.com/products/kubernetes/). Requiring pushing to the right registries, and using the right packages.

Keep in mind that if you are using [`Docker Desktop`](https://www.docker.com/products/docker-desktop) (Windows or OSX), `Kubernetes` can be switched on with a click (dig in the settings and check the right box). Not sure however how it behaves with registry, volume and similar... please have a look at their respective documentations.

## Add local images to `microk8s` registry

**Update 2021:** `microk8s` now allows to push images directly to a its own [built-in registry](https://microk8s.io/docs/registry-built-in). Kepp on tagging and pushing:

```bash
$ docker build --tag localhost:32000/whatever:registry
$ docker push localhost:32000/whatever
```

and your images should be available within the `microk8s` registry. But the old way also remains:

```bash
$ docker[-compose] build ...
$ docker save trainingk8s-<...>:latest > trainingk8s-<...>.tar
$ microk8s.ctr image import trainingk8s-<...>.tar
$ microk8s.ctr images list
```

If using `minikube`, check [this page](https://minikube.sigs.k8s.io/docs/handbook/registry/). Using `Docker Desktop` for Windows or OSX, see [these](https://docs.docker.com/docker-for-windows/kubernetes/#use-the-kubectl-command) [pages](https://docs.docker.com/docker-for-mac/kubernetes/#use-the-kubectl-command) respectively, and probably [this one](https://docs.docker.com/get-started/kube-deploy/) also.

## Check/remove defined objects

```bash
$ kubectl get pods
$ kubectl get configmaps
$ kubectl get deployments
$ kubectl get cronjobs
$ kubectl get all
$ # [...] you get the gist of it
```

`Kubernetes` will _always_ try to maintain the desired state, regardless of, say, a crashing container for instance. Objects, which respective `spec` define that desired state, need to be deleted from the store.

```bash
$ kubectl delete cronjob trainingk8s-push
$ kubectl delete deployment trainingk8s-pass
$ # [...] you get the gist of it
```

## Quickly create a `ConfigMap` from a `key=value` file

```bash
$ kubectl create configmap trainingk8s-conf<...> --from-env-file=envvars
$ kubectl get configmaps
$ kubectl get configmap trainingk8s-conf<...> -o yaml
```

Now, how to use the variables defined in the `ConfigMap` into the `Job`, `Deployment` or other objects? Find your answer in this [section](https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/#define-container-environment-variables-using-configmap-data).

To check if the environment variables were added to the `Pod` (execute something within the running container):

```bash
$ kubectl exec trainingk8s-pull-<...> -it -- /bin/sh
$ export -p
Ctrl-D
```

## Stream logs from a `Pod` as they come

```bash
$ kubectl logs -f trainingk8s-pull-<...>
```

## Make storage available to your `Kubernetes` cluster

Storage volumes can be anything within `Kubernetes`, from blob/S3 in the Cloud to local storage. To describe the storage itself, a `StorageClass` object needs to be defined.

> _Below solution expects you to use `microk8s`. Same solution for `minikube` is slightly more complicated as it uses a VM; but they thought about it and already provided some directories to persist some_ within the VM _as described in their [docs](https://minikube.sigs.k8s.io/docs/handbook/persistent_volumes/). In my humble opinion, the following solution is closer to a real life use-case._

A default `StorageClass` (allowing folders from the host machine, same fashion as a `Docker` volume) is enabled by default when running:

```bash
$ microk8s.enable storage
$ kubectl get all -n kube-system | grep --color=always -e '^' -e 'hostpath-provisioner'
```

If it is not (if the second command did not highlight any `hostpath-provisioner`), have a go with:

```yaml
# storageclass.yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: microk8s-hostpath
  annotations:
    storageclass.kubernetes.io/is-default-class: "true"
provisioner: microk8s.io/hostpath
```

and

```bash
$ kubectl apply -f storageclass.yaml 
```

Remember that `Kubernetes` also orchestrate the storage; you cannot simply access the volume and its content as you would do with vanilla `Docker` containers.

## It is 2020, can't we have a dashboard for this?

Here you go:

```bash
$ microk8s.enable dashboard
```

The token to login, together with the IP of the service to connect to are given by the following commands:

```bash
$ kubectl -n kube-system describe secret $(kubectl -n kube-system get secret | grep default-token | cut -d " " -f1) | tail -1 | awk '{print$2}' # token
$ kubectl get service/kubernetes-dashboard -n kube-system # ip
```

See you on [https://<...>/#/login](https://<...>/#/login); select "Token" as the authentication method and copy-paste in.

> _The dashboard has a dark theme. Just sayin'._

## `Helm`?

_Ja hoor, geen probleem._ If using `microk8s`, just enable the service using:

```bash
$ microk8s.enable helm3
```

And the `helm3` command will be available through the `microk8s.` prefix, as shown above. Note two `Helm` versions are available within `microk8s`; read all about the differences [here](https://helm.sh/docs/faq/). The recommended version is **`v3`**, without the `Tiller` server.

To generate and install a chart template, use the regular:

```bash
$ helm3 create mychart
$ tree
$ helm3 install --dry-run --debug ./mychart
$ helm3 package ./mychart
$ ls
```

## Add a `Helm` repo

`Helm` is far from perfect. `helm3 search hub redis` works fine, but `helm3 install <...> stable/redis` grumbles the first round. This is due to the fact `Helm` is shipped without repository; just the URL of the REST API to hit when searching for charts. [People are complaining and the `Helm` team is currently working on it](https://github.com/helm/helm/issues/7419).

For now, you can figure out which source repo to add using the trick suggested in [this comment](https://github.com/helm/helm/issues/7419#issuecomment-609844530):

```bash
$ curl https://hub.helm.sh/api/chartsvc/v1/charts/search?q=redis | json_pp | grep --color=always -e '^' -e 'bitnami'
```

Scroll up and you should be able to fish out the URL of the [Bitnami](https://bitnami.com/) [trusted] `Helm` charts repository to add to `Helm`:

```bash
$ helm3 repo add bitnami https://charts.bitnami.com/bitnami
$ helm3 search repo redis
```

You should now be able to install the `Redis` chart ([docs](https://github.com/bitnami/charts/tree/master/bitnami/redis)):

```bash
$ helm3 install <...> --set usePassword=false --set cluster.slaveCount=1 bitnami/redis
```

## I need the `metrics-server` service to allow autoscaling!

This monitoring tool needs to be deployed on the cluster to provide metrics _via_ a dedicated API. (Those quantities are not stored within `etcd` as it would overload this latter.)

If using `microk8s` you could have guessed there is an addon for it... simply `microk8s.enable` your way through. If using `Docker Desktop` you could follow the step-by-step solution presented in this [comment](https://github.com/docker/for-mac/issues/2751#issuecomment-441833752) or its summarised, copy/paste-ready [version](https://blog.codewithdan.com/enabling-metrics-server-for-kubernetes-on-docker-desktop/). You could also install it from scratch as described on the [official repo](https://github.com/kubernetes-sigs/metrics-server).

```bash
$ microk8s.enable metrics-server
```

But shouldn't we also check the [Helm Hub](https://hub.helm.sh/charts/stable/metrics-server) for a readied chart?

## Got any more of them hints?

Pulling from a local registry (`microk8s` but also `Docker Desktop` for instance):

```yaml
# [...]
      - name: mycontainer
        image: myimage:version
        imagePullPolicy: Never
# [...]
```

**The last line is [obviously] important.** Also, do not get stuck on the how to access the `ConfigMap` object (note you could do something similar with a `Secret`):

```yaml
# [...]
        envFrom:
        - configMapRef:
            name: myconfigmap
# [...]
```

or run an entrypoint command:

```yaml
# [...]
        command:
        - "python"
        - "script.py"
# [...]
```
