from location import app
import unittest


class FlaskTestCase(unittest.TestCase):
    def test_get(self):
        tester = app.test_client(self)
        response = tester.get('/get_location', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_post_for_correct_values(self):
        tester = app.test_client(self)
        response = tester.get('/post_location', content_type='html/text')
        self.assertEqual(response.status_code, 201)

    def test_post_for_incorrect_values(self):
        tester = app.test_client(self)
        response = tester.get('/post_location', content_type='html/text')
        self.assertEqual(response.status_code, 400)
        
    def test_get_using_postgres(self):
        tester = app.test_client(self)
        response = tester.get('/get_using_postgres', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_get_using_self(self):
        tester = app.test_client(self)
        response = tester.get('/get_using_self', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_check_coordinate_geojson(self):
        tester = app.test_client(self)
        response = tester.get('/check_coordinate_geojson', content_type='html/text')
        self.assertEqual(response.status_code, 200)


if __name__=='__main__':
    unittest.main()