# Explicit environment targeting; no default endpoint

**Status:** accepted

The collector requires `--api-url` (HTTPS) and `--org` on every run and supplies no default endpoint — a reasonable reader would expect `api.github.com` as default, and that expectation is exactly the hazard: in a governance context, silently collecting from the wrong environment is the worst failure mode, worse than not collecting. Credentials are supplied only via the `GITHUB_TOKEN` environment variable, treated as opaque (no upfront scope validation — effective access is discovered empirically per request), and never persisted, logged, echoed, hashed, or included in evidence. Platform and version identity are captured as evidence (`/meta`, response headers) and never branched on in Slice 1.
