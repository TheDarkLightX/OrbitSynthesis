# Direct-Q formal layer

Date: 2026-08-15  
Status: **UNDER TEST**

`DirectQMux.lean` contains no `sorry`, `admit`, or declared `axiom`. It formalizes:

```text
Mux_Q(0;b0,b1,b2)=b0,
Mux_Q(1;b0,b1,b2)=b1,
Mux_Q(2;b0,b1,b2)=b2,
operation count =5,
payload depth =3,
0->10, 1->01, 2->00,
Dec(q,p)=d(q,p,2),
encoder counts =1+1,
decoder count =1.
```

The value names are variables in the scoped term grammar. In the integrated compiler they are the shared roots produced by the nonbinary anchor.

The source imports the frozen `ProgramVectorCost` grammar and is compiled by `check_lean.sh` after SHA-256 verification of the upstream signed-router, program-vector, and cost sources.

No result on this branch should be described as newly Lean-checked until the pinned compiler gate executes successfully. GitHub-hosted runners have previously been blocked before step execution by the repository account’s Actions billing/spending restriction.

The all-arity size-<8 theorem is a paper proof plus deterministic executable audit. This Lean layer covers only the local mux/code bridge.
