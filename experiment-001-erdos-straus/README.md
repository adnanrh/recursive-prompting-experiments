https://substack.com/@meheruem/note/p-222596480

# Erdős–Straus Conjecture — Recursive Prompting Experiment 001

A reproducible, AI-assisted mathematical investigation into the Erdős–Straus conjecture.

## About the experiment

This experiment explored whether an AI assistant, given a self-authored research prompt and a short investigation window, could produce a genuine mathematical breakthrough.

The assistant, Aya (ChatGPT), conducted the mathematical investigation. The human participant initiated the experiment, supplied its goals, and facilitated the prompting process.

The initial investigation targeted approximately ten minutes. Subsequent verification and editorial review were conducted separately.

## Mathematical problem

The Erdős–Straus conjecture asks whether every integer n ≥ 2 admits positive integers x, y, z satisfying:

4/n = 1/x + 1/y + 1/z

## Results

**Classification C — Reproduction of existing mathematical results.**

No proof or counterexample to the conjecture was obtained. No mathematical novelty is claimed.

The investigation:

- Derived an exact finite search criterion for completing candidate unit-fraction decompositions.
- Examined all 9,592 primes below 100,000.
- Found that every prime in that range admits a solution within the first eight eligible choices.
- Identified the prime 118,801 as requiring fifteen choices.
- Confirmed that the exceptional behaviour at 118,801 had already been documented by Ionascu and Wilson in 2011.

A subsequent AI-assisted verification reproduced the principal computational findings.

## Repository contents

- `verify_review.py` — Python verification program using exact integer arithmetic.
- `review_results.json` — Recorded verification results and computational failure certificates.

The files document the subsequent verification review, not the original SoulWorks execution.

## Reproducibility

The verification program uses Python's standard library and requires no third-party dependencies.

Run the script using a compatible Python 3 installation and consult the source code for its output behaviour. The accompanying JSON contains the saved results and certificates.

The computations verify finite cases only. They do not establish the conjecture for all positive integers.

## Limitations

This was an AI-assisted investigation and computational review, not independent expert mathematical verification.

No formal proof assistant was used. Agreement between computational methods does not constitute a universal proof.

## References

Eugen J. Ionascu and Andrew Wilson, [On the Erdős–Straus Conjecture (2011)](https://www.csm.ro/reviste/Revue_Mathematique/pdfs/2011/1/Ionascu.pdf).

Christian Elsholtz and Terence Tao, [Counting the number of solutions to the Erdős–Straus equation on unit fractions](https://arxiv.org/abs/1107.1010).

## Philosophical motivation

The experiment was motivated by a distinction between mathematical output and the human experience of mathematical understanding.

Its purpose was not merely to obtain an answer, but to explore what mathematical discovery means when machines can increasingly participate in mathematical research.

**An answer is not everything we came for.**
