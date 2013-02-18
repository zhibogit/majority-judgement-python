from majorityjudgement.pushback_generator import PushbackGenerator

def test_empty_has_no_next():
    assert not PushbackGenerator([]).has_next()

def test_non_empty_has_next():
    assert PushbackGenerator([1]).has_next()

def test_has_next_after_push_back():
    x = PushbackGenerator([])
    x.push_back(1)
    assert x.has_next()

def test_pushing_back_gives_results_in_lifo():
    x = PushbackGenerator([])
    x.push_back(1)
    x.push_back(2)
    assert x.next() == 2
    assert x.next() == 1
