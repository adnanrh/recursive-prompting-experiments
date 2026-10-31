#!/usr/bin/env python3
"""Verify the five included P vs NP Experiment 003 example certificates.

Standard library only. This checks finite certificates, not the general theorem,
novelty, or a resolution of P vs NP.
"""
from pathlib import Path
from itertools import combinations
import json
import hashlib
from verify_certificates import verify_ns, require

ROOT = Path(__file__).resolve().parent
EXAMPLES = {
    "constructed_php_3_2_lower.json": (3, 2, 3, False, False),
    "constructed_php_3_2_upper.json": (3, 2, 4, True, False),
    "constructed_php_4_3_lower.json": (4, 3, 5, False, False),
    "constructed_php_4_3_upper.json": (4, 3, 6, True, False),
    "functional_php_3_2_d3.json": (3, 2, 3, True, True),
}

def expected_cnf(p, h, functional):
    clauses = [[i*h+j+1 for j in range(h)] for i in range(p)]
    clauses += [[-(i*h+j+1), -(k*h+j+1)]
                for j in range(h) for i, k in combinations(range(p), 2)]
    if functional:
        clauses += [[-(i*h+j+1), -(i*h+k+1)]
                    for i in range(p) for j, k in combinations(range(h), 2)]
    return clauses

def main():
    manifest = json.loads((ROOT / "checksums.json").read_text())
    for filename, (p, h, degree, refuted, functional) in EXAMPLES.items():
        path = ROOT / "certificates" / filename
        require(hashlib.sha256(path.read_bytes()).hexdigest() == manifest[filename],
                f"Checksum mismatch: {filename}")
        data = json.loads(path.read_text())
        require(data["variables"] == p*h and data["pigeons"] == p and data["holes"] == h,
                f"Incorrect dimensions: {filename}")
        require(data["degree"] == degree and data["refuted"] is refuted,
                f"Incorrect claim: {filename}")
        require(data["cnf"] == expected_cnf(p, h, functional),
                f"Incorrect encoding: {filename}")
        result = verify_ns(data)
        print(f"PASS {filename}: {result}")
    print("PASS: all five included certificates verified")

if __name__ == "__main__":
    main()
