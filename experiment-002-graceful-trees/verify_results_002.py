#!/usr/bin/env python3
"""Independent graceful-tree certificate verifier for Experiment 002.

Usage:
    python verify_results_002.py certificates.json

Accepted JSON: a list of certificates, a single certificate, or an object
with a `certificates` list. Each certificate has `edges` (pairs of vertex
IDs) and `labels` (mapping from vertex IDs to integers, or a list indexed
by integer vertex IDs). Optional `n` specifies the number of vertices.

This checks supplied certificates; it does NOT reproduce a search or prove
the Graceful Tree Conjecture.
"""
import argparse
import json
import sys


def verify(cert):
    if not isinstance(cert, dict):
        raise ValueError('certificate must be a JSON object')
    edges = cert.get('edges')
    labels = cert.get('labels')
    if not isinstance(edges, list) or not isinstance(labels, (list, dict)):
        raise ValueError('expected edges list and labels list/object')
    if isinstance(labels, list):
        if any(type(v) is not int for v in labels):
            raise ValueError('labels must be integers')
        vertices = set(range(len(labels)))
        lab = {i: v for i, v in enumerate(labels)}
    else:
        if any(type(v) is not int for v in labels.values()):
            raise ValueError('labels must be integers')
        vertices = set(labels)
        lab = labels
    n = len(vertices)
    if n < 1 or ('n' in cert and (type(cert['n']) is not int or cert['n'] != n)):
        raise ValueError('invalid vertex count')
    if sorted(lab.values()) != list(range(n)):
        raise ValueError('vertex labels are not a bijection onto 0..n-1')
    if len(edges) != n - 1:
        raise ValueError('tree must have exactly n-1 edges')
    parent = {v: v for v in vertices}
    def root(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    differences = []
    for edge in edges:
        if not isinstance(edge, list) or len(edge) != 2:
            raise ValueError('each edge must be a two-element JSON array')
        u, v = edge
        if isinstance(labels, list):
            if type(u) is not int or type(v) is not int:
                raise ValueError('vertex IDs must be integers for list labels')
        else:
            if not isinstance(u, str) or not isinstance(v, str):
                raise ValueError('vertex IDs must be strings for object labels')
        if u not in vertices or v not in vertices or u == v:
            raise ValueError('edge contains unknown vertex or self-loop')
        ru, rv = root(u), root(v)
        if ru == rv:
            raise ValueError('graph contains a cycle or repeated edge')
        parent[ru] = rv
        differences.append(abs(lab[u] - lab[v]))
    if len({root(v) for v in vertices}) != 1:
        raise ValueError('graph is disconnected')
    if sorted(differences) != list(range(1, n)):
        raise ValueError('edge differences are not exactly 1..n-1')
    return n


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificates', help='JSON file containing one or more certificates')
    args = parser.parse_args()
    try:
        with open(args.certificates, encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, dict) and 'certificates' in data:
            items = data['certificates']
        elif isinstance(data, list):
            items = data
        else:
            items = [data]
        if not isinstance(items, list) or not items:
            raise ValueError('no certificates supplied')
        failures = 0
        for i, cert in enumerate(items, 1):
            try:
                n = verify(cert)
                print(f'PASS certificate {i}: {n} vertices')
            except (ValueError, TypeError, KeyError) as e:
                failures += 1
                print(f'FAIL certificate {i}: {e}', file=sys.stderr)
        print(f'Checked {len(items)} certificates: {len(items)-failures} passed, {failures} failed')
        return 1 if failures else 0
    except (OSError, json.JSONDecodeError, ValueError, TypeError) as e:
        print(f'ERROR: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
