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

class MajorityJudgement:
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
        l = len(self)
        if i < 0 and i > -l:
            i = i + l
        elif i < 0 or i >= l:
            raise IndexError("Index %d out of range [0, %d)", i, len(self))
        for x, n in self._each_judgement():    # pragma: no branch
            if i < n:
                return x
            i = i - n

    def __delitem__(self, i):
        raise TypeError(
            "MajorityJudgement objects do not support modifying"
            "the contents")

    def __setitem__(self, i, x):
        raise TypeError(
            "MajorityJudgement objects do not support modifying"
            "the contents")

    def __iter__(self):
        for (x, n) in self._each_judgement():
            for _ in xrange(n):
                yield x

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

        si = self._each_judgement()
        oi = other._each_judgement()

        x, xn = si.next()
        y, yn = oi.next()

        while True:
            if x < y:
                return -1
            if y < x:
                return 1

            m = min(xn, yn)
            xn = xn - m
            yn = yn - m

            if xn == 0:
                try:
                    x, xn = si.next()
                except StopIteration:
                    if yn > 0:
                        return -1
                    else:
                        try:
                            oi.next()
                            return -1
                        except StopIteration:
                            return 0

            if yn == 0:
                try:
                    y, yn = oi.next()
                except StopIteration:
                    # The fact that we've got this far means that xn > 0 so
                    # there is remaining x
                    return 1

    def _how_many_to_pop(self, preceding, votes, total):
        return 1 + min(total - 2 * preceding - 1, 
                       2 * preceding + 2 * votes  - total)

    def _each_judgement(self):
        for x in self._judgement_trail:
            yield x
        while len(self._votes) > 0:
            tot = 0
            for i in xrange(len(self._votes)):  # pragma: no branch
                preceding = tot
                v = self._votes[i]
                tot += v
                if 2 * tot >= self._votes_remaining:
                    votes_to_pop = self._how_many_to_pop(preceding, 
                                                         v, 
                                                         self._votes_remaining)
                    assert votes_to_pop <= v
                    self._votes_remaining -= votes_to_pop
                    self._votes[i] -= votes_to_pop
                    while len(self._votes) > 0 and self._votes[-1] <= 0:
                        self._votes.pop()
                    r = [i, votes_to_pop]
                    self._judgement_trail.append(r)
                    yield r
                    break
