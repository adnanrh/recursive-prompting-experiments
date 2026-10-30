# Experiment 002 — Graceful Tree Conjecture

*An AI-led mathematical investigation conducted through recursive prompting.*

## Overview

The Graceful Tree Conjecture, associated with Gerhard Ringel and Anton Kotzig, proposes that every finite tree admits a *graceful labeling*.

For a tree with \(n\) vertices, a graceful labeling assigns each vertex a distinct integer from \(0\) to \(n-1\), such that the absolute differences across its \(n-1\) edges are exactly the integers from \(1\) to \(n-1\).

The general conjecture remains unresolved.

## Investigation

This experiment tasked an AI model with investigating the conjecture through recursive prompting, with the objective of producing either a general proof or a rigorously verified counterexample.

The investigation explored constructive approaches, gap-insertion arguments, limitations of proposed proof strategies, and computational searches for graceful labelings.

**Outcome:** No general proof or counterexample was established.

The investigation produced local mathematical arguments and computational observations, but did not resolve the universal conjecture.

## Published Article

**[Twenty Failed Searches. Zero Counterexamples.](https://meheruem.substack.com/p/twenty-failed-searches-zero-counterexamples)**

The article serves as the primary research report, documenting the mathematical investigation, methodology, findings, limitations, and conclusions.

## Verification

This repository includes an independent Python verification utility:

[`verify_results_002.py`](verify_results_002.py)

The script checks supplied graceful-labeling certificates for:

- Valid tree structure.
- Bijective vertex labels.
- Distinct edge differences covering the required integer range.
- Invalid or malformed certificate data.

The verifier uses Python's standard library and requires no external dependencies.

It accepts JSON certificates containing graph edges and vertex labels. Run it using:

`python verify_results_002.py <certificate-file.json>`

**Verification status:** The original computational certificates are not currently included in this repository. Consequently, the published computational results have not been independently reproduced using this utility.

The script is provided as a tool for examining graceful-labeling certificates, not as proof of the conjecture or independent confirmation of the published search results.

## Interpretation

Computational verification of individual graceful labelings does not establish that every finite tree is graceful.

Likewise, unsuccessful searches for counterexamples do not establish that no counterexample exists.

The purpose of this experiment is to document the investigation faithfully, including partial results, failed approaches, and unresolved questions.

---

*Part of the [Recursive Prompting Experiments](../) project.*

*Research and writing: Meheruem · Mathematical investigation conducted with AI assistance.*
