#!/usr/bin/env python3
# -*- coding=utf-8 -*-

from typing import List, Tuple, Dict

data: List[Tuple[Tuple, Dict]] = [
    (("W", "words"), {}),
    (("S", "sentences", "ROOT"), {}),
    (("VP1", "regular verb phrases", "VP > S|SINV|SQ"), {}),
    (
        (
            "VP2",
            "verb phrases in inverted yes/no questions or in wh-questions",
            "MD|VBZ|VBP|VBD > (SQ !< VP)",
        ),
        {},
    ),
    (
        (
            "C1",
            "regular clauses",
            (
                "S|SINV|SQ "
                "[> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < "
                "(VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])]"
            ),
        ),
        {},
    ),
    (
        (
            "C2",
            "fragment clauses",
            (
                "FRAG > ROOT !<< "
                "(S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < "
                "(VP [<# MD|VBP|VBZ|VBD | < CC < "
                "(VP <# MD|VBP|VBZ|VBD)])])"
            ),
        ),
        {},
    ),
    (
        (
            "T1",
            "regular T-units",
            "S|SBARQ|SINV|SQ > ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]",
        ),
        {},
    ),
    (
        (
            "T2",
            "fragment T-units",
            "FRAG > ROOT !<< (S|SBARQ|SINV|SQ > ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP])",
        ),
        {},
    ),
    (
        (
            "CN1",
            "complex nominals, type 1",
            "NP !> NP [<< JJ|POS|PP|S|VBG | << (NP $++ NP !$+ CC)]",
        ),
        {},
    ),
    (
        (
            "CN2",
            "complex nominals, type 2",
            "SBAR [<# WHNP | <# (IN < That|that|For|for) | <, S] & [$+ VP | > VP]",
        ),
        {},
    ),
    (("CN3", "complex nominals, type 3", "S < (VP <# VBG|TO) $+ VP"), {}),
    (
        (
            "DC",
            "dependent clauses",
            (
                "SBAR < "
                "(S|SINV|SQ "
                "[> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < "
                "(VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])])"
            ),
        ),
        {},
    ),
    (
        (
            "CT",
            "complex T-units",
            (
                "S|SBARQ|SINV|SQ [> ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]] << "
                "(SBAR < (S|SINV|SQ "
                "[> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < "
                "(VP [<# MD|VBP|VBZ|VBD | < CC < "
                "(VP <# MD|VBP|VBZ|VBD)])]))"
            ),
        ),
        {},
    ),
    (("CP", "coordinate phrases", "ADJP|ADVP|NP|VP < CC"), {}),
    (("VP", "verb phrases"), {"requirements": ["VP1", "VP2"]}),
    (("C", "clauses"), {"requirements": ["C1", "C2"]}),
    (("T", "T-units"), {"requirements": ["T1", "T2"]}),
    (("CN", "complex nominals"), {"requirements": ["CN1", "CN2", "CN3"]}),
    (("MLS", "mean length of sentence"), {"requirements": ["W", "S"]}),
    (("MLT", "mean length of T-unit"), {"requirements": ["W", "T1", "T2"]}),
    (("MLC", "mean length of clause"), {"requirements": ["W", "C1"]}),
    (("C/S", "clauses per sentence"), {"requirements": ["C1", "S"]}),
    (("VP/T", "verb phrases per T-unit"), {"requirements": ["VP1", "T1", "T2"]}),
    (("C/T", "clauses per T-unit"), {"requirements": ["C1", "T1", "T2"]}),
    (("DC/C", "dependent clauses per clause"), {"requirements": ["DC", "C1"]}),
    (("DC/T", "dependent clauses per T-unit"), {"requirements": ["DC", "T1", "T2"]}),
    (("T/S", "T-units per sentence"), {"requirements": ["T1", "T2", "S"]}),
    (("CT/T", "complex T-unit ratio"), {"requirements": ["CT", "T1", "T2"]}),
    (("CP/T", "coordinate phrases per T-unit"), {"requirements": ["CP", "T1", "T2"]}),
    (("CP/C", "coordinate phrases per clause"), {"requirements": ["CP", "C1"]}),
    (
        ("CN/T", "complex nominals per T-unit"),
        {"requirements": ["CN1", "CN2", "CN3", "T1", "T2"]},
    ),
    (("CN/C", "complex nominals per clause"), {"requirements": ["CN1", "CN2", "CN3", "C1"]}),
]
