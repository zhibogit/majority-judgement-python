This is an implementation of the Majority Judgement voting procedure, as
proposed by Michel Balinski and Rida Laraki in `A theory of measuring, electing
, and ranking <http://www.pnas.org/content/104/21/8720.full>`_

It takes tallies of grades provided by voters and provides a python type to 
wrap them which is ordered according to the majority judgement order. 

For example::

    x = MajorityJudgement([5, 5])
    y = MajorityJudgement([3, 7])
    assert x < y

The first is the grade for a candidate who has received 5 votes of 0 and 5 votes
of 1. The second is a candidate with 3 votes of 0 and 7 of 1. As a result the 
majority judgement procedure ranks the first candidate as being worse than the 
second candidate.

In the event that you want more information about the details of the voting,
the MajorityJudgement objects behave like the corresponding lists of grades
assigned to them.

So for example::

    assert list(MajorityJudgement([2,2])) == [0,1,0,1]

The MajorityJudgement object can generally be used exactly like its 
corresponding list of grades. In particular it supports all the container 
methods in an efficient manner.

Internally the implementation is rather different. It is encoded as a list of 
repeating cycles. So the list

    [0, 0, 0, 1, 0, 1, 0, 1]

is internally represented as 

    [[[0], 3], [[1], 1], [[0, 1], 2]]

The representation we choose only ever builds cycles of length one or two: A 
cycle of length one is usually built when there is an unambiguous median, while
a cycle of length 2 will usually be built when the lower and upper medians are 
different (this isn't entirely true. e.g. the list of votes [1,1,1,1] will not
produce any cycles of length 2, but it's a good rule of thumb)

Rather than building the whole list and then compressing, entire cycles are 
built at once by working how large a run can be popped from the remaining votes
and popping it all at once. This means that even very large populations of 
voters may be efficiently worked with as the resulting lists are actually very
small.

The comparisons too may be performed efficiently on this compressed
representation: Equality works straightforwardly in the sense that two equal
votes will produce two equal representations. Comparisons may be performed by 
popping common prefixes first: So if two lists both start with [x, n] and [x,m]
then we may throw away min(m,n) entries immediately rather than having to 
iterate through.

It appears to be the case that all votes can be represented as a compressed 
list of this form with very few cycles. I conjecture that it can be done in 
O(log(voters)), but have not verified this. Certainly in practice it seems to 
be the case.
