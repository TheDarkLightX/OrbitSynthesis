# Fixed-Q academic review preprint

This directory contains the reproducible academic-format build of
`paper/FIXED_Q_TERM_COMPLEXITY_DRAFT.md`.

The generated PDF is deliberately marked **REVIEW DRAFT** because human creator
names, author order, affiliations, ORCIDs, contributions, funding, competing
interests, and final approval have not yet been supplied. It must not be
deposited in an archival repository until those gates are closed.

## Build

Requirements:

- Python 3.11 or later;
- Pandoc 3.x;
- `latexmk` and XeLaTeX;
- TeX Live packages used by `preamble.tex`; and
- TeX Gyre and Noto Serif CJK fonts.

Run:

```bash
python3 paper/preprint/build_preprint.py
```

The build fails closed if the validated Markdown source hash has drifted. It
produces:

- `FIXED_Q_TERM_COMPLEXITY_PREPRINT.tex`;
- `FIXED_Q_TERM_COMPLEXITY_PREPRINT.pdf`;
- `BUILD_RECEIPT.json`, binding the source, build inputs, outputs, and
  toolchain; and
- disposable intermediates under `paper/preprint/build/`.

## AI-disclosure rationale

The provisional declaration follows the common cross-publisher baseline:

1. AI tools are not authors and cannot accept accountability.
2. Substantive AI use is disclosed by tool category and purpose.
3. AI use in research, code, or analysis is described as methodology rather
   than hidden as copy-editing.
4. Human authors must verify the final text, citations, originality, and
   integrity and must approve submission.
5. The target journal's current policy must be checked again at submission,
   and the disclosure should also be repeated in the cover letter when asked.
6. A confidential referee manuscript must not be uploaded to an external AI
   system without the authors' permission and adequate confidentiality terms.
7. Before archival deposit, the human authors should reconcile the retained
   session records into a complete inventory of services, model/version
   identifiers when available, purposes, and affected research stages.

Primary guidance consulted on 2026-08-13:

- [ICMJE: Use of AI by Authors](https://www.icmje.org/recommendations/browse/artificial-intelligence/ai-use-by-authors.html)
- [ICMJE: Use of Artificial Intelligence in Publishing](https://www.icmje.org/recommendations/browse/artificial-intelligence/)
- [Elsevier: Generative AI policies for journals](https://www.elsevier.com/about/policies-and-standards/generative-ai-policies-for-journals)
- [Nature Portfolio editorial policies](https://www.nature.com/nature-portfolio/for-researchers/editorial-policies)

These are transparency and authorship practices, not a substitute for the
policy of the eventual journal or preprint server.
