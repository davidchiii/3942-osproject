import unittest
from .. import app  # Import your Flask app


class FlaskTestCase(unittest.TestCase):
    # Set up before each test
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_unauthorized_access_to_fetch_comments(self):
        response = self.app.get("/fetch_comments")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/", response.headers["Location"])

    # Tear down after each test
    def tearDown(self):
        pass


if __name__ == "__main__":
    unittest.main()
