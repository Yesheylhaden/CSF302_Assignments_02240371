"""Run with: python3 -m unittest -v"""
import random
import unittest
from sorts import quicksort_basic, quicksort_improved


class SortTests(unittest.TestCase):
    def check_case(self, values):
        expected = sorted(values)
        results = []
        for name, algorithm in [('basic', quicksort_basic)] + [
            (f'improved cutoff={c}', lambda a, c=c: quicksort_improved(a, c))
            for c in (1, 4, 8, 16, 32, 64)
        ]:
            with self.subTest(algorithm=name, size=len(values)):
                data = values.copy()
                alias = data
                self.assertIsNone(algorithm(data))
                self.assertIs(data, alias)
                self.assertEqual(alias, expected)
                results.append(data)
        self.assertTrue(all(result == results[0] for result in results))

    def setUp(self):
        random.seed(302)

    def test_500_random_cases(self):
        rng = random.Random(302)
        for case in range(500):
            with self.subTest(case=case):
                self.check_case([rng.randint(-1000, 1000)
                                 for _ in range(rng.randrange(201))])

    def test_edge_cases(self):
        for data in ([], [7], [5] * 150, list(range(150)),
                     list(range(149, -1, -1)), [-8, -2, -9, -1],
                     [100, 500, 100, 500, 100], [-3, 0, 9, -3, 2]):
            with self.subTest(data=data):
                self.check_case(data)

    def test_large_improved_inputs(self):
        for data in (list(range(10000)), list(range(9999, -1, -1)),
                     [500] * 10000):
            expected = sorted(data)
            self.assertIsNone(quicksort_improved(data))
            self.assertEqual(data, expected)

    def test_invalid_cutoffs(self):
        for cutoff in (0, -1, 1.5, True):
            with self.assertRaises(ValueError):
                quicksort_improved([], cutoff)


if __name__ == '__main__':
    unittest.main()
