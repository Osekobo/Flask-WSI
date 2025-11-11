from flask import Flask, jsonify, request
from datetime import datetime
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import sentry_sdk
from models import db, Product, Sale, User, Purchase, SalesDetails
from sqlalchemy import func
# from app import app, db
from flask_cors import CORS
from collections import defaultdict

app = Flask(__name__)
CORS(app)
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


@app.route("/", methods=['GET'])
def home():
    return jsonify({"Flask API Version": "1.0"}), 200


@app.route("/api/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    if request.method == "GET":
        remaining_stock_query = (
            db.session.query(
                Product.id,
                Product.name,
                (func.coalesce(func.sum(Purchase.quantity), 0)
                 - func.coalesce(func.sum(Sale.quantity), 0)).label("remaining_stock")
            )
            .outerjoin(Purchase, Product.id == Purchase.product_id)
            .outerjoin(Sale, Product.id == Sale.product_id)
            .group_by(Product.id, Product.name)
        )
        results = remaining_stock_query.all()
        print("---------------", results)
        data = []
        labels = []
        for r in results:
            data.append(r.remaining_stock)
            labels.append(r.name)
        return jsonify({"data": data, "labels": labels}), 200
    else:
        error = {"error": "Method not allowed"}
        return jsonify(error), 405


@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    if "name" not in data.keys() or "email" not in data.keys() or "password" not in data.keys():
        error = {"error": "Ensure all fields are filled"}
        return jsonify(error), 400
        # Elif expected to check mail is valid/exists, password is long, fields not empty
    elif User.query.filter_by(email=data["email"]).first() is not None:
        error = {"error": "User with that email already exists"}
        return jsonify(error), 409
    else:
        usr = User(name=data["name"], email=data["email"],
                   password=data["password"])
        db.session.add(usr)
        db.session.commit()
        data["id"] = usr.id
        token = create_access_token(identity=data["email"])
        return jsonify({"message": "User registered successfully", "token": token}), 201


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    if "email" not in data.keys() or "password" not in data.keys():
        error = {"error": "Ensure all fields are filled"}
        return jsonify(error), 400
    else:
        usr = User.query.filter_by(
            email=data["email"], password=data["password"]).first()
        if usr is None:
            error = {"error": "Invalid email or password"}
            return jsonify(error), 401
        else:
            token = create_access_token(identity=data["email"])
            return jsonify({"token": token}), 200


@app.route("/api/users", methods=["GET"])
@jwt_required()
def get_users():
    users = User.query.all()
    users_list = []
    for u in users:
        users_list.append({
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "created_at": u.created_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(u, "created_at") else None
        })
    return jsonify(users_list), 200


@app.route("/api/products", methods=["GET", "POST"])
@jwt_required()
def products():
    if request.method == "GET":
        products = Product.query.all()
        products_list = []
        for prod in products:
            data = {"id": prod.id, "name": prod.name,
                    "buying_price": prod.buying_price, "selling_price": prod.selling_price}
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
            prod = Product(
                name=data["name"], buying_price=data["buying_price"], selling_price=data["selling_price"])
            db.session.add(prod)
            db.session.commit()
            data["id"] = prod.id
            return jsonify(data), 201
        # return jsonify({'message': "Product added successfully!"})
    else:
        error = {"error": "Method not allowed"}
        return jsonify(error), 405


@app.route("/api/sales", methods=["GET", "POST"])
@jwt_required()
def sales():
    if request.method == "GET":
        results = (
            db.session.query(Sale, SalesDetails, Product)
            .join(SalesDetails, SalesDetails.sale_id == Sale.id)
            .join(Product, Product.id == SalesDetails.product_id)
            .order_by(Sale.created_at.desc())
            .all()
        )
        # group result by sale
        sales_group = defaultdict(list)
        for sale, detail, product in results:
            sales_group[sale.id].append((sale, detail, product))
        result = [
            {
                "sale_id": sale.id,
                "created_at": sale.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "items": [
                    {
                        "product_id": product.id,
                        "product_name": product.name,
                        "quantity": detail.quantity
                    }
                    for _, detail, product in grouped
                ]
            }
            for sale_id, grouped in sales_group.items()
            for sale, _, _ in [grouped[0]]
        ]
        print("-----------------------------------", sales_group)
        return jsonify(result), 200
    elif request.method == "POST":
        try:
            data = request.get_json()
            sales_data = data.get("sales", [])

            # Validate list content
            if not sales_data or not isinstance(sales_data, list):
                return jsonify({"error": "Request must include a 'sales' list"}), 400

            created_sales = []
            for sale_item in sales_data:
                product_id = sale_item.get("product_id")
                quantity = sale_item.get("quantity")

                if not product_id or not quantity:
                    return jsonify({"error": "Each sale must include product_id and quantity"}), 400

                sale = Sale(
                    product_id=product_id,
                    quantity=quantity
                )
                db.session.add(sale)
                db.session.flush()  # get sale.id before commit

                created_sales.append({
                    "id": sale.id,
                    "product_id": sale.product_id,
                    "quantity": sale.quantity,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })

            db.session.commit()
            return jsonify({"message": "Sales added successfully", "sales": created_sales}), 201

        except Exception as e:
            db.session.rollback()
        return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Method not allowed"}), 405

    #     data = dict(request.get_json())
    #     if "created_at" not in data:
    #         data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #     if "product_id" not in data.keys() or "quantity" not in data.keys():
    #         error = {
    #             "error": "Ensure all fields are set and with correct input types"}
    #         return jsonify(error), 400
    #     else:
    #         try:
    #             sale = Sale(
    #                 product_id=data["product_id"],
    #                 quantity=data["quantity"]
    #             )
    #             db.session.add(sale)
    #             db.session.commit()
    #             data["id"] = sale.id
    #             data["updated_at"] = sale.updated_at.strftime(
    #                 "%Y-%m-%d %H:%M:%S")
    #             return jsonify(data), 201
    #         except Exception as e:
    #             db.session.rollback()
    #             return jsonify({"error": str(e)}), 500
    # else:
    #     error = {"error": "Method not allowed"}
    #     return jsonify(error), 405


@app.route("/api/purchases", methods=["GET", "POST"])
@jwt_required()  # enable when you're ready for token protection
def purchases():
    if request.method == "GET":
        purchases = Purchase.query.all()
        purchases_list = []
        for p in purchases:
            purchases_list.append({
                "id": p.id,
                "product_id": p.product_id,
                "quantity": p.quantity,
                "created_at": p.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": p.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            })
        return jsonify(purchases_list), 200
    elif request.method == "POST":
        data = dict(request.get_json())
        if "created_at" not in data:
            data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if "product_id" not in data.keys() or "quantity" not in data.keys():
            error = {
                "error": "Ensure all fields are set and with correct input types"}
            return jsonify(error), 400
        else:
            try:
                purchase = Purchase(
                    product_id=data["product_id"],
                    quantity=data["quantity"]
                )
                db.session.add(purchase)
                db.session.commit()
                data["id"] = purchase.id
                data["updated_at"] = purchase.updated_at.strftime(
                    "%Y-%m-%d %H:%M:%S")
                return jsonify(data), 201
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": str(e)}), 500
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

# DevOps: Development
#         Operations
#         Shorten Development, improve efficiency, delivery

#     Pillars
#     -Collaboration
#        Teams + tools(Slack, Whatsapp, Tele || Jira, github || Github)
#     -Automation
#     -Continuous intergration - involves merging source code changes into a shared ripo
#     -Continuous Delivery - automatically prepares the code changes for release to (Staging/Test, UAT) production


# DevSecops  -Development
#           -Security
#           -Operations

# Benefits
# 1. Faster time to market(Automation)
# 2. Better comms and collab
# 3. Continous testing and monitoring reduces downtime
# 4. Security

# DEVOPS LIFECYCLE
# 1. Planing
# 2. Code
# 3. Build
# 4. Test
# 5. Release
# 6. Deploy
# 7. Monitoring

# CI/CD PIPELINE -automated process -> develop, test & deploy
#                -removes manual errors
#                -comms/feedback to developers


#          ELEMENTS OF CI/CD PIPELINE
# Source stage -> pipeline is triggered by a source code repo
#              -> A change source code will trigger a notification to the CI/CD
# Build Stage  -> Combine the source code and it`s dependencies.
# Test Stage   -> validate the correctness of the code / product
# Deploy Stage ->

# Github Actions
# CI/CD Platform that allows you to build, test and deploy pipelines(automated workflows)
# More than just DevOps -> Events e.g workflow that adds release notes || labels whenever PR

# Components of Github Actions
# 1. Workflows
#    - A workflow is automated process aimed at running one or more jobs
#    - Defined YAML/yml
#    - defined in a folder called .github/workflows
#    - Repo can have multiple workflows
# 2. Events - an activity in the repo that will trigger a workflow
# 3. Jobs - these are steps in a workflow
# 4. Actions - predefined, reusable set of jobs to perform a specific task eg -> an action to login to a remote server
# 5. Runners - a server that runs your workflows whenever there triggered
# https://jsonplaceholder.typicode.com
