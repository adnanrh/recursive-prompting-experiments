# Experiment 004 migration and reproduction

## Provenance and merge requirement

Source: https://github.com/adnanrh/experiment-004-zagreb-indices

Imported source tip: `1fd4a1b58f5e16dd24892a01f842cf480695abda`.
Audited mathematical commit: `68a494573fdbd2e629c620a263dafed5853ac26e`.
Destination base: `6b2fec9cdede7d0b6503512c366bbff6c5b8b392`.
Destination directory: `experiment-004-zagreb-indices/`.

The migration uses `git subtree add` **without squash**. Its merge commit joins the existing destination history to the original source tip. All three source commits retain their original SHA and ancestry. A following commit captures the 20 previously untracked manuscript files without changing the source repository. All 62 tracked source files and those 20 manuscript files are byte-for-byte preserved, including historical reports and logs. No proof edits or dependency-pin changes were made.

**Merge this PR using a merge commit. Do not squash or rebase it.** Squashing/rebasing can discard the original ancestry from the destination default branch. After merging, recheck `git merge-base --is-ancestor 68a494573fdbd2e629c620a263dafed5853ac26e main` from a fresh full clone before considering source deletion. This PR does not authorize merging or deleting anything.

## Reproduce the nested project

From a checkout of the migration branch (or main after an approved merge):

```bash
cd experiment-004-zagreb-indices
lake exe cache get
python3 scripts/check_dependency_pins.py
python3 scripts/audit_sources.py
python3 migration/verify_preservation.py
lake build
lake env lean Audit.lean
python3 scripts/fresh_audit.py
python3 manuscript/arxiv/validation/check_manuscript.py
cd manuscript/arxiv
bash build.sh
```

The migration validation uses Ubuntu/WSL2, Lean 4.19.0 and Mathlib `c44e0c8ee63ca166450922a373c7409c5d26b00b`. Pinned dependency source/cache directories were reused locally via an ignored `.lake/packages` symlink. All project modules were freshly compiled. The symlink is not committed or needed by fresh clones; `lake exe cache get` supplies dependencies. No compiler or complete Mathlib bootstrap is claimed.

The historical audited commit has **Experiment 004 at repository root**, not at the new subdirectory. It can be reproduced from the destination alone:

```bash
git clone https://github.com/adnanrh/recursive-prompting-experiments.git
cd recursive-prompting-experiments
# Before merge, first fetch/checkout the PR branch to obtain its ancestry.
git fetch origin codex/migrate-experiment-004
git worktree add --detach ../zagreb004-audited 68a494573fdbd2e629c620a263dafed5853ac26e
cd ../zagreb004-audited
lake exe cache get
lake build
lake env lean Audit.lean
```

## Tooling and retained historical artifacts

The Lean and Python project scripts resolve paths relative to their source locations or change into the project directory; no path edits were needed. `check_candidate.sh` also works from the nested project.

`manuscript/arxiv/validation/check_submission.py` is preserved as a historical standalone-repository check. Its Git comparison assumes the project is at the Git root, so it must not be used unchanged as the nested migration checker. It also rewrites historical validation outputs. Instead, use `migration/verify_preservation.py` for exact Git/blob comparisons and build the ZIP in an empty temporary directory with pdfLaTeX, BibTeX, pdfLaTeX, pdfLaTeX. The migration performed that sequence, compared the resulting PDF text and bibliography, and retained the original deliverable bytes. No verification script was rewritten.

The manuscript validation reports and hashes predate its final four editorial revisions. They remain historical evidence, not current PDF hashes. `source-file-hashes.json` records the actual migrated bytes. The original `SHA256SUMS`, obsolete source headers, old report statuses, and local-only evidence links are also retained without rewriting.

## Evidence and exclusions

The `evidence/` directory records current migration verification. Python's 18 original tests and exhaustive certificate verification were run after extracting the unchanged original verification archive into a temporary directory. The manuscript was rebuilt from the nested path and its original three-file source ZIP was rebuilt independently. Both PDFs had identical extracted text, with ten pages and no final LaTeX warnings. Optional SymPy checks remain unavailable; standard-library checks passed.

All 20 nonignored manuscript files were included. No intended uncommitted source file was omitted. Ignored `.lake/`, `local-logs/`, manuscript `build/`, Python caches, and Windows `Zone.Identifier` metadata were excluded. The source working tree remains unchanged, including its untracked manuscript. No LFS pointers, submodules, tags, or GitHub releases were present in either repository. No files from Experiments 001–003 were changed.

## Original-URL inventory and deletion risks

`original-url-inventory.json` is the exact occurrence list (11 occurrences), including ZIP contents and PDF hyperlink annotations. Four original URL forms occur:

1. `https://github.com/adnanrh/experiment-004-zagreb-indices` — novelty report, line 282. Preserve this historical provenance statement. Before deletion, add a separate archival/citation mapping; do not silently rewrite the report.
2. `https://github.com/adnanrh/experiment-004-zagreb-indices.git` — experiment README line 41, manuscript `main.tex` line 413, corresponding ZIP source, and PDF reproduction commands. For a future approved revision, change clone URL to the destination and adjust the directory command. At the audited SHA the project is at the root; at the migration tip it is nested. These two reproduction modes must not be confused.
3. `https://github.com/adnanrh/experiment-004-zagreb-indices/commit/68a494573fdbd2e629c620a263dafed5853ac26e` — experiment README line 24. The proposed equivalent is `https://github.com/adnanrh/recursive-prompting-experiments/commit/68a494573fdbd2e629c620a263dafed5853ac26e`.
4. `https://github.com/adnanrh/experiment-004-zagreb-indices/tree/68a494573fdbd2e629c620a263dafed5853ac26e` — manuscript `references.bib` line 48, generated `main.bbl` line 35, their ZIP copies, and the page-10 PDF hyperlink. The proposed equivalent is `https://github.com/adnanrh/recursive-prompting-experiments/tree/68a494573fdbd2e629c620a263dafed5853ac26e`. The SHA must remain unchanged. Bibliography, PDF, and ZIP must be rebuilt together only under a separately approved manuscript revision.

All these original references are deliberately retained in this migration; the source is still available. The original research PDFs and original verification ZIP were scanned and contain no additional instances of this URL. Logs and historical reports must not be rewritten merely to erase old URLs. This guide and the inventory themselves record original URLs as provenance.

Deletion remains risky until the ancestry-preserving PR merge is verified, destination-only reproduction is tested from a fresh clone, current public citations are updated with author approval, and any externally distributed PDF/ZIP copies or links are addressed. Repository deletion does not guarantee redirects. Git history preservation does not preserve GitHub issues/settings or external links. No deletion, archive, release, arXiv revision, or social publication is part of this migration.

## Final migration verification result

`lake build` and `lake env lean Audit.lean` both exited **0**, without compiler errors or warnings. All project modules, including `Zagreb004.Full`, compiled. The audit covers 90 public theorems; `Zagreb004.fullTarget` depends only on `propext`, `Classical.choice`, and `Quot.sound`. Dependency pins, source policy, byte preservation, Python tests/certificates, nested manuscript compilation and isolated source-ZIP compilation passed. See `evidence/lean-and-preservation-results.json` and `evidence/validation-results.json`. No mathematical or migration build blocker remains. The historical root-assuming manuscript checker and original URL dependencies remain explicitly documented above.

New migration log copies have trailing whitespace normalized for Git review; historical source logs are unchanged.
