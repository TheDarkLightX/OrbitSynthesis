#!/usr/bin/env python3
"""Build the fixed-Q review preprint from the validated Markdown source."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
SOURCE = REPO / "paper/FIXED_Q_TERM_COMPLEXITY_DRAFT.md"
OUTPUT_TEX = HERE / "FIXED_Q_TERM_COMPLEXITY_PREPRINT.tex"
OUTPUT_PDF = HERE / "FIXED_Q_TERM_COMPLEXITY_PREPRINT.pdf"
BUILD_RECEIPT = HERE / "BUILD_RECEIPT.json"
BUILD = HERE / "build"
GENERATED = BUILD / "manuscript.generated.md"
SOURCE_COMMIT = "ab20b9df50f331e430c1a43a9d8c3af9c1e8556c"
EXPECTED_SOURCE_SHA = "01ddf4565212f798d0adf5c4c9b16d6de9074a317a34f2a39a80051de55a5410"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def find_pandoc() -> Path:
    override = os.environ.get("PANDOC")
    candidates = [
        Path(override) if override else None,
        Path(shutil.which("pandoc")) if shutil.which("pandoc") else None,
        Path("/tmp/orbitsynthesis-pandoc/usr/bin/pandoc"),
    ]
    for candidate in candidates:
        if candidate and candidate.is_file():
            return candidate
    raise RuntimeError(
        "Pandoc 3.x is required. Install pandoc or set PANDOC=/absolute/path/to/pandoc."
    )


def pandoc_data_dir(pandoc: Path) -> Path | None:
    bundled = pandoc.parents[1] / "share/pandoc/data"
    if bundled.is_dir():
        return bundled
    extracted = Path("/tmp/orbitsynthesis-pandoc/usr/share/pandoc/data")
    if extracted.is_dir():
        return extracted
    return None


def split_source(text: str) -> tuple[str, str, str, str, str]:
    lines = text.splitlines()
    require(lines and lines[0].startswith("# "), "missing manuscript title")
    title = lines[0][2:].strip()

    abstract_at = lines.index("## Abstract")
    intro_at = lines.index("## 1. Introduction")
    contract_at = lines.index("## 12. Living-draft update contract")
    references_at = lines.index("## References")

    claim_at = lines.index("### Claim-status table")
    claim = "\n".join(lines[claim_at + 1 : abstract_at]).strip()
    abstract = "\n".join(lines[abstract_at + 1 : intro_at]).strip()
    abstract = abstract.split("\n**Keywords:**", maxsplit=1)[0].rstrip()
    body = "\n".join(lines[intro_at:contract_at]).strip()
    body = re.sub(r"(?<!\n)\n(?=#{2,4} )", "\n\n", body)
    references = "\n".join(lines[references_at + 1 :]).strip()
    return title, abstract, claim, body, references


def indent_block(value: str, spaces: int = 2) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line if line else prefix for line in value.splitlines())


def generated_markdown() -> str:
    source_sha = sha256(SOURCE)
    require(
        source_sha == EXPECTED_SOURCE_SHA,
        f"source drift: expected {EXPECTED_SOURCE_SHA}, observed {source_sha}",
    )
    title, abstract, claim, body, references = split_source(
        SOURCE.read_text(encoding="utf-8")
    )

    return f"""---
title: "{title}"
author:
  - "AUTHOR METADATA PENDING HUMAN APPROVAL"
date: "Review draft — 13 August 2026"
lang: en-US
abstract: |
{indent_block(abstract)}
keywords:
  - finite algebra
  - conservative operation
  - discriminator
  - term DAG
  - Shannon complexity
  - local coding
  - multivalued logic
  - circuit depth
---

\\begin{{reviewnotice}}
\\textbf{{Review and authorship status.}} This PDF is a non-archival review copy.
Creator names, order, affiliations, corresponding-author details, and ORCIDs
remain subject to human approval. Do not deposit or represent this file as an
authored preprint until that gate is closed. The mathematical source is bound to
SHA-256 \\texttt{{{source_sha}}} and repository commit
\\href{{https://github.com/TheDarkLightX/OrbitSynthesis/commit/{SOURCE_COMMIT}}}
{{\\texttt{{{SOURCE_COMMIT[:12]}}}}}. The manuscript has not been externally peer
reviewed. Novelty, patent freedom to operate, license interpretation, and
practical performance remain unknown and are not claimed.
\\end{{reviewnotice}}

\\noindent\\textbf{{Keywords:}} finite algebra; conservative operation;
discriminator; term DAG; Shannon complexity; local coding; multivalued logic;
circuit depth.

\\noindent\\textbf{{MSC 2020:}} 08A70 (applications of universal algebra in
computer science); 68Q06 (networks and circuits as models of computation;
circuit complexity).

## Claim status at a glance {{.unnumbered .unlisted}}

{claim}

{body}

\\clearpage

## Declarations {{.unnumbered}}

### Generative AI and AI-assisted technologies {{.unnumbered}}

During exploratory research and preparation of this review draft, the human
project lead used OpenAI Codex and other separately invoked large-language-model
research agents to propose reformulations and proof strategies, draft and
critique mathematical arguments, generate and review Python and Lean artifacts,
and assist with organization and copy-editing. Research Kernel and Morph were
used as research-orchestration and suggestion systems. Their outputs were
treated as untrusted suggestions: promoted claims were required to have
human-readable proofs and/or deterministic normal/optimized checkers,
independent reimplementations, mutation tests, and scoped Lean kernel checks,
as documented in Section 11 and the repository. AI systems are not authors and
cannot accept responsibility for the work. Before submission or archival
deposit, every named human author must inspect and approve the final manuscript,
verify citations and originality, and accept full responsibility for its
accuracy and integrity. The final archival version must replace this provisional
statement with a complete retained-record inventory of the services, model or
version identifiers when available, purposes, and affected research stages. No
generative-AI-created figures are included.

### Author contributions and approval {{.unnumbered}}

Human authorship, author order, affiliations, and ORCIDs have not yet been
approved. Contribution statements and corresponding-author details also remain
pending. This review copy must not be deposited until all named human authors
approve the final text and accept accountability for the work.

### Data, code, and reproducibility {{.unnumbered}}

No empirical or personal data were used. Source code, proof artifacts,
deterministic checkers, and frozen receipts are available in the public
[OrbitSynthesis repository](https://github.com/TheDarkLightX/OrbitSynthesis)
and in [draft PR 16](https://github.com/TheDarkLightX/OrbitSynthesis/pull/16).
Section 11 gives the exact reproduction map. The principal manuscript source
hash is `{source_sha}`.

### Funding and competing interests {{.unnumbered}}

Funding and competing-interest declarations have not yet been supplied by the
human authors and must be completed before submission. No legal opinion about
patents, freedom to operate, or license scope is made in this manuscript.

### Ethics statement {{.unnumbered}}

This work is mathematical and computational and involved no human participants,
animals, personal data, or clinical intervention.

## References {{.unnumbered}}

{references}
"""


def run(command: list[str], *, env: dict[str, str], log_name: str) -> None:
    completed = subprocess.run(
        command,
        cwd=REPO,
        env=env,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    log_path = BUILD / log_name
    log_path.write_bytes(completed.stdout)
    if completed.returncode != 0:
        tail = completed.stdout.decode("utf-8", errors="replace").splitlines()[-80:]
        print("\n".join(tail), file=sys.stderr)
        raise RuntimeError(f"command failed ({completed.returncode}): {' '.join(command)}")


def version_line(command: list[str]) -> str:
    completed = subprocess.run(
        command,
        cwd=REPO,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return next(line for line in completed.stdout.splitlines() if line.strip())


def main() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    GENERATED.write_text(generated_markdown(), encoding="utf-8")

    pandoc = find_pandoc()
    data_dir = pandoc_data_dir(pandoc)
    command = [str(pandoc)]
    if data_dir:
        command.append(f"--data-dir={data_dir}")
    command.extend(
        [
            "--from=markdown+tex_math_dollars+raw_tex+fenced_divs+pipe_tables+autolink_bare_uris+strikeout",
            "--to=latex",
            "--standalone",
            "--toc",
            "--toc-depth=2",
            "--listings",
            "--lua-filter",
            str(HERE / "academic.lua"),
            "--include-in-header",
            str(HERE / "preamble.tex"),
            "--variable=documentclass:article",
            "--variable=fontsize:11pt",
            "--variable=geometry:margin=1in",
            "--variable=mainfont:TeX Gyre Pagella",
            "--variable=mathfont:TeX Gyre Pagella Math",
            "--variable=sansfont:TeX Gyre Heros",
            "--variable=monofont:Latin Modern Mono",
            "--variable=CJKmainfont:Noto Serif CJK SC",
            "--variable=CJKsansfont:Noto Sans CJK SC",
            "--variable=CJKmonofont:Noto Sans Mono CJK SC",
            "--variable=colorlinks:true",
            "--output",
            str(OUTPUT_TEX),
            str(GENERATED),
        ]
    )

    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = "1786579200"
    env["FORCE_SOURCE_DATE"] = "1"
    run(command, env=env, log_name="pandoc.stdout.log")
    run(
        [
            "latexmk",
            "-xelatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-outdir={BUILD}",
            str(OUTPUT_TEX),
        ],
        env=env,
        log_name="latexmk.stdout.log",
    )

    built_pdf = BUILD / OUTPUT_PDF.name
    require(built_pdf.is_file(), "XeLaTeX did not produce the expected PDF")
    shutil.copy2(built_pdf, OUTPUT_PDF)

    receipt = {
        "schema": "orbitsynthesis.academic_preprint_build.v1",
        "status": "PASS",
        "review_status": "NON_ARCHIVAL_REVIEW_COPY",
        "source": {
            "path": str(SOURCE.relative_to(REPO)),
            "sha256": sha256(SOURCE),
            "repository_commit": SOURCE_COMMIT,
        },
        "build_inputs": {
            "script_sha256": sha256(Path(__file__)),
            "lua_filter_sha256": sha256(HERE / "academic.lua"),
            "preamble_sha256": sha256(HERE / "preamble.tex"),
        },
        "outputs": {
            "tex": {"path": OUTPUT_TEX.name, "sha256": sha256(OUTPUT_TEX)},
            "pdf": {"path": OUTPUT_PDF.name, "sha256": sha256(OUTPUT_PDF)},
        },
        "toolchain": {
            "pandoc": version_line([str(pandoc), "--version"]),
            "latexmk": version_line(["latexmk", "-v"]),
            "xelatex": version_line(["xelatex", "--version"]),
            "source_date_epoch": env["SOURCE_DATE_EPOCH"],
        },
    }
    BUILD_RECEIPT.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(f"source_sha256={sha256(SOURCE)}")
    print(f"tex_sha256={sha256(OUTPUT_TEX)}")
    print(f"pdf_sha256={sha256(OUTPUT_PDF)}")
    print(f"receipt_sha256={sha256(BUILD_RECEIPT)}")
    print(f"pdf={OUTPUT_PDF}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"BUILD FAILED: {error}", file=sys.stderr)
        raise
