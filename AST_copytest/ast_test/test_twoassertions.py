import unittest


class TestCase2(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, True)

    def test_bad_type(self):
        data = "wrongtype"
        with self.assertRaises(TypeError):
            result = sum(data)

if __name__ == '__main__':
    unittest.main()
