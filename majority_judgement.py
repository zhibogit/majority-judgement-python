class MajorityJudgement:
  def __init__(self, votes):
    self.length = sum(votes)
    self.votes = list(votes)
    self.votes_remaining = sum(votes)
    self.judgement_trail = []

  def __repr__(self):
    return "MajorityJudgement(%s, %s)" % (self.judgement_trail, self.votes) 

  def __eq__(self, other): return self.compare(other) == 0
  def __ne__(self, other): return self.compare(other) != 0
  def __lt__(self, other): return self.compare(other) < 0
  def __le__(self, other): return self.compare(other) <= 0
  def __gt__(self, other): return self.compare(other) > 0
  def __ge__(self, other): return self.compare(other) >= 0

  def __len__(self):
    return self.length

  def __getitem__(self, i):
    l = len(self)
    if i < 0 and i > -l: i = i + l
    elif i < 0 or i >= l: raise IndexError("Index %d out of range [0, %d)", i, len(self))

    for x, n in self.each_judgement():  # pragma: no branch
      if i < n: return x
      i = i - n
  
  def __iter__(self):
    for (x, n) in self.each_judgement():
      for _ in xrange(n): yield x

  def compare(self, other):
    if self is other: return False
    if len(self) == 0 and len(other) == 0: return 0
    if len(self) == 0: return -1
    if len(other) == 0: return 1

    si = self.each_judgement()
    oi = other.each_judgement()

    x, xn = si.next()
    y, yn = oi.next()

    def pop_head(a,b):
      def clamp(n): 
        if n < 0: return 0
        else: return n
      c = min(a,b)
      return (clamp(a - c), clamp(b - c))

    def any_remaining(n, i):
      if n > 0: return True
      try: 
        i.next()
        return True
      except StopIteration: return False

    while True:
      if x < y: return -1
      if y < x: return 1

      xn,yn = pop_head(xn, yn)

      if xn == 0:
        try: x, xn = si.next()
        except StopIteration:
          if any_remaining(yn, oi): return -1
          else: return 0

      if yn == 0:
        try: y, yn = oi.next()
        except StopIteration: 
          if any_remaining(xn, si): return 1
          else: return 0
      
  def each_judgement(self):
    for x in self.judgement_trail: yield x
    while len(self.votes) > 0: 
      tot = 0
      for i in xrange(len(self.votes)): # pragma: no branch
        tot += self.votes[i]
        if 2 * tot >= self.votes_remaining:
          votes_to_pop = 1
          self.votes_remaining -= votes_to_pop
          self.votes[i] -= votes_to_pop

          while len(self.votes) > 0 and self.votes[-1] <= 0: self.votes.pop()
          
          if len(self.judgement_trail) > 0: xv = self.judgement_trail[-1]
          else: xv = None

          if xv and xv[0] == i:
            xv[1] = xv[1] + votes_to_pop
          else:
            self.judgement_trail.append([i, votes_to_pop])

          yield [i, 1]
          break
