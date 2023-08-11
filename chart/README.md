# LibreTranslate Helm Chart

This Helm chart deploys a LibreTranslate instance on a Kubernetes cluster using the Helm package manager.

## Prerequisites

- Kubernetes 1.12+
- Helm 3.0+

## Installing the Chart

To install the chart with the release name `libretranslate`:

```bash
helm install libretranslate ./chart --namespace libretranslate --create-namespace
```

This command deploys LibreTranslate on the Kubernetes cluster with the default configuration. The [values.yaml](values.yaml) file lists the parameters that can be configured during installation.

> **Tip**: List all releases using `helm list`

## Uninstalling the Chart

To uninstall/delete the `libretranslate` deployment:

```bash
helm delete libretranslate
```

This command removes all the Kubernetes components associated with the chart and deletes the release.

## Configuration

See [values.yaml](values.yaml) for the full list of parameters that can be configured. You can specify each parameter using the `--set key=value[,key=value]` argument to `helm install`. For example,

```bash
helm install libretranslate ./chart --namespace libretranslate --create-namespace --set service.port=8080
```

Alternatively, a YAML file that specifies the values for the parameters can be provided while installing the chart. For example,

```bash
helm install libretranslate ./chart --namespace libretranslate --create-namespace -f values.yaml
```

## Upgrade

Run the following command to upgrade your LibreTranslate installation. This command will use the Helm chart in the ./chart directory, apply the custom values from values.yaml, and deploy the upgrade to the `libretranslate` namespace:

```bash
helm upgrade --install libretranslate ./chart --namespace libretranslate -f values.yaml
```

> **Tip**: You can use the default [values.yaml](values.yaml)

# References
- [https://jmrobles.medium.com/libretranslate-your-own-translation-service-on-kubernetes-b46c3e1af630](https://jmrobles.medium.com/libretranslate-your-own-translation-service-on-kubernetes-b46c3e1af630)
- [https://github.com/LibreTranslate/LibreTranslate](https://github.com/LibreTranslate/LibreTranslate)