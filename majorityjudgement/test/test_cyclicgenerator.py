from majorityjudgement.cyclicgenerator import CyclicGenerator
import pytest

@pytest.mark.parametrize("x", [
    [([1,2,3], 5)],
    [([1], 10)],
    [([1,2,3], 5), ([1], 10)],
    [([1], 10), ([1], 5)],
    [([1,2,3], 5), ([1,2,3], 5)],
])
def test_matches_list(x):
    list_directly = []
    for y, n in x:
        list_directly += y * n
    list_via_generator = []
    for y, n in CyclicGenerator(iter(x)):
        list_via_generator += [y] * n

    assert list_directly == list_via_generator
