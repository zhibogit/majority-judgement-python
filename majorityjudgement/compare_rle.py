def compare(si, oi):
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

