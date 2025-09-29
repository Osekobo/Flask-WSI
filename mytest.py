import unittest, json
from main import app

class FlaskAPITest(unittest.TestCase):
  def setUp(self):
    self.client = app.test_client()
  def test_register(self):
    data = {"name":"Test_User","email":"test@mail.com","password":"12345"}
    response = self.client.post("/api/register",json=data)
    self.assertEqual(response.status_code,201)
    self.assertIn("token",response.get_json())
    print(response.get_json()["token"])

  def test_login(self):
    data = {"email":"test@mail.com","password":"12345"}
    response = self.client.post("/api/login",json=data)
    self.assertEqual(response.status_code,200)
    self.assertIn("token",response.get_json())
    print(response.get_json()["token"])

unittest.main()