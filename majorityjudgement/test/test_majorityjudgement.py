from majorityjudgement import MajorityJudgement
import pytest
import re
import operator

def all_votes_of_size(length, total):
    if length <= 0:
        yield []
        return
    if length == 1:
        yield [total]
        return
    if total <= 0:
        yield [0 for _ in xrange(length)]
        return
    for i in xrange(total):
        x = [i]
        for xs in all_votes_of_size(length - 1, total - i):
            y = x + xs
            yield y

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
    
def seq_to_n(xs, n):
    results = [[]]
    for _ in xrange(n):
        results = [r + [x] for r in results for x in xs]
    return results

def small_variations(xs):
    for v in seq_to_n([-1,0,1], len(xs)):
        if sum(v) == 0:
            yield [x + p for (x,p) in zip(xs,v) if x + p >= 0]

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
        [9, 1],
        [11,10],
        [0,1,0],
        [0,0,1],
        [1,0,0],
    ]

    on_all_examples = pytest.mark.parametrize("x", example_votes)

    def test_input_validation_non_negative(self):
        with pytest.raises(ValueError) as exinfo:
            MajorityJudgement([-1, 2])

        assert re.search("negative", exinfo.value.message)

    def test_input_validation_integer(self):
        with pytest.raises(ValueError) as exinfo:
            MajorityJudgement([[]])
        assert re.search("integer", exinfo.value.message)

        with pytest.raises(ValueError) as exinfo:
            MajorityJudgement([-1.0])
        assert re.search("integer", exinfo.value.message)

    @on_all_examples
    def test_not_less_than_self(self, x):
        assert MajorityJudgement(x) >= MajorityJudgement(x)

    @on_all_examples
    def test_front_loading_moves_earlier(self, x):
        for i in xrange(1, len(x)):
            
            y = list(x)
            y[i] = y[i] - 1
            if y[i] < 0:
                continue
            y[i-1] = y[i-1] + 1
            assert MajorityJudgement(y) < MajorityJudgement(x)

    @on_all_examples
    def test_small_variations_order_correctly(self, x):
        xj = MajorityJudgement(x)
        xnj = naive_majority_judgement(x)
        for v in small_variations(x):
            vj = MajorityJudgement(v)
            vnj = naive_majority_judgement(v)
            if vnj < xnj: assert vj < xj
            elif vnj > xnj: assert vj > xj
            else: assert vj == xj

    @on_all_examples
    def test_equality_of_same_input(self, x):
        x = MajorityJudgement(x)
        assert x == x

    @on_all_examples
    def test_greater_equal_same_input(self,x):
        x = MajorityJudgement(x)
        assert x >= x
        
    @on_all_examples
    def test_equality_of_identical_inputs(self, x):
        assert MajorityJudgement(x) == MajorityJudgement(x)

    @on_all_examples
    def test_greater_equal_identical_inputs(self, x):
        assert MajorityJudgement(x) >= MajorityJudgement(x)

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
        ([5, 5], [10, 10]),
        ([0, 8, 4], [0,6,6]),
    ])


    @order_tests 
    def test_puts_pairs_in_correct_order(self, x, y):
        assert MajorityJudgement(x) < MajorityJudgement(y)

    @order_tests
    def test_doubling_preserves_order(self,x,y):
        x = [2 * t for t in x]
        y = [2 * t for t in y]
        
        assert MajorityJudgement(x) < MajorityJudgement(y)

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
        assert MajorityJudgement([]) >= MajorityJudgement([])
        assert MajorityJudgement([]) < MajorityJudgement([1])
        assert MajorityJudgement([1]) > MajorityJudgement([])

    @pytest.mark.parametrize(("ev"), [all_votes_of_size(3, 10),
                                      all_votes_of_size(5, 10),
                                      all_votes_of_size(7, 5),
                                      (list(all_votes_of_size(7, 5)) + list(all_votes_of_size(7, 7))),
                                      (list(all_votes_of_size(7, 5)) + list(all_votes_of_size(3, 10))),
                                      ])
    def test_sorts_all_small_examples_like_naive_version(self, ev):
        ev = [(naive_majority_judgement(x), x) for x in ev]
        ev.sort()
        for i in xrange(0, len(ev) - 1):
            assert MajorityJudgement(ev[i][1]) < MajorityJudgement(ev[i+1][1])
