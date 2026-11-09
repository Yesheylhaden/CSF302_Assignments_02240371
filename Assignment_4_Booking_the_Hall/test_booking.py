"""Run: python3 -m unittest -v"""
import random
import unittest
from booking import (greedy_earliest_finish, greedy_highest_fee,
                     best_schedule, brute_force)

FUNCTIONS = (greedy_earliest_finish, greedy_highest_fee, best_schedule, brute_force)


class BookingTests(unittest.TestCase):
    def check_case(self, requests):
        original = list(requests)
        results = []
        for function in FUNCTIONS:
            total, chosen = function(requests)
            self.assertEqual(requests, original)
            self.assertEqual(len(chosen), len(set(chosen)))
            self.assertTrue(all(isinstance(i, int) and 0 <= i < len(requests)
                                for i in chosen))
            self.assertEqual(total, sum(requests[i][2] for i in chosen))
            for k, i in enumerate(chosen):
                for j in chosen[k + 1:]:
                    a, b = requests[i], requests[j]
                    self.assertTrue(a[1] <= b[0] or b[1] <= a[0])
            self.assertEqual(function(requests), (total, chosen))
            results.append(total)
        self.assertEqual(results[2], results[3])
        self.assertLessEqual(results[0], results[2])
        self.assertLessEqual(results[1], results[2])
        return results

    def test_500_random_cases(self):
        rng = random.Random(302)
        for case in range(500):
            requests = []
            for _ in range(rng.randint(0, 10)):
                start = rng.randint(-5, 20)
                requests.append((start, start + rng.randint(1, 10), rng.randint(0, 100)))
            with self.subTest(case=case):
                self.check_case(requests)

    def test_200_equal_fee_cases(self):
        rng = random.Random(304)
        for case in range(200):
            fee = rng.randint(1, 100)
            requests = []
            for _ in range(rng.randint(0, 10)):
                start = rng.randint(0, 20)
                requests.append((start, start + rng.randint(1, 8), fee))
            with self.subTest(case=case):
                revenue = self.check_case(requests)
                self.assertEqual(revenue[0], revenue[2])

    def test_edge_cases(self):
        cases = [[], [(9, 12, 30)], [(0, 5, 1), (1, 4, 9), (2, 3, 4)],
                 [(8, 9, 3), (0, 1, 2), (4, 5, 7)],
                 [(0, 1, 2), (1, 2, 3), (2, 3, 4)],
                 [(0, 2, 5), (0, 3, 7), (1, 3, 7)],
                 [(0, 2, 4), (2, 4, 4), (0, 4, 8)],
                 [(0, 1, 0), (1, 2, 0)], [(0, 1, 5), (0, 1, 5)]]
        for requests in cases:
            with self.subTest(requests=requests):
                self.check_case(requests)
        for function in FUNCTIONS:
            self.assertEqual(function([]), (0, []))
            self.assertEqual(function([(3, 5, 7)]), (7, [0]))

    def test_counterexamples_and_example(self):
        self.assertEqual(self.check_case([(0, 2, 3), (0, 3, 8)]), [3, 8, 8, 8])
        self.assertEqual(self.check_case([(0, 4, 7), (0, 2, 4), (2, 4, 4)]),
                         [8, 7, 8, 8])
        requests = [(9, 12, 3000), (10, 16, 8000), (13, 17, 4000),
                    (12, 14, 2500), (16, 18, 2000)]
        self.check_case(requests)
        self.assertEqual(greedy_earliest_finish(requests), (7500, [0, 3, 4]))
        self.assertEqual(best_schedule(requests), (10000, [1, 4]))

    def test_brute_force_limit(self):
        with self.assertRaises(ValueError):
            brute_force([(i, i + 1, 1) for i in range(16)])
        self.assertEqual(brute_force([(i, i + 1, 1) for i in range(15)])[0], 15)


if __name__ == '__main__':
    unittest.main()
