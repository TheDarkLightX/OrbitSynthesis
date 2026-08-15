# Authoritative bindings for the sharpening layers

```text
check_constant_15.py
  git blob e52297c6976df8dc451a0f90dcedc71eae292b4d

receipt_constant_15.json
  git blob 2c15b55bc2feb9f41af0d831b0685296348ad304
  semantic SHA-256 ad37969af91fee138674e66151ed1c55c6b4428f5786dce56a44e78744c25193

check_adaptive_113_8.py
  git blob 104be09dfac6b6be921a258a401becd74591e7f1

receipt_adaptive_113_8.json
  git blob 1b05456d234b323e3a5e28f4a85f2a22a6169113
  semantic SHA-256 fb4bb1f1cac137e8bbe22a47070b733858009d60d6f3d2ddc755951ff1380142
```

The lane `check.sh` regenerates all three receipts under normal and optimized Python and compares them byte-for-byte with the committed JSON files.
