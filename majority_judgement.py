class MajorityJudgement:
  def __init__(self, votes):
    self.votes = list(votes)
    self.votes_remaining = sum(votes)
    self.judgement_trail = []

  def has_remaining_votes(self):
    return len(self.votes) > 0

  def __repr__(self):
    return "MajorityJudgement(%s, %s)" % (self.judgement_trail, self.votes) 

  def __eq__(self, other): return self.compare(other) == 0
  def __ne__(self, other): return self.compare(other) != 0
  def __lt__(self, other): return self.compare(other) < 0
  def __le__(self, other): return self.compare(other) <= 0
  def __gt__(self, other): return self.compare(other) > 0
  def __ge__(self, other): return self.compare(other) >= 0

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

  def __len__(self):
    return len(self.judgement_trail) + self.votes_remaining

  def __getitem__(self, i):
    if i < 0 or i >= len(self): raise IndexError("Index %d out of range [0, %d)", i, len(self))
    while i >= len(self.judgement_trail): self.pop_vote()
    return self.judgement_trail[i]

  def pop_vote(self):
    tot = 0
    for i in xrange(len(self.votes)):
      tot += self.votes[i]
      if 2 * tot >= self.votes_remaining:
        self.votes_remaining -= 1
        self.votes[i] -= 1
        while len(self.votes) > 0 and self.votes[-1] <= 0: self.votes.pop()
        self.judgement_trail.append(i)
        return i

  def __iter__(self):
    for x in self.judgement_trail: yield x
    while self.has_remaining_votes(): yield self.pop_vote()
