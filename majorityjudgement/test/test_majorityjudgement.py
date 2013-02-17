from majorityjudgement import MajorityJudgement
import pytest
import re


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
        [1, 3, 2],
        [10],
        [9],
        [10],
        [9, 1]
    ]

    on_all_examples = pytest.mark.parametrize("x", example_votes)

    @on_all_examples
    def test_tallies(self, x):
        tallies = [0 for _ in x]
        for i in MajorityJudgement(x):
            tallies[i] = tallies[i] + 1
        assert x == tallies

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
    def test_equals_self_when_fully_evaluated(self, x):
        x1 = MajorityJudgement(x)
        x2 = MajorityJudgement(x)
        list(x1)
        assert x1 == x2

    @on_all_examples
    def test_calling_list_twice_produces_same_result(self, x):
        x = MajorityJudgement(x)
        assert list(x) == list(x)

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

    @on_all_examples
    def test_length_agrees_with_list(self, x):
        assert len(MajorityJudgement(x)) == len(list(MajorityJudgement(x)))

    @on_all_examples
    def test_length_agrees_with_list_when_evaluated(self, x):
        x = MajorityJudgement(x)
        y = list(x)
        assert len(x) == len(y)

    @on_all_examples
    def test_correct_number(self, x):
        total = sum(x)
        assert len(list(MajorityJudgement(x))) == total

    @on_all_examples
    def test_positive_index_matches_list_index(self, x):
        y = list(MajorityJudgement(x))
        x = MajorityJudgement(x)

        for i in xrange(len(y)):
            assert x[i] == y[i]

    @on_all_examples
    def test_negative_index_matches_list_index(self, x):
        y = list(MajorityJudgement(x))
        x = MajorityJudgement(x)

        for i in xrange(len(y)):
            assert x[-i] == y[-i]

    @pytest.mark.parametrize(("x", "m"), [
        ([1, 1, 1, 1], 1),
        ([5, 1, 1, 5], 1),
        ([5, 1, 1, 6], 2),
        ([1, 1, 1, 1, 20], 4)
    ])
    def test_starts_with_median(self, x, m):
        assert MajorityJudgement(x)[0] == m

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
        x = self.build_single_upvote(k, n)
        l = list(MajorityJudgement(x))
        assert l == [0 for _ in xrange(k)] + [n]

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

    @order_tests
    def test_on_specified_pairs_unevaluated(self, x, y):
        assert MajorityJudgement(x) < MajorityJudgement(y)
        assert MajorityJudgement(y) > MajorityJudgement(x)

    @order_tests
    def test_on_specified_pairs_fully_evaluated(self, x, y):
        xe = MajorityJudgement(x)
        ye = MajorityJudgement(y)
        list(xe)
        list(ye)
        assert xe < ye
        assert ye > xe

    @pytest.mark.parametrize(("ev"), [example_votes])
    def test_sorts_like_corresponding_lists(self, ev):
        by_mj = [list(x) for x in sorted([MajorityJudgement(y) for y in ev])]
        by_list = sorted([list(MajorityJudgement(y)) for y in ev])
        assert by_mj == by_list

    @on_all_examples
    def test_repr_does_not_evaluate(self, x):
        x = MajorityJudgement(x)
        repr(x)
        assert len(x._judgement_trail) == 0

    @on_all_examples
    def test_repr_reflects_evaluation(self, x):
        x = MajorityJudgement(x)
        o = repr(x)
        list(x)
        assert repr(x) != o

    def test_empty_behaviour(self):
        assert MajorityJudgement([]) == MajorityJudgement([])
        assert MajorityJudgement([]) < MajorityJudgement([1])
        assert MajorityJudgement([1]) > MajorityJudgement([])

    def test_no_delete(self):
        x = MajorityJudgement([1, 2, 3])
        l = list(x)
        with pytest.raises(TypeError) as excinfo:
            del x[0]
        assert re.search('not support modifying', excinfo.value.message)
        assert list(x) == l

    def test_no_set(self):
        x = MajorityJudgement([1, 2, 3])
        l = list(x)
        with pytest.raises(TypeError) as excinfo:
            x[0] = 15
        assert re.search('not support modifying', excinfo.value.message)
        assert list(x) == l

    def test_index_out_of_bounds(self):
        with pytest.raises(IndexError):
            MajorityJudgement([1, 2, 3])[6]
        with pytest.raises(IndexError):
            MajorityJudgement([1, 2, 3])[-6]

    @on_all_examples
    def test_run_length_encoding(self, x):
        xj = MajorityJudgement(x)
        last_x = None
        rlel = 0
        for v in xj:
            if last_x != v:
                last_x = v
                rlel  = rlel + 1
        assert len(list(xj._each_judgement())) <= rlel

    def test_compresses_two_cycles(self):
        len(list(MajorityJudgement([10, 10])._each_judgement())) == 1
        len(list(MajorityJudgement([9, 10])._each_judgement())) == 2
