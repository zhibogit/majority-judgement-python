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

from pushback_generator import PushbackGenerator
import collections

class MajorityJudgement(collections.Sequence):
    """
    Objects of type MajorityJudgement behave like a lazily evaluated frozen
    list. They may be indexed, iterated over and _compared exactly as if they
    were their list of majority judgement grades.
    """
    def __init__(self, votes):
        """
        Create a MajorityJudgement object from a tally of grades. Note that
        the votes are taken as tallies, not as a list of grades. i.e.
        [1,2,1] means that there is one vote each of grades 0 and 2 and 2 votes
        of grade 1, not that there 2 votes of grade 1 and 1 of grade 2.
        """
        self._length = sum(votes)
        self._votes = list(votes)
        self._votes_remaining = sum(votes)
        self._judgement_trail = []

    def __repr__(self):
        return "MajorityJudgement(%s, %s)" % (self._judgement_trail, self._votes)

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

    def __len__(self):
        return self._length

    def __getitem__(self, i):
        if type(i) is slice:
            if i.stop <= i.start: 
                return []
            ix = 0
            result = []
            for x in self:
                if ix >= i.start and (ix - i.start) % (i.step or 1) == 0:
                    result.append(x)
                ix += 1
                if ix >= i.stop:
                    break
            return result

        if type(i) is not int:
            raise TypeError(
                "MajorityJudgement indices must be integers,"
                " not %s" % type(i).__name__)    
        l = len(self)
        if i < 0 and i > -l:
            i = i + l
        elif i < 0 or i >= l:
            raise IndexError("Index %d out of range [0, %d)", i, len(self))
        for x, n in self._each_judgement():    # pragma: no branch
            m = n * len(x)
            if i < m:
                return x[i % len(x)]
            i = i - m

    def __delitem__(self, i):
        raise TypeError(
            "MajorityJudgement objects do not support modifying"
            "the contents")

    def __setitem__(self, i, x):
        raise TypeError(
            "MajorityJudgement objects do not support modifying"
            "the contents")

    def __iter__(self):
        for (xs, n) in self._each_judgement():
            for _ in xrange(n):
                for x in xs:
                    yield x

    def __reversed__(self):
        self._force_full_evaluation()
        for (xs, n) in reversed(self._judgement_trail):
            for _ in xrange(n):
                for x in reversed(xs):
                    yield x

    def __contains__(self, x):
        if not type(x) is int: return False
        if x < 0: 
            return False
        if x < len(self._votes) and self._votes[x]:
            return True
        for (ys, n) in self._judgement_trail:
            if x in ys:
                return True
        return False
        
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
        if len(self) == 0 and len(other) == 0:
            return 0
        if len(self) == 0:
            return -1
        if len(other) == 0:
            return 1

        si = PushbackGenerator(self._each_judgement())
        oi = PushbackGenerator(other._each_judgement())

        while si.has_next() and oi.has_next():
            x, xn = si.next()
            y, yn = oi.next()
            
            m = min(xn, yn)

            if x == y:
                xn = xn - m
                yn = yn - m
                if xn: si.push_back((x, xn))
                if yn: oi.push_back((y, yn))
            elif x[:m] < y[:m]:
                return -1
            elif y[:m] < x[:m]:
                return 1
            else:
                if xn > 1: si.push_back((x, xn - 1))
                if yn > 1: oi.push_back((y, yn - 1))

                x = x[m:]
                y = y[m:]

                if x: si.push_back((x, 1))
                if y: oi.push_back((y, 1))

        if si.has_next(): return 1
        if oi.has_next(): return -1

        return 0

    def _how_many_to_pop(self, preceding, votes, total):
        return 1 + min(total - 2 * preceding - 1,
                       2 * preceding + 2 * votes - total)

    def _each_judgement(self):
        for x in self._judgement_trail:
            yield x
        while len(self._votes) > 0:
            assert sum(self._votes) == self._votes_remaining
            tot = 0
            for i in xrange(len(self._votes)):  # pragma: no branch
                preceding = tot
                v = self._votes[i]
                tot += v
                if 2 * tot >= self._votes_remaining:
                    if 2 * tot == self._votes_remaining:
                        relevant_indices = [i, i+1]
                        votes_to_pop = self._how_many_to_pop(preceding,
                                                             v + self._votes[i+1],
                                                             self._votes_remaining)
                        k = votes_to_pop / 2
                        votes_to_pop = k * 2

                        if k == 0:
                            relevant_indices = [i]
                            k = 1
                            votes_to_pop = 1
                    else:
                        relevant_indices = [i]
                        votes_to_pop = self._how_many_to_pop(preceding,
                                                             v,
                                                             self._votes_remaining)
                        k = votes_to_pop

                    self._votes_remaining -= votes_to_pop
                    for i in relevant_indices:
                        self._votes[i] -= k

                    while len(self._votes) > 0 and self._votes[-1] <= 0:
                        self._votes.pop()
                    r = [relevant_indices, k]
                    self._judgement_trail.append(r)
                    yield r
                    break

    def _force_full_evaluation(self, length=None):
        if length == None: 
            length = len(self)
        if self._votes:
            for _ in self._each_judgement(): 
                pass
