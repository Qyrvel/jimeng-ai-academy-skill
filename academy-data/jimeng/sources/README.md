# Public source layer

This public repository includes the **source registry and source scope**, but intentionally does **not** redistribute locally captured verbatim excerpts from third-party websites, app-store pages, or terms of service.

Why: the private/frozen development baseline retained minimal evidence captures for auditability. A public open-source release should instead point contributors to the original URLs and let them re-materialize evidence under the repository's evidence policy.

To contribute new evidence:

1. Start from `source-registry.json`.
2. Follow `.agents/skills/ai-academy/references/source-policy.md` and `evidence-materialization-policy.md`.
3. Capture only the minimum text needed for the evidence scope.
4. Do not commit full webpages, screenshots, login-gated content, or material you are not allowed to redistribute.
5. Keep product, model, API, observed, and version scopes separate.

The test suite uses a synthetic local fixture for materialization-registry mechanics; it is not evidence about any third-party product.
