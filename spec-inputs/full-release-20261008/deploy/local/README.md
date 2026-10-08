# Local release files

The publisher must supply real image digests, application binaries, migration commands, and health commands before this topology can run.
This package is a specification and reference contract. It contains no fake working images.
The final launcher implements `docs/local-delivery.md` and starts the complete Compose bundle.
The reference compose file intentionally rejects absent publisher image identities.
The operator fills cloud keys in a private copy of `.env.example`.
The launcher generates and retains internal credentials. The operator does not configure databases or accounts manually.
Do not call an empty bank or successful container startup a full release.
