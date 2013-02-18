from pushback_generator import PushbackGenerator

def compare(xi, yi):
    xi = PushbackGenerator(xi)
    yi = PushbackGenerator(yi)

    while xi.has_next() and yi.has_next():
        x, xn = xi.next()
        y, yn = yi.next()

        if x < y:
            return -1
        if y < x:
            return 1

        m = min(xn, yn)
        xn = xn - m
        yn = yn - m

        if xn: xi.push_back((x, xn))
        if yn: yi.push_back((y, yn))

    if xi.has_next(): return 1
    if yi.has_next(): return -1
    return 0
