from flask import Flask, jsonify, request
from datetime import datetime
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import sentry_sdk
from models import db, Product, Sale, User, Purchase

app = Flask(__name__)
# Change this to a random secret key in production
app.config['JWT_SECRET_KEY'] = 'hgyutd576uyfutu'
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:12039@localhost:5432/flask_api"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


sentry_sdk.init(
    dsn="https://d094d4f6e41f019d48dc3cfd2d7f37df@o4510040510431234.ingest.us.sentry.io/4510040789811200",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)

jwt = JWTManager(app)

purchases_list=[]
sales_list=[]

@app.route("/", methods=['GET'])
def home():
    return jsonify({"Flask API Version": "1.0"}), 200


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    if "name" not in data.keys() or "email" not in data.keys() or "password" not in data.keys():
        error = {"error": "Ensure all fields are filled"}
        return jsonify(error), 400
        # Elif expected to check mail is valid/exists, password is long, fields not empty
    elif User.query.filter_by(email=data["email"]).first() is not None:
        error = {"error" : "User with that email already exists"}
        return jsonify(error), 409
    else:
        usr = User(name=data["name"], email = data["email"], password=data["password"])
        db.session.add(usr)
        db.session.commit()
        data["id"] = usr.id
        token = create_access_token(identity=data["email"])
        return jsonify({"message": "User registered successfully", "token": token}), 201

@app.route("/api/login", methods=["POST"])
def login(): 
    data = request.get_json()
    if "email" not in data.keys() or "password" not in data.keys():
        return jsonify({"error": "Ensure all fields are filled"}), 400
    else:
        usr = User.query.filter_by(email=data["email"], password=data["password"]).first()
        if usr is None:
            error = {"error": "Invalid email or password"}
            return jsonify(error), 401
        else:
            token = create_access_token(identity=data["email"])
            return jsonify({"token":token}), 200

@app.route("/api/users", methods=["GET"])
@jwt_required()
def get_users():
    users = User.query.all()
    users_list=[]
    for u in users:
      users_list.append({
          "id":u.id,
          "name":u.name,
          "email":u.email,
           "created_at": u.created_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(u, "created_at") else None
      })
    return jsonify(users_list), 200


@app.route("/api/products", methods=["GET", "POST"])
@jwt_required()
def products():
    if request.method == "GET":
        products = Product.query.all()
        products_list=[]
        for prod in products:
          data={"id":prod.id,"name":prod.name,"buying_price":prod.buying_price,"selling_price":prod.selling_price}
          products_list.append(data)
        # retriving products
        return jsonify(products_list), 200
    elif request.method == "POST":
        data = dict(request.get_json())
        if "name" not in data.keys() or "buying_price" not in data.keys() or "selling_price" not in data.keys():
            error = {"error": "Ensure  all fields are set"}
            return jsonify(error), 400
        else:
            # products_list.append(data)
            prod = Product(name=data["name"], buying_price=data["buying_price"], selling_price=data["selling_price"])
            db.session.add(prod)
            db.session.commit()
            data["id"] = prod.id
            return jsonify(data), 201
        # return jsonify({'message': "Product added successfully!"})
    else:
        error = {"error": "Method not allowed"}
        return jsonify(error), 405

# sales - product_id(int), quantity(float), created_at(datetime_now)
@app.route("/api/sales", methods=["GET", "POST"])
@jwt_required()
def sales():
    if request.method == "GET":
        return jsonify(sales_list), 200
    elif request.method == "POST":
        data = dict(request.get_json())
        if "created_at" not in data:
            data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if "product_id" not in data.keys() or "quantity" not in data.keys():
            error = {
                "error": "Ensure  all fields are set and with correct input types"}
            return jsonify(error), 400
        else:
            sales_list.append(data)
            return jsonify(data), 201
    else:
        error = {"error": "Method not allowed"}
        return jsonify(error), 405

# purchases - product_id(int), quantity(float), created_at(datetime_now)


@app.route("/api/purchases", methods=["GET", "POST"])
@jwt_required()
def purchases():
    if request.method == "GET":
        return jsonify(purchases_list), 200
    elif request.method == "POST":
        data = dict(request.get_json())
        if "created_at" not in data:
            data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if "product_id" not in data.keys() or "quantity" not in data.keys():
            error = {
                "error": "Ensure  all fields are set and with correct input types"}
            return jsonify(error), 400
        else:
            purchases_list.append(data)
            return jsonify(data), 201
    else:
        error = {"error": "Method not allowed"}
        return jsonify(error), 405


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()

# Create a Github Repo - called Flask API and Push your code.
# Rest API HTTP Rules
# 1. Have a route
# 2. Always return data as JSON / Capture as JSON
# 3. Specify the request method e.g GET, POST, PUT, DELETE, PATCH
# 4. Return status Code (used by an application that is consuming)

# JWT is JSON Web Token - Generatednin the API and sent to the client
# A  Client(web,mobile) can not access a protected route without a token
# The client stores that toejn once they login or register
# pip install flask-jwt-extended
