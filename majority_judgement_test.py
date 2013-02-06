import unittest
from majority_judgement import MajorityJudgement

class TestMajorityJudgementSoundness(unittest.TestCase):
    def setUp(self):
      pass

    def test_correct_number(self):
      def correct_number_test(x):
        total = sum(x)
        self.assertEqual(len(list(MajorityJudgement(x))), total)
      
      correct_number_test([1,1,1,1])
      correct_number_test([1,7,1,1])
      correct_number_test([10])

    def test_index_matches_list_index(self):
      def index_test(x):
        index_result = []
        for i in xrange(0, sum(x)): index_result.append(MajorityJudgement(x)[i])

        list_result = list(MajorityJudgement(x))
        self.assertEqual(index_result, list_result)

      index_test([10])
      index_test([1, 2, 3])
      index_test([1,6,1])

    def test_starts_with_median(self):
      def median_test(x, m):
        self.assertEqual(MajorityJudgement(x)[0], m)

      median_test([1,1,1,1], 1)
      median_test([5,1,1,5], 1)
      median_test([5,1,1,6], 2)
      median_test([1,1,1,1,20], 4)


if __name__ == '__main__':
    unittest.main()
