import unittest

from load_test import validate_target


class SafetyTests(unittest.TestCase):
    def test_loopback_is_allowed(self):
        validate_target("http://127.0.0.1:8765/echo")

    def test_public_target_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_target("https://xuandi.org/")


if __name__ == "__main__":
    unittest.main()
