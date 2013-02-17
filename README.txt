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
the MajorityJudgement objects behave like the corresponding lists of grades assigned
to them.

So for example::

    assert list(MajorityJudgement([2,2])) == [0,1,0,1]

The MajorityJudgement object can generally be used exactly like its corresponding
list of grades.
