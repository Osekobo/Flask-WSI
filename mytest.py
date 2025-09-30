import unittest, json
from main import app

class FlaskAPITest(unittest.TestCase):

  def setUp(self):
    self.client = app.test_client()

  def test_register(self):
    data = {"name":"Test_User","email":"test@mail.com","password":"12345"}
    response = self.client.post("/api/register",json=data)
    self.assertEqual(response.status_code, 409 or 201)
    if response.status_code == 201:
      self.assertIn("token",response.get_json())
      print(response.get_json()["token"])

  def test_login(self):
    data = {"email":"test@mail.com","password":"12345"}
    response = self.client.post("/api/login",json=data)
    self.assertEqual(response.status_code,200)
    self.assertIn("token",response.get_json())
    print(response.get_json()["token"])

  def test_products(self):     
    headers = {"Authorization" : f"Bearer {self.test_login()}"}
    response = self.client.get("/api/products",headers=headers)
    self.assertEqual(response.status_code,200)
    self.assertIsInstance(response.get_json(), list)

 
  def test_products_post(self):
      headers = {"Authorization": f"Bearer {self.test_login()}"}
      data = {"name": "Sample Product", "buying_price": 19.99, "selling_price": 29.99}
      response = self.client.post("/api/products", json=data, headers=headers)
      self.assertEqual(response.status_code, 201)
      self.assertIn("id", response.get_json())
  
  def test_purchases(self):
      headers = {"Authorization": f"Bearer {self.test_login()}"}
      response = self.client.get("/api/purchases", headers=headers)
      self.assertEqual(response.status_code, 200)
      self.assertIsInstance(response.get_json(), list)
  
  def test_purchase_post(self):
      headers = {"Authorization": f"Bearer {self.test_login()}"}
      data = {"product_id": 1, "quantity": 5}
      response = self.client.post("/api/purchases", json=data, headers=headers)
      self.assertEqual(response.status_code, 201)
      self.assertIn("id", response.get_json())
  
  def test_sales(self):
      headers = {"Authorization": f"Bearer {self.test_login()}"}
      response = self.client.get("/api/sales", headers=headers)
      self.assertEqual(response.status_code, 200)
      self.assertIsInstance(response.get_json(), list)
  
  def test_sale_post(self):
      headers = {"Authorization": f"Bearer {self.test_login()}"}
      data = {"product_id": 1, "quantity": 2}
      response = self.client.post("/api/sales", json=data, headers=headers)
      self.assertEqual(response.status_code, 201)
      self.assertIn("id", response.get_json())


unittest.main()