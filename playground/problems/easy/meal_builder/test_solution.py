"""Runnable tests for the Meal Builder (Builder). Write solution.py first."""
import unittest

try:
    from solution import MealBuilder, Meal, BuildError
    _IMPORT_ERROR = None
except ImportError as _e:  # pragma: no cover
    _IMPORT_ERROR = _e
    MealBuilder = Meal = BuildError = None


def setUpModule():
    if _IMPORT_ERROR is not None:
        raise unittest.SkipTest(
            "Write solution.py first (see contract.py). Import failed: "
            f"{_IMPORT_ERROR}"
        )


class TestBuilder(unittest.TestCase):
    def test_full_meal(self):
        meal = (MealBuilder("Combo")
                .add_main("Burger", 5.0)
                .add_side("Fries", 2.0)
                .add_drink("Coke", 1.5)
                .build())
        self.assertEqual(meal.name, "Combo")
        self.assertEqual(meal.items, ["Burger", "Fries", "Coke"])
        self.assertAlmostEqual(meal.total_price, 8.5)
        self.assertEqual(meal.size, "regular")

    def test_chaining_returns_builder(self):
        b = MealBuilder("X")
        self.assertIs(b.add_main("M", 1.0), b)
        self.assertIs(b.add_side("S", 1.0), b)

    def test_size_optional(self):
        meal = MealBuilder("Big").add_main("Steak", 10).set_size("large").build()
        self.assertEqual(meal.size, "large")

    def test_multiple_sides(self):
        meal = (MealBuilder("Feast")
                .add_main("Pizza", 8)
                .add_side("Wings", 4)
                .add_side("Garlic Bread", 3)
                .build())
        self.assertEqual(meal.items, ["Pizza", "Wings", "Garlic Bread"])
        self.assertAlmostEqual(meal.total_price, 15)

    def test_build_requires_main(self):
        with self.assertRaises(BuildError):
            MealBuilder("Empty").add_side("Fries", 2.0).build()


if __name__ == "__main__":
    unittest.main(verbosity=2)
