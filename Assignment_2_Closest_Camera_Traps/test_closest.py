"""Run with python3 -m unittest -v."""
import random
import unittest

from closest import closest_pair, closest_pair_brute


class ClosestPairTests(unittest.TestCase):
    def check_pair(self, points, expected=None):
        brute = closest_pair_brute(points)
        fast = closest_pair(points)
        self.assertAlmostEqual(fast[0], brute[0], places=12)
        self.assertEqual(fast[1:], brute[1:])
        self.assertLess(fast[1], fast[2])
        if expected is not None:
            self.assertEqual(fast, expected)

    def test_500_random_inputs(self):
        rng = random.Random(302)
        for case in range(500):
            n = rng.randint(2, 50)
            # Alternate integers (many ties/duplicates) and continuous points.
            points = ([(rng.randint(-20, 20), rng.randint(-20, 20))
                       for _ in range(n)] if case % 2 else
                      [(rng.uniform(-100, 100), rng.uniform(-100, 100))
                       for _ in range(n)])
            with self.subTest(case=case, n=n):
                self.check_pair(points)

    def test_two_points(self):
        self.check_pair([(0, 0), (3, 4)], (5.0, 0, 1))

    def test_duplicates(self):
        self.check_pair([(4, 4), (1, 1), (1, 1), (4, 4)], (0.0, 0, 3))
        self.check_pair([(2, 2)] * 30, (0.0, 0, 1))

    def test_vertical(self):
        self.check_pair([(3, y) for y in [10, -4, 8, 7, 20]], (1.0, 2, 3))

    def test_crossing_dividing_line(self):
        self.check_pair([(-10, 20), (-0.1, 0), (0.1, 0), (10, 20)],
                        (0.2, 1, 2))

    def test_ties(self):
        self.check_pair([(1, 1), (0, 0), (0, 1), (1, 0)], (1.0, 0, 2))
        self.check_pair([(x, y) for x in range(10) for y in range(10)],
                        (1.0, 0, 1))

    def test_invalid_size(self):
        for function in (closest_pair, closest_pair_brute):
            for points in ([], [(0, 0)]):
                with self.subTest(function=function.__name__, points=points):
                    with self.assertRaises(ValueError):
                        function(points)

    def test_nonfinite_coordinates(self):
        for function in (closest_pair, closest_pair_brute):
            with self.assertRaises(ValueError):
                function([(0, 0), (float('nan'), 1)])


if __name__ == '__main__':
    unittest.main()
