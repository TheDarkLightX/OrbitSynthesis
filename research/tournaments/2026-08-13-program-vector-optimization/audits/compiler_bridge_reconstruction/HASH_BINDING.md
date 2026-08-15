# Authoritative repository bindings

The repository contents API normalizes the uploaded source bytes independently of the locally executed working copies. Therefore the authoritative publication bindings for this reconstruction are the Git blob object IDs below, not the local SHA-256 source lines in the first version of `REPORT.md`.

```text
compiler_bridge_model.py
  git blob 00cc8a96fc90aa84cdcbf3fdb3bd6f1c70f4d262

check_compiler_bridge.py
  git blob 666fe8b0aa1184a081d5f7dc73bc80bd7e606927

receipt.json
  git blob 2eb2f9193d3675ce53de8e07704632efbc0dfe1f
  semantic SHA-256 b0dec4c34465d5b25e5aa35e59ac6016452afcb9df1307bbb6b52b5399b81e23

check_constant_15.py
  git blob e52297c6976df8dc451a0f90dcedc71eae292b4d

receipt_constant_15.json
  git blob 2c15b55bc2feb9f41af0d831b0685296348ad304
  semantic SHA-256 ad37969af91fee138674e66151ed1c55c6b4428f5786dce56a44e78744c25193
```

The committed `check.sh` regenerates both receipts under normal and optimized Python, compares the results byte-for-byte, and then compares them with the committed JSON files. These comparisons—not prose hash lines—are the semantic publication gate.

The hosted workflow has so far received no runner and executed zero steps because of the repository account's existing Actions billing/spending restriction. Until a runner executes, the repository sources should be described as locally replayed and remotely gate-ready, not remotely executed.
