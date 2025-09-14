from flask import Flask, jsonify, request

app = Flask(__name__)

products_list = []
sales_list = []
purchase_list = []

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
    #  products_list.append(data)
    #  return jsonify(data), 201
      return jsonify({'message': "Product added successfully!"})
  else:
    error = {"error" : "Method not allowed"}
    return jsonify(error), 405
  
app.run()