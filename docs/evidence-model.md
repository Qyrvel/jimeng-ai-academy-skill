# Evidence model

The source engine uses two independent classifications.

## Trust tiers

Sources are ranked by authority and directness. Official product/model documentation should be preferred over secondary/community descriptions for product facts.

## Information type

- `DOCUMENTED` — directly supported by a source in the recorded scope.
- `OBSERVED` — observed in a specific client/account/state/time context.
- `INFERRED` — a reasoned conclusion that must not be represented as direct documentation.
- `UNVERIFIED` — not yet sufficiently established.

## Scope is part of the claim

A statement about a Seed model is not automatically a statement about the Jimeng product. A historical app-store entry is not proof of current Web availability. A logged-in Web observation is not proof of Android/iOS behavior or every account/region.

## Public-release evidence policy

The private frozen development baseline retained minimal local evidence captures. This public export deliberately does not redistribute those verbatim third-party captures. `source-registry.json` remains the provenance index. Contributors should verify original URLs and create their own local evidence material when needed.
