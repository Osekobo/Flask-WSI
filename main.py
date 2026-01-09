from flask_jwt_extended import jwt_required
import africastalking
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, OTP
from flask import Blueprint, request, jsonify
import random
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
                 - func.coalesce(func.sum(SalesDetails.quantity), 0)).label("remaining_stock")
            )
            .outerjoin(Purchase, Product.id == Purchase.product_id)
            .outerjoin(SalesDetails, Product.id == SalesDetails.product_id)
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
    if "name" not in data.keys() or "phone" not in data.keys() or "email" not in data.keys() or "password" not in data.keys():
        error = {"error": "Ensure all fields are filled"}
        return jsonify(error), 400
    elif User.query.filter_by(email=data["email"]).first() is not None:
        error = {"error": "User with that email already exists"}
        return jsonify(error), 409
    else:
        usr = User(name=data["name"], phone=data["phone"], email=data["email"],
                   password=generate_password_hash(data["password"]))
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
    usr = User.query.filter_by(email=data["email"]).first()
    if not usr or not check_password_hash(usr.password, data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

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
                    "buying_price": prod.buying_price, "selling_price": prod.selling_price, "model": prod.model, "year": prod.year, "condition": prod.condition, "fuel": prod.fuel}
            products_list.append(data)
        # retriving products
        return jsonify(products_list), 200
    elif request.method == "POST":
        data = dict(request.get_json())
        # data = request.get_json(silent=True)
        # if not data:
        #     return jsonify({"error": "Invalid or missing JSON body"}), 400
        if "name" not in data.keys() or "buying_price" not in data.keys() or "selling_price" not in data.keys() or "model" not in data.keys() or "year" not in data.keys() or "condition" not in data.keys() or "fuel" not in data.keys():
            error = {"error": "Ensure  all fields are set"}
            return jsonify(error), 400
        else:
            # products_list.append(data)
            prod = Product(
                name=data["name"], buying_price=data["buying_price"], selling_price=data["selling_price"], model=data["model"], year=data["year"], condition=data["condition"], fuel=data["fuel"])
            db.session.add(prod)
            db.session.commit()
            data["id"] = prod.id
            return jsonify(data), 201
        # return jsonify({'message': "Product added successfully!"})
    else:
        error = {"error": "Method not allowed"}
        return jsonify(error), 405

# update product per id route


@app.route("/api/products/<int:id>", methods=["PUT"])
@jwt_required()
def update_product(id):
    data = request.get_json()
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    # Update fields if provided
    product.name = data.get("name", product.name)
    product.buying_price = data.get("buying_price", product.buying_price)
    product.selling_price = data.get("selling_price", product.selling_price)
    product.model = data.get("model", product.model)
    product.year = data.get("year", product.year)
    product.condition = data.get("condition", product.condition)
    product.fuel = data.get("fuel", product.fuel)

    db.session.commit()

    return jsonify({
        "id": product.id,
        "name": product.name,
        "buying_price": product.buying_price,
        "selling_price": product.selling_price,
        "model": product.model,
        "year": product.year,
        "condition": product.condition,
        "fuel": product.fuel
    }), 200


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
        # print("-----------------------------------", sales_group)
        return jsonify(result), 200
    elif request.method == "POST":
        try:
            data = request.get_json()
            # print("Incoming sales data----------------:", data)
            sales_data = data.get("sales", [])
            if not sales_data or not isinstance(sales_data, list):
                return jsonify({"error": "Request must include a 'sales' list"}), 400
            sale = Sale()
            db.session.add(sale)
            db.session.flush()
            created_details = []
            for item in sales_data:
                product_id = item.get("product_id")
                quantity = item.get("quantity")
                if not product_id or not quantity:
                    return jsonify({"error": "Each sale must include product_id and quantity"}), 400
                detail = SalesDetails(
                    sale_id=sale.id,
                    product_id=product_id,
                    quantity=quantity
                )
                db.session.add(detail)
                created_details.append({
                    "product_id": detail.product_id,
                    "quantity": detail.quantity,
                })
            db.session.commit()
            return jsonify({"message": "Sales added successfully", "sale_id": sale.id, "details": created_details}), 201
        except Exception as e:
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Method not allowed"}), 405


@app.route("/api/purchases", methods=["GET", "POST"])
@jwt_required()
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


@app.route("/api/mpesa/callback", methods=["GET", "POST"])
def mpesa_callback():
    data = request.get_json()
    print("\n=== CALLBACK RECEIVED ===")
    print(data)
    print("========================\n")

    return {"message": "Callback received"}, 200


@app.route("/api/product-stock-trend", methods=["GET"])
@jwt_required()
def product_stock_trend():
    period = request.args.get("period", "day")  # default to day
    if period not in ["hour", "day", "week", "month"]:
        period = "day"

    # Use PostgreSQL date_trunc to group by selected period
    results = (
        db.session.query(
            Product.name,
            func.date_trunc(period, Purchase.created_at).label("time_period"),
            func.sum(Purchase.quantity).label("total_quantity")
        )
        .join(Purchase, Product.id == Purchase.product_id)
        .group_by(Product.name, "time_period")
        .order_by("time_period")
        .all()
    )

    data = {}
    for name, time_period, qty in results:
        if name not in data:
            data[name] = []
        data[name].append({
            "date": time_period.strftime("%Y-%m-%d %H:%M:%S") if period == "hour" else time_period.strftime("%Y-%m-%d"),
            "quantity": qty
        })

    return jsonify(data), 200


auth = Blueprint('auth', __name__)

# Africastalking init
username = "sandbox"
api_key = "atsk_0be4512d5a73da6bad07b94aa50afcea41ca8338a93888a5c129f36e4f99b18ca1e2b4b4"
africastalking.initialize(username, api_key)
sms = africastalking.SMS


def format_phone(phone):
    phone = phone.strip()

    if phone.startswith("0"):
        phone = "+254" + phone[1:]
    elif phone.startswith("254"):
        phone = "+" + phone
    elif not phone.startswith("+"):
        phone = "+" + phone

    # Basic length check for Kenya numbers
    if not phone.startswith("+254") or len(phone) != 13:
        raise ValueError("Invalid Kenyan phone number")

    return phone


def generate_otp():
    return str(random.randint(100000, 999999))


@auth.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()

    if not data or "phone" not in data:
        return jsonify({"error": "Phone number is required"}), 400

    phone_raw = data["phone"]

    try:
        phone = format_phone(phone_raw)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # Check if user exists
    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Generate OTP
    otp_code = generate_otp()

    # Save OTP in the database
    otp_entry = OTP(user_id=user.id, otp=otp_code)
    db.session.add(otp_entry)
    db.session.commit()


    try:
        print(f"Simulating sending SMS to {phone} with OTP {otp_code}")
    except Exception as e:
        print("SMS failed:", e)
        return jsonify({"message": "OTP sent successfully"}), 200


@auth.route('/verify-code/<int:user_id>', methods=['POST'])
def verify_code(user_id):
    data = request.get_json()
    code = data.get('otp')

    otp = OTP.query.filter_by(user_id=user_id, otp=code).first()
    if not otp:
        return jsonify({"error": "Invalid code"}), 400

    return jsonify({"message": "OTP verified"}), 200


# generate password


@auth.route('/reset-password/<int:user_id>', methods=['POST'])
def reset_password(user_id):
    data = request.get_json()
    new_password = data.get('password')

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"message": "Password updated"}), 200


if __name__ == "__main__":
    # at the bottom, before app.run()
    app.register_blueprint(auth, url_prefix="/auth")
    with app.app_context():
        # db.drop_all()
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
