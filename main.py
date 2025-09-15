from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

products_list = []
sales_list = []
purchase_list = []
sales_list = []
purchases_list = []

@app.route("/")
def home():
  res = {"Flask API Version" : "1.0"}
  return jsonify(res), 200

@app.route("/api/products", methods = ["GET", "POST"])
def products():
  if request.method == "GET":
    return jsonify(products_list), 200
  elif request.method == "POST":
    data = dict(request.get_json())
    if "name" not in data.keys()  or "buying_price" not in  data.keys() or "selling_price" not in data.keys():
      error = {"error" : "Ensure  all fields are set"} 
      return jsonify(error), 400
    else:
     products_list.append(data)
     return jsonify(data), 201
    # return jsonify({'message': "Product added successfully!"})
  else:
    error = {"error" : "Method not allowed"}
    return jsonify(error), 405
  
# sales - product_id(int), quantity(float), created_at(datetime_now)
@app.route("/api/sales", methods = ["GET", "POST"])
def sales():
  if request.method == "GET":
    return jsonify(sales_list), 200
  elif request.method == "POST":
    data = dict(request.get_json())
    if "created_at" not in data:
      data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "product_id" not in data.keys()   or "quantity" not in  data.keys():
      error = {"error" : "Ensure  all fields are set and with correct input types"} 
      return jsonify(error), 400
    else:
     sales_list.append(data)
     return jsonify(data), 201
  else:
    error = {"error" : "Method not allowed"}
    return jsonify(error), 405

# purchases - product_id(int), quantity(float), created_at(datetime_now)
@app.route("/api/purchases", methods = ["GET", "POST"])
def purchases():
  if request.method == "GET":
    return jsonify(purchases_list), 200
  elif request.method == "POST":
    data = dict(request.get_json())
    if "created_at" not in data:
      data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if "product_id" not in data.keys()   or "quantity" not in  data.keys():
      error = {"error" : "Ensure  all fields are set and with correct input types"} 
      return jsonify(error), 400
    else:
     purchases_list.append(data)
     return jsonify(data), 201
  else:
    error = {"error" : "Method not allowed"}
    return jsonify(error), 405

app.run()

# Create a Github Repo - called Flask API and Push your code.
# Rest API HTTP Rules
# 1. Have a route
# 2. Always return data as JSON / Capture as JSON
# 3. Specify the request method e.g GET, POST, PUT, DELETE, PATCH
# 4. Return status Code (used by an application that is consuming)