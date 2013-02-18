class PushbackGenerator:
    def __init__(self, wrapped):
        self.wrapped = iter(wrapped)
        self.pushed_back = []

    def next(self):
        if self.pushed_back:
            return self.pushed_back.pop()
        else:
            return self.wrapped.next()

    def has_next(self):
        if self.pushed_back: 
            return True
        try:
            self.pushed_back.append(self.wrapped.next())
            return True
        except StopIteration:
            return False

    def push_back(self, x):
        self.pushed_back.append(x)
