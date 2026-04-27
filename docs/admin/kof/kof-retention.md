# KOF Retention and Replication

KOF stores metrics in **VictoriaMetrics** and logs in **VictoriaLogs**. Configure retention and replication to balance cost, durability, and compliance.

For example, consider these recommendations:

* **Management cluster:** short-term retention (1–30 days)
* **Regional clusters:** long-term retention (30–365 days)
* Increase **replicationFactor** where higher availability is required; this field enables you to determine how many copies are stored, usually on different nodes.

Configure VictoriaMetrics and VictoriaLogs by adjusting the `charts/kof-storage/values.yaml` file
to include the following parameters:

```yaml
victoriametrics:
  vmcluster:
    spec:
      retentionPeriod: "30d"
      replicationFactor: 2
      vmstorage:
        storage:
          volumeClaimTemplate:
            spec:
              resources:
                requests:
                  storage: 100Gi

victoria-logs-cluster:
  vlstorage:
    extraArgs:
      retentionPeriod: "30d"
    persistentVolume:
      size: "100Gi"
```