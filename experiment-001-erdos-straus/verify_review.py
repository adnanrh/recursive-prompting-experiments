#!/usr/bin/env python3
"""Fresh reproducibility audit of Recursive Prompting -- Experiment 001.

This is NEW review code, not the unavailable original SoulWorks script.
Python standard library only. All mathematical tests use exact integer arithmetic.
Run: python3 verify_review.py --output review_results.json

A: unreduced residual, factor-pair criterion (a*y-b)(a*z-b)=b^2.
B: reduced residual A/B, coprime divisors u,v of B with A | (u+v).
C: bounded direct y enumeration, used only for exhaustive small-n cross-checks.

These are computational checks, not proof-assistant verification or expert review.
No result here proves the universal Erdos--Straus conjecture or claims novelty.
"""
from __future__ import annotations
import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import json
from math import gcd, isqrt
from pathlib import Path
import platform
import sys


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArithmeticError(message)


@lru_cache(maxsize=None)
def trial_factors(n: int) -> tuple[tuple[int, int], ...]:
    """Exact trial division, independent of the sieve used to select primes."""
    if n < 1:
        raise ValueError('Factorization requires a positive integer')
    result = []
    divisor = 2
    while divisor * divisor <= n:
        exponent = 0
        while n % divisor == 0:
            n //= divisor
            exponent += 1
        if exponent:
            result.append((divisor, exponent))
        divisor = 3 if divisor == 2 else divisor + 2
    if n > 1:
        result.append((n, 1))
    return tuple(result)


def product_factors(n: int, x: int) -> dict[int, int]:
    result: dict[int, int] = {}
    for p, e in trial_factors(n) + trial_factors(x):
        result[p] = result.get(p, 0) + e
    return result


def generate_divisors(factors: dict[int, int], power: int = 1) -> list[int]:
    ds = [1]
    for prime, exponent in factors.items():
        old = ds[:]
        multiplier = 1
        for _ in range(exponent * power):
            multiplier *= prime
            ds.extend(d * multiplier for d in old)
    return sorted(ds)


def valid(n: int, x: int, y: int, z: int) -> bool:
    return 0 < x <= y <= z and 4*x*y*z == n*(x*y+x*z+y*z)


def solutions_a(n: int, x: int) -> list[tuple[int, int]]:
    a, b = 4*x-n, n*x
    if a <= 0:
        return []
    solutions = []
    for d in generate_divisors(product_factors(n, x), power=2):
        if d > b:
            break
        e = b*b//d
        if (b+d) % a == 0 and (b+e) % a == 0:
            y, z = (b+d)//a, (b+e)//a
            if y >= x:
                require(valid(n, x, y, z), 'Method A generated an invalid witness')
                solutions.append((y, z))
    return sorted(set(solutions))


# B uses its own factorization of the reduced denominator, not A's n*x factors.
def divisors_b(number: int) -> list[int]:
    ds = [1]
    remaining = number
    p = 2
    while p*p <= remaining:
        powers = [1]
        while remaining % p == 0:
            remaining //= p
            powers.append(powers[-1]*p)
        if len(powers) > 1:
            ds = [d*q for d in ds for q in powers]
        p = 3 if p == 2 else p+2
    if remaining > 1:
        ds += [d*remaining for d in ds]
    return sorted(ds)


def solutions_b(n: int, x: int) -> list[tuple[int, int]]:
    a, b = 4*x-n, n*x
    if a <= 0:
        return []
    common = gcd(a, b)
    a, b = a//common, b//common
    ds = divisors_b(b)
    by_residue: dict[int, list[int]] = {}
    for v in ds:
        by_residue.setdefault(v % a, []).append(v)
    result = []
    for u in ds:
        for v in by_residue.get((-u) % a, []):
            if u > v or gcd(u, v) != 1:
                continue
            h = (u+v)//a
            require((b*h) % v == 0 and (b*h) % u == 0,
                    'Method B reconstruction is nonintegral')
            y, z = b*h//v, b*h//u
            if y >= x:
                require(valid(n, x, y, z), 'Method B generated an invalid witness')
                result.append((y, z))
    return sorted(set(result))


def solutions_direct(n: int, x: int) -> list[tuple[int, int]]:
    a, b = 4*x-n, n*x
    if a <= 0:
        return []
    result = []
    # a/b=1/y+1/z and y<=z imply b/a<y<=2b/a.
    for y in range(max(x, b//a+1), (2*b)//a+1):
        denominator = a*y-b
        numerator = b*y
        if numerator % denominator == 0:
            z = numerator//denominator
            if y <= z:
                require(valid(n, x, y, z), 'Direct method generated invalid witness')
                result.append((y, z))
    return result


def primes_through(limit: int) -> list[int]:
    flags = bytearray(b'\x01')*(limit+1)
    flags[:2] = b'\x00\x00'
    for p in range(2, isqrt(limit)+1):
        if flags[p]:
            flags[p*p:limit+1:p] = b'\x00'*(((limit-p*p)//p)+1)
    return [p for p in range(2, limit+1) if flags[p]]


def certificate(n: int, x: int) -> dict:
    a, b = 4*x-n, n*x
    factors = product_factors(n, x)
    ds = generate_divisors(factors, power=2)
    target = (-b) % a
    residues = sorted({d % a for d in ds})
    candidates = []
    for d in ds:
        if d > b:
            break
        e = b*b//d
        if d % a == target and e % a == target:
            y, z = (b+d)//a, (b+e)//a
            candidates.append({'d': d, 'e': e, 'y': y, 'z': z,
                               'sorted_admissible': y >= x})
    return {'n': n, 'x': x, 'a_unreduced': a, 'b_unreduced': b,
            'b_factorization': [[p, e] for p, e in sorted(factors.items())],
            'b_squared_divisor_count': len(ds), 'all_divisors_of_b_squared': ds,
            'divisor_residues_mod_a': residues, 'required_residue': target,
            'required_residue_absent': target not in residues,
            'factor_pairs_meeting_both_congruences': candidates,
            'solutions_a': solutions_a(n, x), 'solutions_b': solutions_b(n, x)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='review_results.json')
    args = parser.parse_args()
    small_checks = 0
    for n in range(2, 201):
        for x in range(n//4+1, 3*n//4+1):
            aa, bb, cc = solutions_a(n, x), solutions_b(n, x), solutions_direct(n, x)
            require(aa == bb == cc, f'Small-case mismatch at n={n}, x={x}')
            small_checks += 1
    limit = 118801
    ps = primes_through(limit)
    require(all(trial_factors(p) == ((p, 1),) for p in ps), 'Nonprime sieve output')
    # Separate trial-division classification of every integer confirms no omissions.
    trial_ps = [n for n in range(2, limit+1) if trial_factors(n) == ((n, 1),)]
    require(ps == trial_ps, 'Sieve and trial-division prime lists disagree')
    records = []
    evaluated = 0
    max_depth, record_breakers = 0, []
    for p in ps:
        start = p//4+1
        success = None
        # This finite audit tests at most 15 choices. It is not a general solver.
        for x in range(start, min(3*p//4, start+14)+1):
            aa, bb = solutions_a(p, x), solutions_b(p, x)
            evaluated += 1
            require(aa == bb, f'Method mismatch at p={p}, x={x}')
            if aa:
                y, z = aa[0]
                depth = x-start+1
                success = {'p': p, 'first_x': x, 'choice_number': depth,
                           'witness': [x, y, z],
                           'completions_at_first_x': len(aa)}
                if depth > max_depth:
                    record_breakers.append({'p': p, 'choice_number': depth})
                    max_depth = depth
                records.append(success)
                break
        require(success is not None, f'No solution in audit cap at p={p}')
    below = [r for r in records if r['p'] < 100000]
    odd = [r for r in below if r['p'] != 2]
    require(len(below) == 9592 and len(odd) == 9591, 'Prime counts mismatch')
    fails = sum(r['choice_number'] > 1 for r in odd)
    require(fails == 606, '606 first-choice failures not reproduced')
    require(max(r['choice_number'] for r in below) == 8, 'Depth 8 not reproduced')
    above8 = [r for r in records if r['choice_number'] > 8]
    require(above8[0]['p'] == 118801 and above8[0]['choice_number'] == 15,
            '118801 depth-15 claim not reproduced')
    witnesses = [(5, 2, 4, 20), (73, 20, 292, 730),
                 (118801, 29715, 59875704, 84724121160)]
    require(all(valid(*w) for w in witnesses), 'Displayed article witness failed')
    special = [certificate(118801, x) for x in range(29701, 29716)]
    require(all(not c['solutions_a'] for c in special[:-1]), 'Failure certificate error')
    require(bool(special[-1]['solutions_a']), 'Fifteenth choice did not succeed')
    summary = {'classification': 'C: reproduction of existing results; no novelty claimed',
               'primes_below_100000': len(below), 'odd_primes_below_100000': len(odd),
               'odd_primes_failing_first_choice_below_100000': fails,
               'maximum_choices_below_100000': 8,
               'depth_histogram_below_100000': dict(sorted(Counter(r['choice_number'] for r in below).items())),
               'first_prime_requiring_more_than_eight_choices': 118801,
               'choices_at_118801': 15, 'primes_through_118801': len(ps),
               'fixed_x_checks_in_prime_scan': evaluated,
               'three_method_small_case_checks': small_checks,
               'small_case_scope': 'every n=2..200; every n//4+1 <= x <= 3*n//4',
               'methods_a_b_agree_on_full_solution_sets_for_every_checked_x': True,
               'sieve_cross_checked_by_trial_division_through': limit,
               'record_breakers_through_118801': record_breakers,
               'displayed_witnesses_verified': [list(w) for w in witnesses]}
    data = {'provenance': {'kind': 'NEW editorial-review reconstruction',
                           'original_script_or_certificates_accessed': False,
                           'original_ten_minute_runtime_verified': False,
                           'formal_proof_assistant_verification': False,
                           'independent_human_expert_review': False,
                           'python': platform.python_version(),
                           'source_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
            'summary': summary, 'n73_first_choice_certificate': certificate(73, 19),
            'n118801_certificates': special,
            'all_prime_first_success_records_through_118801': records}
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    print(f'Wrote {path} ({path.stat().st_size} bytes)')


if __name__ == '__main__':
    try:
        main()
    except (ArithmeticError, ValueError, OSError) as error:
        print(f'VERIFICATION FAILED: {error}', file=sys.stderr)
        raise SystemExit(1)
