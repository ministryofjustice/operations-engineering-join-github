import unittest
import landing_page_app
# from landing_page_app.main.views import index


class TestViews(unittest.TestCase):
    def test_index(self):
        page = landing_page_app.create_app().test_client().get('index')
        self.assertEqual(page.status_code, 200)

    def test_home(self):
        page = landing_page_app.create_app().test_client().get('home')
        self.assertEqual(page.status_code, 200)

    def test_default(self):
        page = landing_page_app.create_app().test_client().get('/')
        self.assertEqual(page.status_code, 200)

    def test_join_github_info_page(self):
        page = landing_page_app.create_app().test_client().get('/join-github.html')
        self.assertEqual(page.status_code, 200)

    def test_join_github_form(self):
        page = landing_page_app.create_app().test_client().get('/join-github-form.html')
        self.assertEqual(page.status_code, 200)

    def test_thank_you(self):
        page = landing_page_app.create_app().test_client().get('/thank-you')
        self.assertEqual(page.status_code, 200)

    def test_form_error(self):
        page = landing_page_app.create_app().test_client().get('/form-error')
        self.assertEqual(page.status_code, 200)

    def test_internal_error(self):
        page = landing_page_app.create_app().test_client().get('/internal-error', data={"error_message": "some-value"})
        self.assertEqual(page.status_code, 200)


if __name__ == "__main__":
    unittest.main()
