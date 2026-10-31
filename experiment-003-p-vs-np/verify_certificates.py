#!/usr/bin/env python3
"""Separate checker for Experiment 003 artifacts (standard library only).

No imports from either producer script. Polynomials are independently expanded
as sets of frozensets of variable numbers, rather than producer bit vectors.
Checks both positive and negative certificates, exhaustive small truth tables,
and deliberately corrupted certificates. This is software cross-checking by
the same authoring assistant, NOT independent expert or proof-assistant review.

Usage: python verify_certificates.py --evidence evidence
"""
from __future__ import annotations
import argparse
from collections import Counter
import copy
import hashlib
from itertools import combinations
import json
from pathlib import Path
import time

Monomial = frozenset[int]
Polynomial = set[Monomial]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def unpack(mask: int, n: int) -> Monomial:
    require(isinstance(mask, int) and 0 <= mask < (1 << n), 'invalid monomial mask')
    return frozenset(v for v in range(1, n+1) if mask >> (v-1) & 1)


def expand(clause: list[int]) -> Polynomial:
    terms: Polynomial = {frozenset()}
    for literal in clause:
        updated: Polynomial = set()
        for term in terms:
            extended = term | {abs(literal)}
            updated.symmetric_difference_update((extended,))
            if literal > 0:
                updated.symmetric_difference_update((term,))
        terms = updated
    return terms


def poly_times_monomial(polynomial: Polynomial, monomial: Monomial) -> Polynomial:
    terms: Polynomial = set()
    for term in polynomial:
        terms.symmetric_difference_update((term | monomial,))
    return terms


def verify_ns(data: dict) -> dict:
    n, degree, clauses = data['variables'], data['degree'], data['cnf']
    for clause in clauses:
        require(len({abs(v) for v in clause}) == len(clause), 'repeated/tautological clause')
        require(all(1 <= abs(v) <= n for v in clause), 'invalid variable')
    polynomials = [expand(c) for c in clauses]
    certificate = data['certificate']
    if certificate['type'] == 'identity':
        total: Polynomial = set()
        for ci, mask in certificate['terms']:
            require(0 <= ci < len(clauses), 'invalid clause index')
            multiplier = unpack(mask, n)
            require(len(multiplier)+len(clauses[ci]) <= degree, 'degree exceeded')
            total.symmetric_difference_update(poly_times_monomial(polynomials[ci], multiplier))
        require(total == {frozenset()}, 'claimed identity does not sum to one')
        require(data['refuted'] is True, 'incorrect polarity')
        return {'type': 'identity', 'terms_checked': len(certificate['terms'])}
    require(certificate['type'] == 'dual', 'unknown certificate type')
    support = {unpack(mask, n) for mask in certificate['support']}
    require(frozenset() in support, 'dual does not map one to one')
    require(all(len(m) <= degree for m in support), 'dual outside truncated space')
    rows_checked = 0
    for clause, polynomial in zip(clauses, polynomials):
        for k in range(min(n, degree-len(clause))+1):
            for variables in combinations(range(1, n+1), k):
                row = poly_times_monomial(polynomial, frozenset(variables))
                require(len(row & support) % 2 == 0, 'dual fails on an admissible row')
                rows_checked += 1
    require(data['refuted'] is False, 'incorrect polarity')
    return {'type': 'dual', 'rows_checked': rows_checked}


def verify_resolution(data: dict) -> dict:
    n, width = data['variables'], data['width']
    inputs = [frozenset(c) for c in data['cnf']]
    derived: list[frozenset[int]] = []
    for line, record in enumerate(data['certificate']):
        clause = frozenset(record['clause'])
        require(len(clause) == len(record['clause']) and len(clause) <= width, 'invalid clause width')
        require(all(1 <= abs(v) <= n and -v not in clause for v in clause), 'invalid clause')
        if 'input' in record:
            require(clause == inputs[record['input']], 'not an input clause')
        else:
            a, b = record['parents']
            pivot = record['pivot']
            require(0 <= a < line and 0 <= b < line, 'parents not earlier')
            require(1 <= pivot <= n, 'invalid pivot')
            left, right = derived[a], derived[b]
            require((pivot in left and -pivot in right) or (-pivot in left and pivot in right),
                    'pivot missing from parents')
            require(clause == (left | right) - {pivot, -pivot}, 'incorrect resolvent')
        derived.append(clause)
    if data['refuted']:
        require(derived and derived[-1] == frozenset(), 'no final empty clause')
        return {'type': 'refutation', 'lines_checked': len(derived)}
    closed = set(derived)
    require(frozenset() not in closed, 'negative certificate contains empty clause')
    require(all(c in closed for c in inputs if len(c) <= width), 'input missing from closure')
    resolvents_checked = 0
    for i, left in enumerate(derived):
        for right in derived[i+1:]:
            for pivot in left:
                if -pivot not in right:
                    continue
                resolvent = (left | right) - {pivot, -pivot}
                if len(resolvent) <= width and not any(-v in resolvent for v in resolvent):
                    require(resolvent in closed, 'set not saturated under permitted resolution')
                    resolvents_checked += 1
    return {'type': 'saturated_closure', 'lines_checked': len(derived),
            'permitted_resolvents_checked': resolvents_checked}


def verify_bdd(data: dict) -> int:
    m, nodes = data['pairs'], data['nodes']
    order = data['order']
    require(sorted(order) == list(range(1,2*m+1)), 'invalid order')
    level = {v: i for i,v in enumerate(order)}
    require(len({tuple(node) for node in nodes}) == len(nodes), 'duplicate BDD nodes')
    for node_id, (variable, low, high) in enumerate(nodes, start=2):
        require(variable in level and low != high, 'unreduced node')
        require(0 <= low < node_id and 0 <= high < node_id, 'invalid edge')
        for child in (low, high):
            require(child < 2 or level[nodes[child-2][0]] > level[variable], 'order violation')
    require(0 <= data['root'] < len(nodes)+2, 'invalid root')
    for assignment in range(1 << (2*m)):
        node = data['root']
        while node > 1:
            variable, low, high = nodes[node-2]
            node = high if assignment & (1 << (variable-1)) else low
        expected = all(bool(assignment & (1 << i)) == bool(assignment & (1 << (m+i))) for i in range(m))
        require(bool(node) == expected, 'incorrect BDD truth value')
    return 1 << (2*m)


def verify_rank(data: dict) -> int:
    m, matrix = data['m'], data['matrix']
    side = 1 << m
    require(len(matrix) == side and all(len(row) == side for row in matrix), 'matrix dimension')
    for a in range(side):
        for b in range(side):
            parity = sum((a >> i & 1)*(b >> i & 1) for i in range(m)) % 2
            require(matrix[a][b] == (-1 if parity else 1), 'incorrect sign entry')
    for a in range(side):
        for b in range(side):
            dot = sum(x*y for x,y in zip(matrix[a],matrix[b]))
            require(dot == (side if a == b else 0), 'incorrect Gram identity')
    return side


def verify_tseitin(data: dict) -> int:
    edges, charges, clauses = data['edges'], data['charges'], data['cnf']
    total: Polynomial = set()
    for clause in clauses:
        total.symmetric_difference_update(expand(clause))
    require(total == {frozenset()}, 'Tseitin F_2 identity failed')
    require(sum(charges)%2 == 1, 'charge parity')
    for a in range(1 << len(edges)):
        parity_ok = all((sum((a >> i)&1 for i,e in enumerate(edges) if v in e) % 2) == charge
                        for v,charge in enumerate(charges))
        cnf_ok = all(any(bool(a >> (abs(lit)-1)&1) == (lit > 0) for lit in c) for c in clauses)
        require(parity_ok == cnf_ok, 'CNF differs from XOR system')
        require(not cnf_ok, 'unexpected satisfying assignment')
    return 1 << len(edges)


def span_contains_one(clauses: list[list[int]], n: int, degree: int) -> bool:
    """Set-valued elimination, independent of producer's packed integer matrix."""
    key = lambda monomial: tuple(sorted(monomial))
    pivots: dict[Monomial, Polynomial] = {}
    for clause in clauses:
        polynomial = expand(clause)
        for k in range(min(n,degree-len(clause))+1):
            for variables in combinations(range(1,n+1),k):
                row = poly_times_monomial(polynomial, frozenset(variables))
                while row:
                    pivot = max(row,key=key)
                    if pivot not in pivots:
                        pivots[pivot] = row
                        break
                    row = row ^ pivots[pivot]
    target: Polynomial = {frozenset()}
    while target:
        pivot = max(target,key=key)
        if pivot not in pivots:
            return False
        target = target ^ pivots[pivot]
    return True


def verify_regression(data: dict) -> dict:
    universe, rows = data['universe'], data['rows']
    require(len(rows) == 4096, 'regression incomplete')
    counter: Counter[str] = Counter()
    for expected_subset, (subset, claimed_count, claimed_d2, claimed_d3) in enumerate(rows):
        require(subset == expected_subset, 'regression subset missing')
        clauses = [clause for i,clause in enumerate(universe) if subset >> i & 1]
        count = 0
        for a in range(8):
            if all(any(bool(a & (1 << (abs(lit)-1))) == (lit > 0) for lit in c) for c in clauses):
                count += 1
        require(count == claimed_count, 'SAT count differs')
        d2, d3 = span_contains_one(clauses,3,2), span_contains_one(clauses,3,3)
        require((d2,d3) == (claimed_d2,claimed_d3), 'independent span result differs')
        require(d3 == (count == 0), 'degree-three completion mismatch')
        counter['satisfiable' if count else 'unsatisfiable'] += 1
    return {'formulas': len(rows), **counter}


def must_reject(function, data: dict) -> None:
    try:
        function(data)
    except (ValueError, KeyError, IndexError):
        return
    raise ValueError('negative control incorrectly accepted')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, default=Path('evidence'))
    args = parser.parse_args()
    base = args.evidence
    start = time.perf_counter()
    load = lambda filename: json.loads((base/filename).read_text())
    checked = []
    ns_files = sorted(base.glob('ns_php_*.json')) + sorted(base.glob('constructed_php_*_upper.json')) + sorted(base.glob('constructed_php_*_lower.json'))
    for path in ns_files:
        checked.append({'file':path.name, **verify_ns(load(path.name))})
    for path in sorted(base.glob('resolution_*.json')):
        checked.append({'file':path.name, **verify_resolution(load(path.name))})
    for path in sorted(base.glob('bdd_eq_*.json')):
        checked.append({'file':path.name, 'assignments_checked': verify_bdd(load(path.name))})
    for path in sorted(base.glob('inner_product_sign_*.json')):
        checked.append({'file':path.name, 'verified_full_rank': verify_rank(load(path.name))})
    for path in sorted(base.glob('tseitin_*.json')):
        checked.append({'file':path.name, 'assignments_checked': verify_tseitin(load(path.name))})
    regression = verify_regression(load('exhaustive_2cnf_3vars.json'))
    # Five negative controls: remove a real term, corrupt lambda(1), delete
    # a refutation's conclusion, alter a BDD result, and change a matrix entry.
    damaged = copy.deepcopy(load('ns_php_3_2_d4.json'))
    damaged['certificate']['terms'].pop()
    must_reject(verify_ns, damaged)
    damaged = copy.deepcopy(load('ns_php_4_3_d5.json'))
    damaged['certificate']['support'].remove(0)
    must_reject(verify_ns, damaged)
    damaged = copy.deepcopy(load('resolution_K4_w4.json'))
    damaged['certificate'].pop()
    must_reject(verify_resolution, damaged)
    damaged = copy.deepcopy(load('bdd_eq_2_blocked.json'))
    damaged['root'] = 0
    must_reject(verify_bdd, damaged)
    damaged = copy.deepcopy(load('inner_product_sign_2.json'))
    damaged['matrix'][0][0] *= -1
    must_reject(verify_rank, damaged)
    output = {'status':'PASS', 'certificate_files_checked': len(checked),
              'checks':checked, 'regression':regression, 'negative_controls_rejected':5,
              'elapsed_seconds':time.perf_counter()-start,
              'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'independence_note':'Separate implementations, same authoring assistant. Not formal verification or independent expert review.'}
    (base/'verification.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n')
    print(json.dumps(output,indent=2))

if __name__ == '__main__':
    main()
