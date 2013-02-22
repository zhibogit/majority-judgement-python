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

def _how_many_to_pop(preceding, votes, total):
    return 1 + min(total - 2 * preceding - 1,
                   2 * preceding + 2 * votes - total)

def _calculate_judgement_trail(tallies):
    judgement_trail = []
    tallies = list(tallies)
    tallies_remaining = sum(tallies)
    while len(tallies) > 0:
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

                    relevant_indices = [i, next_index]
                    votes_to_pop = _how_many_to_pop(preceding,
                                                    v + tallies[next_index],
                                                    tallies_remaining)
                    k = votes_to_pop / 2
                    votes_to_pop = k * 2
                else:
                    relevant_indices = [i]
                    votes_to_pop = _how_many_to_pop(preceding,
                                                    v,
                                                    tallies_remaining)
                    k = votes_to_pop

                tallies_remaining -= votes_to_pop
                for i in relevant_indices:
                    tallies[i] -= k

                while len(tallies) > 0 and tallies[-1] <= 0:
                    tallies.pop()
                r = [relevant_indices, k]
                judgement_trail.append(r)
                break
    return judgement_trail

def __append_cycle(result, h, xs,n):
    if n <= 0: return h 
    if not h:
        if len(xs) == 2:
            result.append((xs, n))
        else:
            x = xs[0]
            result.append(((x,x),n/2))
            if n % 2 != 0: h = x
    else:
        if len(xs) == 2:
            result.append(((h, xs[0]), 1))
            result.append(((h, xs), n-1))
            h = xs[1]
        else:
            x = xs[0]
            if x == h:
                result.append((xs,n+1))
            else:
                result.append(((h,x), 1))
                h = __append_cycle(result,h,xs,n-1)
    return h
                
def _tupleize_cycle_list(cycles):
    result = []
    hangover = None
    for xs, n in cycles:
        hangover = __append_cycle(result,hangover, xs, n)             

    flattened_result = []
    i = 0
    while i < len(result):
        j = i + 1
        x = result[i][0]
        n = result[i][1]
        while j < len(result) and result[j][0] == x:
            n += result[j][1]
            j += 1
        flattened_result.append(x[0])
        flattened_result.append(x[1])
        flattened_result.append(n)
        i = j

    return flattened_result, hangover

class MajorityJudgement():
    """
    Objects of type MajorityJudgement behave like a lazily evaluated frozen
    list. They may be indexed, iterated over and _compared exactly as if they
    were their list of majority judgement grades.
    """
    def __init__(self, tally):
        """
        Create a MajorityJudgement object from a tally of grades. Note that
        the votes are taken as tallies, not as a list of grades. i.e.
        [1,2,1] means that there is one vote each of grades 0 and 2 and 2 votes
        of grade 1, not that there 2 votes of grade 1 and 1 of grade 2.
        """

        for x in tally:
            if x < 0:
                raise ValueError("Tally counts may not be negative: %s" % tally)

        self._judgement_trail, self._trailing_member = _tupleize_cycle_list(_calculate_judgement_trail(tally))

    def __nonzero__(self):
        return bool(self._judgement_trail or self._trailing_member)

    def __repr__(self):
        return "MajorityJudgement(%s)" % (self._judgement_trail)

    def __eq__(self, other):
        return self._compare(other) == 0

    def __ne__(self, other):
        return self._compare(other) != 0

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
        if not self and not other:
            return 0
        if not self:
            return -1
        if not other:
            return 1

        self_list = list(self._judgement_trail)
        other_list = list(other._judgement_trail)

        self_index = 0
        other_index = 0

        while self_index < len(self_list) and other_index < len(other_list):
            if self_list[self_index] < other_list[other_index]: return -1
            if self_list[self_index] > other_list[other_index]: return 1
            if self_list[self_index+1] < other_list[other_index+1]: return -1
            if self_list[self_index+1] > other_list[other_index+1]: return 1

            m = min(self_list[self_index+2], other_list[other_index+2])

            self_list[self_index+2] -= m
            other_list[other_index+2] -= m

            if not self_list[self_index+2]: self_index += 3
            if not other_list[other_index+2]: other_index += 3


        if other_index < len(other_list): return -1
        if self_index < len(self_list): return 1

        if self._trailing_member and other._trailing_member:
            if self._trailing_member < other._trailing_member:
                return -1
            if self._trailing_member > other._trailing_member:
                return 1
            return 0
        elif self._trailing_member:
            return 1
        elif other._trailing_member:
            return -1
        else:
            return 0
