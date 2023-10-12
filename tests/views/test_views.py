import unittest
import landing_page_app
from landing_page_app.main.views import index


class TestViews(unittest.TestCase):
    def test_index(self):
        the_app = landing_page_app.create_app().test_client().get('1index')
        # pages = the_app.index()
        self.assertTrue(the_app)
        # self.assertTrue(1)

if __name__ == "__main__":
    unittest.main()
