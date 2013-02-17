from majorityjudgement.compare_rle import compare as compare_rle
import pytest

def run_length_compress_list(xs):
    result = []
    last_x = None
    for x in xs:
        if x == last_x:
            l = result[-1]
            l[1] = l[1] + 1
        else:
            result.append([x, 1])
            last_x = x
    return result

@pytest.mark.parametrize(("x", "y"), [
    ([1,1,1,1,5], [1,1,1,1]),
    ([1,1,1,1,5], [1,1,1,1,4]),
    ([1,2,1,2,1], [1,2,2,1,2])
])
def test_run_length_preserves_order(x, y):
    xr = iter(run_length_compress_list(x))
    yr = iter(run_length_compress_list(y))

    if x < y:
        assert compare_rle(xr, yr) < 0
    else:
        assert compare_rle(xr, yr) > 0
