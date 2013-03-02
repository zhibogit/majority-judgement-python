"""
Majority Judgement is a method of voting proposed by Michel Balinski
and Rida Laraki in "A theory of measuring, electing, and ranking"
(http://www.pnas.org/content/104/21/8720.full)

Members of the electorate vote by assigning grades to candidates. These grades
can be any ordinal values (numbers, "A,B,C", "Good, Bad,Terrible", etc.
All that matters is the relative ordinal positions of the grades.

In this module we assume that grades are consecutive integer values starting
from 0 as the lowest. Because all that matters is the ordering, any other
grading scheme can be trivially converted to this form.

The essential idea of majority judgement is that we sort the grades assigned to
the candidate in order of most significant to least significant. At any given
point the most significant grade of those left is the lower median of the set
(i.e. the highest grade which at least 50% of the population supports).

So for example given the grading Bad, OK, OK, Good we would convert this to the
sequence

OK, Bad, OK, Good

Another candidate might have the grading

OK, Good, OK, Good

This candidate would win because their second grading is better than the first
candidate's.

This module provides a type which wraps a tally of grades and is then ordered
in terms of the majority judgement. It may then be used to implement a voting
procedure by assigning each candidate their tally and taking the maximum.
"""

import collections
import copy


class MajorityJudgement():
    """
    Objects of type MajorityJudgement support comparison and ordering options 
    as per the ordering of the described voting algorithm. They expose no other
    operations.
    """
    def __init__(self, tally):
        """
        Create a MajorityJudgement object from a tally of grades. Note that
        the votes are taken as tallies, not as a list of grades. i.e.
        [1,2,1] means that there is one vote each of grades 0 and 2 and 2 votes
        of grade 1, not that there 2 votes of grade 1 and 1 of grade 2.
        """

        for x in tally:
            if type(x) is not int:
                raise ValueError("Tally counts must be integers: %s" % tally)
            if x < 0:
                raise ValueError("Tally counts may not be negative: %s" % tally)
        
        self.tally = tally
        self.__judgement_trail = []
        self.__hangover = -1
        self.__calculate_judgement_trail()

    def __repr__(self):
        return "MajorityJudgement(tally=%s,judgement_trail=%s)" % (self.tally, self.__judgement_trail)

    def __eq__(self, other):
        return self.__judgement_trail == other.__judgement_trail

    def __ne__(self, other):
        return self.__judgement_trail != other.__judgement_trail

    def __lt__(self, other):
        return self._compare(other) < 0

    def __le__(self, other):
        return self._compare(other) <= 0

    def __gt__(self, other):
        return self._compare(other) > 0

    def __ge__(self, other):
        return self._compare(other) >= 0

    def _compare(self, other):
        """
            Return an integer expressing the order relation between self and
            other. -1 if self < other, 0 if self == other, 1 if self > other.

            Ordering is defined to be equivalent to lexicographical ordering of
            list(self) and list(other), but may not fully evaluate the sequence
            and may require less iteration due to long stretches of common
            values.
        """
        if self is other:
            return 0
        if not self.__judgement_trail and not other.__judgement_trail:
            return 0
        if not self.__judgement_trail:
            return -1
        if not other.__judgement_trail:
            return 1

        self_stack = list(self.__judgement_trail)
        other_stack = list(other.__judgement_trail)

        si = 0
        oi = 0
        
        while si < len(self_stack) and oi < len(other_stack):
            if self_stack[si] < other_stack[oi]: return -1
            elif self_stack[si] > other_stack[oi]: return 1

            if self_stack[si+1] < other_stack[oi+1]: return -1
            elif self_stack[si+1] > other_stack[oi+1]: return 1

            m = min(self_stack[si+2], other_stack[oi+2])
            self_stack[si+2] -= m
            other_stack[oi+2] -= m

            if self_stack[si+2] == 0: si += 3
            if other_stack[oi+2] == 0: oi += 3

        if si < len(self_stack): return 1
        if oi < len(other_stack): return -1

        return 0

    def __how_many_to_pop(self, preceding, votes, total):
        return 1 + min(total - 2 * preceding - 1,
                       2 * preceding + 2 * votes - total)
   
    def __medians(self, tallies):
        tallies_remaining = sum(tallies)
        tot = 0
        for i in xrange(len(tallies)):  # pragma: no branch
            preceding = tot
            v = tallies[i]
            tot += v
            if 2 * tot >= tallies_remaining:
                if 2 * tot == tallies_remaining:
                    next_index = i+1
                    while not tallies[next_index]:
                        next_index += 1
                    return i, next_index
                else:
                    return i, i

 
    def __calculate_judgement_trail(self):
        tallies = [2 * x for x in self.tally]
        tallies_remaining = sum(tallies)
        while len(tallies) > 0:
            lm,um = self.__medians(tallies)
             
            votes_to_pop = (
                self.__how_many_to_pop(sum((tallies[i] for i in xrange(lm))),
                                       sum((tallies[i] for i in xrange(lm,um+1))),
                                       sum(tallies)))

            if lm != um:
                relevant_indices = [lm, um]
                k = votes_to_pop / 2
                votes_to_pop = k * 2
            else:
                relevant_indices = [lm]
                k = votes_to_pop

            for i in relevant_indices:
                tallies[i] -= k

            while len(tallies) > 0 and tallies[-1] <= 0:
                tallies.pop()
            self.__append(relevant_indices, k)
            break

        assert self.__hangover < 0
        self.__judgement_trail = tuple(self.__judgement_trail)

    def __append(self,xs, n):
        print self.__hangover
        if self.__hangover < 0:
            if len(xs) == 2:
                self.__simple_append(xs[0],xs[1],n)
            else:
                x = xs[0]
                if n > 1: self.__simple_append(x,x,n/2)
                if n % 2 != 0: self.__hangover = x
        else:
            # I actually haven't reasoned through this bit yet.
            # I think we can never have len(xs) == 2 here when the original
            # total passed in is even. Certainly this seems to be true 
            # empirically
            assert len(xs) == 1
            x = xs[0]
            self.__simple_append(self.__hangover, x, 1)
            n -= 1 
            if n > 1: self.__simple_append(x,x,n/2)
            if n % 2 != 0: self.__hangover = x
            else: self.__hangover = -1

    def __simple_append(self,x,y,n):
        self.__judgement_trail.append(x)
        self.__judgement_trail.append(y)
        self.__judgement_trail.append(n)
        
