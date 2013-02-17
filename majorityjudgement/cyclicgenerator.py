class CyclicGenerator:

    def __init__(self, generator):
        self.generator = generator
        self.current_cycle = None
        self.current_index = 0
        self.current_count = 0

    def next(self):
        if not self.current_cycle or self.current_count <= 0:
            (self.current_cycle, self.current_count) = self.generator.next()
            self.current_index = 0
        if len(self.current_cycle) == 1:
            result = (self.current_cycle[0], self.current_count)
            self.current_cycle = None
            return result
        if self.current_index >= len(self.current_cycle):
            self.current_index = 0
            self.current_count = self.current_count - 1
        if self.current_count <= 0:
            return self.next()
        result = self.current_cycle[self.current_index]
        self.current_index = self.current_index + 1
        return (result, 1)

    def __iter__(self):
        return self
