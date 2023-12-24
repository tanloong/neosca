#!/usr/bin/env python3

import operator

from neosca.ns_exceptions import StructureNotFoundError
from neosca.ns_sca import l2sca
from neosca.ns_sca.structure_counter import Structure, StructureCounter
from neosca.ns_tregex.tree import Tree

from .base_tmpl import BaseTmpl

# CN2
# CT
# DC


class TestL2SCA(BaseTmpl):
    def test_cp(self):  # {{{
        """
        ADJP|ADVP|NP|VP < CC
        """
        self.run_test(l2sca.CP, "(ADJP (CC))", 1)
        self.run_test(l2sca.CP, "(ADVP (CC))", 1)
        self.run_test(l2sca.CP, "(NP   (CC))", 1)
        self.run_test(l2sca.CP, "(VP   (CC))", 1)
        self.run_test(l2sca.CP, "(NULL (CC))", 0)

    # }}}
    def test_cn3(self):  # {{{
        """
        S < (VP <# VBG|TO) $+ VP
        """
        self.run_test(l2sca.CN3, "(ROOT (S (VP (VBG))) VP)", 1)
        self.run_test(l2sca.CN3, "(ROOT (S (VP (TO)))  VP)", 1)

        self.run_test(l2sca.CN3, "(ROOT (S (VP   (NULL))) VP)", 0)
        self.run_test(l2sca.CN3, "(ROOT (S (VP   (VBG)))  NULL)", 0)
        self.run_test(l2sca.CN3, "(ROOT (S (VP   (TO)))   NULL)", 0)
        self.run_test(l2sca.CN3, "(ROOT (S (NULL (VBG)))  VP)", 0)
        self.run_test(l2sca.CN3, "(ROOT (S (NULL (TO)))   VP)", 0)

    # }}}
    def test_vp1(self):  # {{{
        """
        VP > S|SINV|SQ
        """
        self.run_test(l2sca.VP1, "(S    VP)", 1)
        self.run_test(l2sca.VP1, "(SINV VP)", 1)
        self.run_test(l2sca.VP1, "(SQ   VP)", 1)
        self.run_test(l2sca.VP1, "(NULL VP)", 0)

    # }}}
    def test_vp2(self):  # {{{
        """
        MD|VBZ|VBP|VBD > (SQ !< VP)
        """
        self.run_test(l2sca.VP2, "(SQ MD)", 1)
        self.run_test(l2sca.VP2, "(SQ VBZ)", 1)
        self.run_test(l2sca.VP2, "(SQ VBP)", 1)
        self.run_test(l2sca.VP2, "(SQ VBD)", 1)

        self.run_test(l2sca.VP2, "(SQ NULL)", 0)
        self.run_test(l2sca.VP2, "(SQ VBD VP)", 0)
        self.run_test(l2sca.VP2, "(SQ VBD NULL)", 1)

    # }}}
    def test_s(self):  # {{{
        """
        ROOT !> __
        """
        self.run_test(l2sca.S, "(ROOT)", 1)
        self.run_test(l2sca.S, "(NULL)", 0)
        self.run_test(l2sca.S, "(NULL ROOT)", 0)

    # }}}
    def test_c1(self):  # {{{
        """
        S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])]
        """
        # Branch 1: S|SINV|SQ > ROOT <, (VP <# VB)
        self.run_test(l2sca.C1, "(ROOT (S    (VP   VB)))", 1)  # {{{
        self.run_test(l2sca.C1, "(ROOT (SINV (VP   VB)))", 1)
        self.run_test(l2sca.C1, "(ROOT (SQ   (VP   VB)))", 1)
        self.run_test(l2sca.C1, "(NULL (S    (VP   VB)))", 0)
        self.run_test(l2sca.C1, "(NULL (SINV (VP   VB)))", 0)
        self.run_test(l2sca.C1, "(NULL (SQ   (VP   VB)))", 0)
        self.run_test(l2sca.C1, "(ROOT (NULL (VP   VB)))", 0)
        self.run_test(l2sca.C1, "(ROOT (NULL (VP   VB)))", 0)
        self.run_test(l2sca.C1, "(ROOT (NULL (VP   VB)))", 0)
        self.run_test(l2sca.C1, "(ROOT (S    (NULL VB)))", 0)
        self.run_test(l2sca.C1, "(ROOT (SINV (NULL VB)))", 0)
        self.run_test(l2sca.C1, "(ROOT (SQ   (NULL VB)))", 0)
        self.run_test(l2sca.C1, "(ROOT (S    (VP   NULL)))", 0)
        self.run_test(l2sca.C1, "(ROOT (SINV (VP   NULL)))", 0)
        self.run_test(l2sca.C1, "(ROOT (SQ   (VP   NULL)))", 0)
        self.run_test(l2sca.C1, "(ROOT (S    FIRST_CHILD (VP   VB)))", 0)
        self.run_test(l2sca.C1, "(ROOT (SINV FIRST_CHILD (VP   VB)))", 0)
        self.run_test(l2sca.C1, "(ROOT (SQ   FIRST_CHILD (VP   VB)))", 0)

        # }}}

        # Branch 2: S|SINV|SQ <# MD|VBZ|VBP|VBD
        self.run_test(l2sca.C1, "(S    MD)", 1)  # {{{
        self.run_test(l2sca.C1, "(S    VBZ)", 1)
        self.run_test(l2sca.C1, "(S    VBP)", 1)
        self.run_test(l2sca.C1, "(S    VBD)", 1)
        self.run_test(l2sca.C1, "(SINV MD)", 1)
        self.run_test(l2sca.C1, "(SINV VBZ)", 1)
        self.run_test(l2sca.C1, "(SINV VBP)", 1)
        self.run_test(l2sca.C1, "(SINV VBD)", 1)
        self.run_test(l2sca.C1, "(SQ   MD)", 1)
        self.run_test(l2sca.C1, "(SQ   VBZ)", 1)
        self.run_test(l2sca.C1, "(SQ   VBP)", 1)
        self.run_test(l2sca.C1, "(SQ   VBD)", 1)

        self.run_test(l2sca.C1, "(S    NULL)", 0)
        self.run_test(l2sca.C1, "(SINV NULL)", 0)
        self.run_test(l2sca.C1, "(SQ   NULL)", 0)
        self.run_test(l2sca.C1, "(NULL MD)", 0)
        self.run_test(l2sca.C1, "(NULL VBZ)", 0)
        self.run_test(l2sca.C1, "(NULL VBP)", 0)
        self.run_test(l2sca.C1, "(NULL VBD)", 0)  # }}}

        # Branch 3: S|SINV|SQ < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])
        # Branch 3.1: S|SINV|SQ < (VP <# MD|VBP|VBZ|VBD)
        self.run_test(l2sca.C1, "(S    (VP (MD)))", 1)  # {{{
        self.run_test(l2sca.C1, "(S    (VP (VBP)))", 1)
        self.run_test(l2sca.C1, "(S    (VP (VBZ)))", 1)
        self.run_test(l2sca.C1, "(S    (VP (VBD)))", 1)
        self.run_test(l2sca.C1, "(SINV (VP (MD)))", 1)
        self.run_test(l2sca.C1, "(SINV (VP (VBP)))", 1)
        self.run_test(l2sca.C1, "(SINV (VP (VBZ)))", 1)
        self.run_test(l2sca.C1, "(SINV (VP (VBD)))", 1)
        self.run_test(l2sca.C1, "(SQ   (VP (MD)))", 1)
        self.run_test(l2sca.C1, "(SQ   (VP (VBP)))", 1)
        self.run_test(l2sca.C1, "(SQ   (VP (VBZ)))", 1)
        self.run_test(l2sca.C1, "(SQ   (VP (VBD)))", 1)

        self.run_test(l2sca.C1, "(NULL (VP (MD)))", 0)
        self.run_test(l2sca.C1, "(NULL (VP (VBP)))", 0)
        self.run_test(l2sca.C1, "(NULL (VP (VBZ)))", 0)
        self.run_test(l2sca.C1, "(NULL (VP (VBD)))", 0)
        self.run_test(l2sca.C1, "(NULL (VP (MD)))", 0)
        self.run_test(l2sca.C1, "(NULL (VP (VBP)))", 0)
        self.run_test(l2sca.C1, "(NULL (VP (VBZ)))", 0)
        self.run_test(l2sca.C1, "(NULL (VP (VBD)))", 0)
        self.run_test(l2sca.C1, "(NULL (VP (MD)))", 0)
        self.run_test(l2sca.C1, "(NULL (VP (VBP)))", 0)
        self.run_test(l2sca.C1, "(NULL (VP (VBZ)))", 0)
        self.run_test(l2sca.C1, "(NULL (VP (VBD)))", 0)
        self.run_test(l2sca.C1, "(S    (NULL (MD)))", 0)
        self.run_test(l2sca.C1, "(S    (NULL (VBP)))", 0)
        self.run_test(l2sca.C1, "(S    (NULL (VBZ)))", 0)
        self.run_test(l2sca.C1, "(S    (NULL (VBD)))", 0)
        self.run_test(l2sca.C1, "(SINV (NULL (MD)))", 0)
        self.run_test(l2sca.C1, "(SINV (NULL (VBP)))", 0)
        self.run_test(l2sca.C1, "(SINV (NULL (VBZ)))", 0)
        self.run_test(l2sca.C1, "(SINV (NULL (VBD)))", 0)
        self.run_test(l2sca.C1, "(SQ   (NULL (MD)))", 0)
        self.run_test(l2sca.C1, "(SQ   (NULL (VBP)))", 0)
        self.run_test(l2sca.C1, "(SQ   (NULL (VBZ)))", 0)
        self.run_test(l2sca.C1, "(SQ   (NULL (VBD)))", 0)
        self.run_test(l2sca.C1, "(S    (VP   (NULL)))", 0)
        self.run_test(l2sca.C1, "(SINV (VP   (NULL)))", 0)
        self.run_test(l2sca.C1, "(SQ   (VP   (NULL)))", 0)  # }}}

        # Branch 3.2: S|SINV|SQ < (VP < CC < (VP <# MD|VBP|VBZ|VBD))
        self.run_test(l2sca.C1, "(S    (VP CC (VP MD)))", 1)  # {{{
        self.run_test(l2sca.C1, "(S    (VP CC (VP VBP)))", 1)
        self.run_test(l2sca.C1, "(S    (VP CC (VP VBZ)))", 1)
        self.run_test(l2sca.C1, "(S    (VP CC (VP VBD)))", 1)
        self.run_test(l2sca.C1, "(SINV (VP CC (VP MD)))", 1)
        self.run_test(l2sca.C1, "(SINV (VP CC (VP VBP)))", 1)
        self.run_test(l2sca.C1, "(SINV (VP CC (VP VBZ)))", 1)
        self.run_test(l2sca.C1, "(SINV (VP CC (VP VBD)))", 1)
        self.run_test(l2sca.C1, "(SQ   (VP CC (VP MD)))", 1)
        self.run_test(l2sca.C1, "(SQ   (VP CC (VP VBP)))", 1)
        self.run_test(l2sca.C1, "(SQ   (VP CC (VP VBZ)))", 1)
        self.run_test(l2sca.C1, "(SQ   (VP CC (VP VBD)))", 1)

        self.run_test(l2sca.C1, "(NULL (VP CC (VP MD)))", 0)
        self.run_test(l2sca.C1, "(NULL (VP CC (VP VBP)))", 0)
        self.run_test(l2sca.C1, "(NULL (VP CC (VP VBZ)))", 0)
        self.run_test(l2sca.C1, "(NULL (VP CC (VP VBD)))", 0)
        self.run_test(l2sca.C1, "(NULL (VP CC (VP MD)))", 0)
        self.run_test(l2sca.C1, "(NULL (VP CC (VP VBP)))", 0)
        self.run_test(l2sca.C1, "(NULL (VP CC (VP VBZ)))", 0)
        self.run_test(l2sca.C1, "(NULL (VP CC (VP VBD)))", 0)
        self.run_test(l2sca.C1, "(NULL (VP CC (VP MD)))", 0)
        self.run_test(l2sca.C1, "(NULL (VP CC (VP VBP)))", 0)
        self.run_test(l2sca.C1, "(NULL (VP CC (VP VBZ)))", 0)
        self.run_test(l2sca.C1, "(NULL (VP CC (VP VBD)))", 0)
        self.run_test(l2sca.C1, "(S    (NULL CC (VP MD)))", 0)
        self.run_test(l2sca.C1, "(S    (NULL CC (VP VBP)))", 0)
        self.run_test(l2sca.C1, "(S    (NULL CC (VP VBZ)))", 0)
        self.run_test(l2sca.C1, "(S    (NULL CC (VP VBD)))", 0)
        self.run_test(l2sca.C1, "(SINV (NULL CC (VP MD)))", 0)
        self.run_test(l2sca.C1, "(SINV (NULL CC (VP VBP)))", 0)
        self.run_test(l2sca.C1, "(SINV (NULL CC (VP VBZ)))", 0)
        self.run_test(l2sca.C1, "(SINV (NULL CC (VP VBD)))", 0)
        self.run_test(l2sca.C1, "(SQ   (NULL CC (VP MD)))", 0)
        self.run_test(l2sca.C1, "(SQ   (NULL CC (VP VBP)))", 0)
        self.run_test(l2sca.C1, "(SQ   (NULL CC (VP VBZ)))", 0)
        self.run_test(l2sca.C1, "(SQ   (NULL CC (VP VBD)))", 0)
        self.run_test(l2sca.C1, "(S    (VP NULL (VP MD)))", 0)
        self.run_test(l2sca.C1, "(S    (VP NULL (VP VBP)))", 0)
        self.run_test(l2sca.C1, "(S    (VP NULL (VP VBZ)))", 0)
        self.run_test(l2sca.C1, "(S    (VP NULL (VP VBD)))", 0)
        self.run_test(l2sca.C1, "(SINV (VP NULL (VP MD)))", 0)
        self.run_test(l2sca.C1, "(SINV (VP NULL (VP VBP)))", 0)
        self.run_test(l2sca.C1, "(SINV (VP NULL (VP VBZ)))", 0)
        self.run_test(l2sca.C1, "(SINV (VP NULL (VP VBD)))", 0)
        self.run_test(l2sca.C1, "(SQ   (VP NULL (VP MD)))", 0)
        self.run_test(l2sca.C1, "(SQ   (VP NULL (VP VBP)))", 0)
        self.run_test(l2sca.C1, "(SQ   (VP NULL (VP VBZ)))", 0)
        self.run_test(l2sca.C1, "(SQ   (VP NULL (VP VBD)))", 0)
        self.run_test(l2sca.C1, "(S    (VP CC (NULL MD)))", 0)
        self.run_test(l2sca.C1, "(S    (VP CC (NULL VBP)))", 0)
        self.run_test(l2sca.C1, "(S    (VP CC (NULL VBZ)))", 0)
        self.run_test(l2sca.C1, "(S    (VP CC (NULL VBD)))", 0)
        self.run_test(l2sca.C1, "(SINV (VP CC (NULL MD)))", 0)
        self.run_test(l2sca.C1, "(SINV (VP CC (NULL VBP)))", 0)
        self.run_test(l2sca.C1, "(SINV (VP CC (NULL VBZ)))", 0)
        self.run_test(l2sca.C1, "(SINV (VP CC (NULL VBD)))", 0)
        self.run_test(l2sca.C1, "(SQ   (VP CC (NULL MD)))", 0)
        self.run_test(l2sca.C1, "(SQ   (VP CC (NULL VBP)))", 0)
        self.run_test(l2sca.C1, "(SQ   (VP CC (NULL VBZ)))", 0)
        self.run_test(l2sca.C1, "(SQ   (VP CC (NULL VBD)))", 0)
        self.run_test(l2sca.C1, "(S    (VP CC (VP NULL)))", 0)
        self.run_test(l2sca.C1, "(S    (VP CC (VP NULL)))", 0)
        self.run_test(l2sca.C1, "(S    (VP CC (VP NULL)))", 0)
        self.run_test(l2sca.C1, "(S    (VP CC (VP NULL)))", 0)
        self.run_test(l2sca.C1, "(SINV (VP CC (VP NULL)))", 0)
        self.run_test(l2sca.C1, "(SINV (VP CC (VP NULL)))", 0)
        self.run_test(l2sca.C1, "(SINV (VP CC (VP NULL)))", 0)
        self.run_test(l2sca.C1, "(SINV (VP CC (VP NULL)))", 0)
        self.run_test(l2sca.C1, "(SQ   (VP CC (VP NULL)))", 0)
        self.run_test(l2sca.C1, "(SQ   (VP CC (VP NULL)))", 0)
        self.run_test(l2sca.C1, "(SQ   (VP CC (VP NULL)))", 0)
        self.run_test(l2sca.C1, "(SQ   (VP CC (VP NULL)))", 0)  # }}}

    # }}}
    def test_c2(self):  # {{{
        """
        FRAG > ROOT !<< (S|SINV|SQ [> ROOT <, (VP <# VB) | <# MD|VBZ|VBP|VBD | < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])])
        """
        self.run_test(l2sca.C2, "(ROOT FRAG)", 1)
        # Branch 1: FRAG > ROOT !<< (S|SINV|SQ > ROOT <, (VP <# VB))
        # Seems that this branch will never be reached. A FRAG dominated by
        # ROOT won't dominate a S|SINV|SQ that is also dominated by the same
        # ROOT.
        # Branch 2: FRAG > ROOT !<< (S|SINV|SQ <# MD|VBZ|VBP|VBD){{{
        self.run_test(l2sca.C2, "(ROOT (FRAG       (S    MD)))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (NULL (S    MD))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG       (SINV MD)))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (NULL (SINV MD))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG       (SQ   MD)))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (NULL (SQ   MD))))", 0)  # }}}
        # Branch 3: FRAG > ROOT !<< (S|SINV|SQ < (VP [<# MD|VBP|VBZ|VBD | < CC < (VP <# MD|VBP|VBZ|VBD)])){{{
        # Branch 3.1: FRAG > ROOT !<< (S|SINV|SQ < (VP <# MD|VBP|VBZ|VBD))
        self.run_test(l2sca.C2, "(ROOT (FRAG (S    (VP MD))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (S    (VP VBP))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (S    (VP VBZ))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (S    (VP VBD))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (SINV (VP MD))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (SINV (VP VBP))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (SINV (VP VBZ))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (SINV (VP VBD))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (SQ   (VP MD))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (SQ   (VP VBP))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (SQ   (VP VBZ))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (SQ   (VP VBD))))", 0)
        # Branch 3.2: FRAG > ROOT !<< (S|SINV|SQ < (VP < CC < (VP <# MD|VBP|VBZ|VBD)))
        self.run_test(l2sca.C2, "(ROOT (FRAG (S    (VP CC (VP MD)))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (S    (VP CC (VP VBP)))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (S    (VP CC (VP VBZ)))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (S    (VP CC (VP VBD)))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (SINV (VP CC (VP MD)))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (SINV (VP CC (VP VBP)))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (SINV (VP CC (VP VBZ)))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (SINV (VP CC (VP VBD)))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (SQ   (VP CC (VP MD)))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (SQ   (VP CC (VP VBP)))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (SQ   (VP CC (VP VBZ)))))", 0)
        self.run_test(l2sca.C2, "(ROOT (FRAG (SQ   (VP CC (VP VBD)))))", 0)  # }}}

    # }}}
    def test_t1(self):  # {{{
        """
        S|SBARQ|SINV|SQ > ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]
        """
        # Branch 1: S|SBARQ|SINV|SQ > ROOT
        self.run_test(l2sca.T1, "(ROOT S)", 1)
        self.run_test(l2sca.T1, "(ROOT SBARQ)", 1)
        self.run_test(l2sca.T1, "(ROOT SINV)", 1)
        self.run_test(l2sca.T1, "(ROOT SQ)", 1)
        self.run_test(l2sca.T1, "(ROOT NULL)", 0)
        # Branch 2: S|SBARQ|SINV|SQ [$-- S|SBARQ|SINV|SQ !>> SBAR|VP]
        self.run_test(l2sca.T1, "(NULL S     (S     NULL))", 1)
        self.run_test(l2sca.T1, "(NULL S     (SBARQ NULL))", 1)
        self.run_test(l2sca.T1, "(NULL S     (SINV  NULL))", 1)
        self.run_test(l2sca.T1, "(NULL S     (SQ    NULL))", 1)
        self.run_test(l2sca.T1, "(NULL SBARQ (S     NULL))", 1)
        self.run_test(l2sca.T1, "(NULL SBARQ (SBARQ NULL))", 1)
        self.run_test(l2sca.T1, "(NULL SBARQ (SINV  NULL))", 1)
        self.run_test(l2sca.T1, "(NULL SBARQ (SQ    NULL))", 1)
        self.run_test(l2sca.T1, "(NULL SINV  (S     NULL))", 1)
        self.run_test(l2sca.T1, "(NULL SINV  (SBARQ NULL))", 1)
        self.run_test(l2sca.T1, "(NULL SINV  (SINV  NULL))", 1)
        self.run_test(l2sca.T1, "(NULL SINV  (SQ    NULL))", 1)
        self.run_test(l2sca.T1, "(NULL SQ    (S     NULL))", 1)
        self.run_test(l2sca.T1, "(NULL SQ    (SBARQ NULL))", 1)
        self.run_test(l2sca.T1, "(NULL SQ    (SINV  NULL))", 1)
        self.run_test(l2sca.T1, "(NULL SQ    (SQ    NULL))", 1)

        self.run_test(l2sca.T1, "(SBAR S     S)", 0)
        self.run_test(l2sca.T1, "(SBAR S     SBARQ)", 0)
        self.run_test(l2sca.T1, "(SBAR S     SINV)", 0)
        self.run_test(l2sca.T1, "(SBAR S     SQ)", 0)
        self.run_test(l2sca.T1, "(SBAR SBARQ S)", 0)
        self.run_test(l2sca.T1, "(SBAR SBARQ SBARQ)", 0)
        self.run_test(l2sca.T1, "(SBAR SBARQ SINV)", 0)
        self.run_test(l2sca.T1, "(SBAR SBARQ SQ)", 0)
        self.run_test(l2sca.T1, "(SBAR SINV  S)", 0)
        self.run_test(l2sca.T1, "(SBAR SINV  SBARQ)", 0)
        self.run_test(l2sca.T1, "(SBAR SINV  SINV)", 0)
        self.run_test(l2sca.T1, "(SBAR SINV  SQ)", 0)
        self.run_test(l2sca.T1, "(SBAR SQ    S)", 0)
        self.run_test(l2sca.T1, "(SBAR SQ    SBARQ)", 0)
        self.run_test(l2sca.T1, "(SBAR SQ    SINV)", 0)
        self.run_test(l2sca.T1, "(SBAR SQ    SQ)", 0)
        self.run_test(l2sca.T1, "(VP S     S)", 0)
        self.run_test(l2sca.T1, "(VP S     SBARQ)", 0)
        self.run_test(l2sca.T1, "(VP S     SINV)", 0)
        self.run_test(l2sca.T1, "(VP S     SQ)", 0)
        self.run_test(l2sca.T1, "(VP SBARQ S)", 0)
        self.run_test(l2sca.T1, "(VP SBARQ SBARQ)", 0)
        self.run_test(l2sca.T1, "(VP SBARQ SINV)", 0)
        self.run_test(l2sca.T1, "(VP SBARQ SQ)", 0)
        self.run_test(l2sca.T1, "(VP SINV  S)", 0)
        self.run_test(l2sca.T1, "(VP SINV  SBARQ)", 0)
        self.run_test(l2sca.T1, "(VP SINV  SINV)", 0)
        self.run_test(l2sca.T1, "(VP SINV  SQ)", 0)
        self.run_test(l2sca.T1, "(VP SQ    S)", 0)
        self.run_test(l2sca.T1, "(VP SQ    SBARQ)", 0)
        self.run_test(l2sca.T1, "(VP SQ    SINV)", 0)
        self.run_test(l2sca.T1, "(VP SQ    SQ)", 0)

        self.run_test(l2sca.T1, "(NULL (SBAR S     S))", 0)
        self.run_test(l2sca.T1, "(NULL (SBAR S     SBARQ))", 0)
        self.run_test(l2sca.T1, "(NULL (SBAR S     SINV))", 0)
        self.run_test(l2sca.T1, "(NULL (SBAR S     SQ))", 0)
        self.run_test(l2sca.T1, "(NULL (SBAR SBARQ S))", 0)
        self.run_test(l2sca.T1, "(NULL (SBAR SBARQ SBARQ))", 0)
        self.run_test(l2sca.T1, "(NULL (SBAR SBARQ SINV))", 0)
        self.run_test(l2sca.T1, "(NULL (SBAR SBARQ SQ))", 0)
        self.run_test(l2sca.T1, "(NULL (SBAR SINV  S))", 0)
        self.run_test(l2sca.T1, "(NULL (SBAR SINV  SBARQ))", 0)
        self.run_test(l2sca.T1, "(NULL (SBAR SINV  SINV))", 0)
        self.run_test(l2sca.T1, "(NULL (SBAR SINV  SQ))", 0)
        self.run_test(l2sca.T1, "(NULL (SBAR SQ    S))", 0)
        self.run_test(l2sca.T1, "(NULL (SBAR SQ    SBARQ))", 0)
        self.run_test(l2sca.T1, "(NULL (SBAR SQ    SINV))", 0)
        self.run_test(l2sca.T1, "(NULL (SBAR SQ    SQ))", 0)
        self.run_test(l2sca.T1, "(NULL (VP S     S))", 0)
        self.run_test(l2sca.T1, "(NULL (VP S     SBARQ))", 0)
        self.run_test(l2sca.T1, "(NULL (VP S     SINV))", 0)
        self.run_test(l2sca.T1, "(NULL (VP S     SQ))", 0)
        self.run_test(l2sca.T1, "(NULL (VP SBARQ S))", 0)
        self.run_test(l2sca.T1, "(NULL (VP SBARQ SBARQ))", 0)
        self.run_test(l2sca.T1, "(NULL (VP SBARQ SINV))", 0)
        self.run_test(l2sca.T1, "(NULL (VP SBARQ SQ))", 0)
        self.run_test(l2sca.T1, "(NULL (VP SINV  S))", 0)
        self.run_test(l2sca.T1, "(NULL (VP SINV  SBARQ))", 0)
        self.run_test(l2sca.T1, "(NULL (VP SINV  SINV))", 0)
        self.run_test(l2sca.T1, "(NULL (VP SINV  SQ))", 0)
        self.run_test(l2sca.T1, "(NULL (VP SQ    S))", 0)
        self.run_test(l2sca.T1, "(NULL (VP SQ    SBARQ))", 0)
        self.run_test(l2sca.T1, "(NULL (VP SQ    SINV))", 0)
        self.run_test(l2sca.T1, "(NULL (VP SQ    SQ))", 0)

    # }}}
    def test_t2(self):  # {{{
        """
        FRAG > ROOT !<< (S|SBARQ|SINV|SQ > ROOT | [$-- S|SBARQ|SINV|SQ !>> SBAR|VP])
        """
        # Branch 1: FRAG > ROOT !<< (S|SBARQ|SINV|SQ > ROOT)
        # Seems won't reach, for similar reason as C2 Branch1.
        # Branch 2: FRAG > ROOT !<< (S|SBARQ|SINV|SQ [$-- S|SBARQ|SINV|SQ !>> SBAR|VP])
        self.run_test(l2sca.T2, "(ROOT FRAG)", 1)

        self.run_test(l2sca.T2, "(ROOT (FRAG (SBAR S     S)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (SBAR S     SBARQ)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (SBAR S     SINV)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (SBAR S     SQ)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (SBAR SBARQ S)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (SBAR SBARQ SBARQ)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (SBAR SBARQ SINV)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (SBAR SBARQ SQ)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (SBAR SINV  S)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (SBAR SINV  SBARQ)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (SBAR SINV  SINV)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (SBAR SINV  SQ)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (SBAR SQ    S)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (SBAR SQ    SBARQ)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (SBAR SQ    SINV)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (SBAR SQ    SQ)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (VP S     S)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (VP S     SBARQ)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (VP S     SINV)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (VP S     SQ)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (VP SBARQ S)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (VP SBARQ SBARQ)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (VP SBARQ SINV)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (VP SBARQ SQ)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (VP SINV  S)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (VP SINV  SBARQ)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (VP SINV  SINV)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (VP SINV  SQ)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (VP SQ    S)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (VP SQ    SBARQ)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (VP SQ    SINV)))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (VP SQ    SQ)))", 1)

        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (SBAR S     S))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (SBAR S     SBARQ))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (SBAR S     SINV))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (SBAR S     SQ))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (SBAR SBARQ S))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (SBAR SBARQ SBARQ))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (SBAR SBARQ SINV))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (SBAR SBARQ SQ))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (SBAR SINV  S))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (SBAR SINV  SBARQ))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (SBAR SINV  SINV))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (SBAR SINV  SQ))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (SBAR SQ    S))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (SBAR SQ    SBARQ))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (SBAR SQ    SINV))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (SBAR SQ    SQ))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (VP S     S))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (VP S     SBARQ))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (VP S     SINV))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (VP S     SQ))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (VP SBARQ S))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (VP SBARQ SBARQ))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (VP SBARQ SINV))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (VP SBARQ SQ))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (VP SINV  S))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (VP SINV  SBARQ))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (VP SINV  SINV))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (VP SINV  SQ))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (VP SQ    S))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (VP SQ    SBARQ))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (VP SQ    SINV))))", 1)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP (VP SQ    SQ))))", 1)

        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP S     S)))", 0)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP S     SBARQ)))", 0)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP S     SINV)))", 0)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP S     SQ)))", 0)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP SBARQ S)))", 0)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP SBARQ SBARQ)))", 0)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP SBARQ SINV)))", 0)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP SBARQ SQ)))", 0)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP SINV  S)))", 0)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP SINV  SBARQ)))", 0)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP SINV  SINV)))", 0)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP SINV  SQ)))", 0)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP SQ    S)))", 0)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP SQ    SBARQ)))", 0)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP SQ    SINV)))", 0)
        self.run_test(l2sca.T2, "(ROOT (FRAG (NOT_SBAR_VP SQ    SQ)))", 0)

    # }}}
    def test_cn1(self):# {{{
        """
        NP !> NP [<< JJ|POS|PP|S|VBG | << (NP $++ NP !$+ CC)]
        """
        self.run_test(l2sca.CN1, "(NP NP)", 0)

        # Branch 1: NP !> NP << JJ|POS|PP|S|VBG
        self.run_test(l2sca.CN1, "(NOT_NP (NP JJ))", 1)
        self.run_test(l2sca.CN1, "(NOT_NP (NP POS))", 1)
        self.run_test(l2sca.CN1, "(NOT_NP (NP PP))", 1)
        self.run_test(l2sca.CN1, "(NOT_NP (NP S))", 1)
        self.run_test(l2sca.CN1, "(NOT_NP (NP VBG))", 1)
        self.run_test(l2sca.CN1, "(NOT_NP (NP NOT_JJ_POS_PP_S_VBG))", 0)

        self.run_test(l2sca.CN1, "(NOT_NP (NP (NOT_JJ_POS_PP_S_VBG JJ)))", 1)
        self.run_test(l2sca.CN1, "(NOT_NP (NP (NOT_JJ_POS_PP_S_VBG POS)))", 1)
        self.run_test(l2sca.CN1, "(NOT_NP (NP (NOT_JJ_POS_PP_S_VBG PP)))", 1)
        self.run_test(l2sca.CN1, "(NOT_NP (NP (NOT_JJ_POS_PP_S_VBG S)))", 1)
        self.run_test(l2sca.CN1, "(NOT_NP (NP (NOT_JJ_POS_PP_S_VBG VBG)))", 1)
        # Branch 2: NP !> NP << (NP $++ NP !$+ CC)
        self.run_test(l2sca.CN1, "(NOT_NP (NP NP NOT_CC NP))", 1)
        self.run_test(l2sca.CN1, "(NOT_NP (NP (NOT_NP NP NOT_CC NP)))", 1)

        self.run_test(l2sca.CN1, "(NOT_NP (NP NP CC NP))", 0)
        self.run_test(l2sca.CN1, "(NOT_NP (NP (NOT_NP NP CC NP)))", 0)
# }}}
    def test_cn2(self):
        """
        SBAR [<# WHNP | <# (IN < That|that|For|for) | <, S] & [$+ VP | > VP]
        """

    def run_test(self, searcher: l2sca.Abstract_Searcher, tree_str: str, expected_matches: int):
        tree = next(Tree.fromstring(tree_str))
        self.assertEqual(len(list(searcher.searchNodeIterator(tree))), expected_matches)
