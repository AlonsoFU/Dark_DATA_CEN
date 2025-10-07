#!/usr/bin/env python3
"""Test numbering patterns"""
import re

test_strings = [
    '7.2 Apertura',
    '7.2 15:16',
    'd.1 Origen',
    'd.1',
    '94.64',
    '94.64 15:16',
    'a. Fecha',
    '1. Descripción',
    '7. Análisis',
]

patterns = [
    (r'^([A-Z]|\d+)(\.\d+){2,}\s*', 'hierarchical_complex'),
    (r'^[A-Za-z]\.\d+(?:\s|$)', 'hierarchical_letter'),
    (r'^\d+\.\d+\s+[A-Za-z]', 'hierarchical_number'),
    (r'^\d+[\.\)\-](?!\d)\s*', 'numbered'),
    (r'^[IVX]+[\.\)]\s*', 'roman'),
    (r'^[a-z][\.\)\-](?:\s|$)', 'letter'),
]

for s in test_strings:
    print(f'Text: {s!r}')
    matches = []
    for pattern, name in patterns:
        if re.match(pattern, s):
            matches.append(name)
    if matches:
        for m in matches:
            print(f'  ✅ {m}')
    else:
        print(f'  ❌ NO MATCH')
    print()
