# Public release notes

Version 1.0.0 of this repository was exported from a separately frozen development baseline. The public export is intentionally **not byte-identical** to that private snapshot.

Public-release transformations include:

- removing internal audit/forensic evidence and machine-local execution traces;
- removing local absolute-path diagnostics;
- removing locally captured verbatim excerpts from third-party webpages, app-store pages, and terms;
- keeping source URLs and provenance metadata;
- adding public documentation, contribution policy, security guidance, license, notice, and smoke tests;
- replacing the materialization-registry test's dependency on real captured source text with a synthetic fixture.

The private frozen baseline remains unchanged.
