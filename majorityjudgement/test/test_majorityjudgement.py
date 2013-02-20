from majorityjudgement import MajorityJudgement
from majorityjudgement.grading import _calculate_judgement_trail
import pytest
import re
import operator

def naive_majority_judgement(tally):
    tally = list(tally)
    result = []
    tot = sum(tally)

    while tot:
        rt = 0
        for i in xrange(len(tally)):
            rt += tally[i]
            if rt * 2 >= tot:
                tot -= 1
                tally[i] -= 1
                result.append(i)
                break

    return result
    

class TestMajorityJudgementSoundness:
    example_votes = [
        [1, 1, 1, 1, 1, 1, 1, 1],
        [1, 2, 3],
        [13],
        [1, 13, 12, 11, 1],
        [1, 1, 1, 1],
        [2, 3],
        [2, 1, 3],
        [10, 1, 10],
        [10, 0, 10],
        [1, 3, 2],
        [10],
        [9],
        [10],
        [9, 1]
    ]

    on_all_examples = pytest.mark.parametrize("x", example_votes)

    @on_all_examples
    def test_everything_makes_it_into_judgement(self,x):
        jt = _calculate_judgement_trail(x)
        assert sum(x) == sum((len(x) * n for (x, n) in jt))

    @on_all_examples
    def test_not_less_than_self(self, x):
        assert MajorityJudgement(x) >= MajorityJudgement(x)

    @on_all_examples
    def test_front_loading_moves_earlier(self, x):
        for i in xrange(1, len(x)):
            y = list(x)
            y[i] = y[i] - 1
            y[i-1] = y[i-1] + 1
            assert MajorityJudgement(y) < MajorityJudgement(x)

    @on_all_examples
    def test_equality_of_same_input(self, x):
        x = MajorityJudgement(x)
        assert x == x

    @on_all_examples
    def test_equality_of_identical_inputs(self, x):
        assert MajorityJudgement(x) == MajorityJudgement(x)

    @pytest.mark.parametrize(("x", "y"), [
        (x, y) for x in example_votes for y in example_votes if x != y
    ])
    def test_inequality_of_different_inputs(self, x, y):
        assert MajorityJudgement(x) != MajorityJudgement(y)

    @pytest.mark.parametrize(("x", "y"), [
        (x, y) for x in example_votes for y in example_votes
    ])
    def test_anti_symmetry_of__compare(self, x, y):
        assert (MajorityJudgement(x)._compare(MajorityJudgement(y)) ==
                -MajorityJudgement(y)._compare(MajorityJudgement(x)))


    @pytest.mark.parametrize(
        ("x", "y", "k"),
        [(x, y, k)
            for x in example_votes
            for y in example_votes
            if sum(x) == sum(y) and x != y
            for k in xrange(sum(x) / 2)])
    def test_can_drop_outliers(self, x, y, k):
        assert sum(x) == sum(y)
        x1 = MajorityJudgement(x)
        y1 = MajorityJudgement(y)

        def drop_outliers(l, k):
            l = list(l)
            for r in [xrange(len(l)), reversed(xrange(len(l)))]:
                k2 = k
                for i in r:
                    if l[i] >= k2:
                        l[i] = l[i] - k2
                        break
                    else:
                        k2 = k2 - l[i]
                        l[i] = 0
            return l

        x2 = MajorityJudgement(drop_outliers(x, k))
        y2 = MajorityJudgement(drop_outliers(y, k))

        if x1 <= y1:
            assert x2 <= y2
        else:
            assert y2 <= x2

    def build_single_upvote(self, k, n):
        return [k] + [0 for _ in xrange(n-1)] + [1]

    @pytest.mark.parametrize(("k", "n"), [
        (10, 1),
        (10, 5),
        (10, 3),
        (1, 1),
        (2, 10)
    ])
    def test_single_upvote_comes_last(self, k, n):
        x = MajorityJudgement(self.build_single_upvote(k, n))
        assert x._judgement_trail[-1][0][-1] == n

    @pytest.mark.parametrize(("k", "m", "n"), [
        (10, 1, 5),
        (10, 5, 6),
        (10, 3, 5),
        (1, 1, 2),
        (2, 10, 20)
    ])
    def test_single_upvote_determines_result(self, k, m, n):
        assert (MajorityJudgement(self.build_single_upvote(k, n)) >
                MajorityJudgement(self.build_single_upvote(k, m)))

    order_tests = pytest.mark.parametrize(("x", "y"), [
        ([10], [5, 5]),
        ([10], [9, 1]),
        ([9, 1], [5, 5]),
        ([1, 1, 1, 1, 1], [0, 1, 1, 1, 2]),
        ([5, 5], [10, 10])
    ])

    @pytest.mark.parametrize(("ev"), [example_votes])
    def test_sorts_like_corresponding_lists(self, ev):
        blah = [ (i, MajorityJudgement(x), 
                 naive_majority_judgement(x)) 
                 for i, x in zip(range(len(ev)),ev)]

        assert sorted(blah,key=operator.itemgetter(1)) == sorted(blah,key=operator.itemgetter(2))

    @on_all_examples
    def test_repr_does_not_error(self, x):
        x = MajorityJudgement(x)
        repr(x)

    def test_empty_behaviour(self):
        assert MajorityJudgement([]) == MajorityJudgement([])
        assert MajorityJudgement([]) < MajorityJudgement([1])
        assert MajorityJudgement([1]) > MajorityJudgement([])

    @on_all_examples
    def test_run_length_encoding(self, x):
        xj = MajorityJudgement(x)
        last_x = None
        rlel = 0
        for v in naive_majority_judgement(x):
            if last_x != v:
                last_x = v
                rlel  = rlel + 1
        assert len(list(xj._judgement_trail)) <= rlel

    def test_compresses_two_cycles(self):
        assert len(list(MajorityJudgement([10, 10])._judgement_trail)) == 1
        assert len(list(MajorityJudgement([9, 10])._judgement_trail)) == 2
        assert len(list(MajorityJudgement([10, 0, 10])._judgement_trail)) == 1
