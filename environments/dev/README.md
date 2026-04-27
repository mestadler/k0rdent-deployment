# Development Environment

`config.env` is included with baseline values inferred from repository docs.
Adjust cluster context and any chart references that differ in your environment.

Files:

- `config.env`: shell variables consumed by scripts.
- `config.env.example`: template copy of shell variables.
- `artifact-lock.yaml`: pinned OCI charts and images.
- `values/`: Helm values per component.

Notes:

- `kof` is intentionally not represented in this environment.
- Keep chart versions and digests aligned with `catalog` policy.
