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
    si = iter(self)
    oi = iter(other)

    while True:
      try: x = si.next()
      except StopIteration:
        try: 
          oi.next()
          return -1
        except StopIteration:
          return 0
      try: y = oi.next()
      except StopIteration: return 1

      if x < y: return -1
      if x > y: return 1


  def each_judgement(self):
    for x in self.judgement_trail: yield x
    while len(self.votes) > 0: 
      tot = 0
      for i in xrange(len(self.votes)): # pragma: no branch
        tot += self.votes[i]
        if 2 * tot >= self.votes_remaining:
          self.votes_remaining -= 1
          self.votes[i] -= 1
          while len(self.votes) > 0 and self.votes[-1] <= 0: self.votes.pop()
          
          if len(self.judgement_trail) > 0: xv = self.judgement_trail[-1]
          else: xv = None

          if xv and xv[0] == i:
            xv[1] = xv[1] + 1
          else:
            self.judgement_trail.append([i, 1])

          yield [i, 1]
          break
