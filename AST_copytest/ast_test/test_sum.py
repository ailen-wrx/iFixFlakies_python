import unittest
import datetime

class MyTestCase(unittest.TestCase):
    def test_something(self):
        print(datetime)
        data = [1, 2, 3]
        result = sum(data)
        self.assertEqual(result, 6)

if __name__ == '__main__':
    unittest.main()
