from main import db, app

with app.app_context():
    db.drop_all()
    db.create_all()
    print("All tables dropped and recreated successfully!")


from flask import Flask, jsonify, request
from datetime import datetime
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import sentry_sdk
from models import db, Product, Sale, User, Purchase, SalesDetails
from sqlalchemy import func
from flask_cors import CORS
from collections import defaultdict

app = Flask(__name__)
CORS(app)


@app.route("/api/sales", methods=["GET", "POST"])
# This decorator registers a route with Flask.
# /api/sales is the URL endpoint.
# methods=["GET", "POST"] means this endpoint accepts GET and POST requests.
@jwt_required()
# ensures that only authenticated users with a valid JWT (JSON Web Token) can access this route.
def sales():
    # defines the function sales() that will run whenever /api/sales is accessed.
    if request.method == "GET":  # Checks if the request is a GET request.
        results = (
            # SQLAlchemy query that joins three tables: Sale → main sale record SalesDetails → which products were sold in that sale. Product → details about each product
            db.session.query(Sale, SalesDetails, Product)
            .join(SalesDetails, SalesDetails.sale_id == Sale.id)
            # .join() connects the tables on foreign key relationships.
            .join(Product, Product.id == SalesDetails.product_id)
            .order_by(Sale.created_at.desc())
            # .order_by(Sale.created_at.desc()) sorts the results so most recent sales come first.
            .all()
            # .all() executes the query and returns a list of tuples (Sale, SalesDetails, Product)
        )
        sales_group = defaultdict(list)
        # Creates a dictionary that defaults to an empty list for any key,that will be used to group products by sale.
        for sale, detail, product in results:
            sales_group[sale.id].append((sale, detail, product))
            # loops through the query results, groups all SalesDetails foe each sale.id. After this sales_group[sale_id] contains a list of (sale, detail, product) tuples for that sale.
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
        # builds a JSON-serializable list of sales. For each sale_id in sales_group: sale.id → sale ID sale.created_at → formatted timestamp "items" → list of products in that sale with: product ID product name quantity sold
        # Returns the list of sales as JSON with HTTP status 200 (OK).
        return jsonify(result), 200
    elif request.method == "POST":
        try:
            data = request.get_json()
            # If the request is POST, it reads JSON payload from the request body.
            # Extracts the "sales" key from the JSON.Defaults to an empty list if it doesn’t exist.
            sales_data = data.get("sales", [])
            if not sales_data or not isinstance(sales_data, list):
                # checks if the sales key exists and is a list. Returns HTTP 40(Bad Request)if the data is invalid
                return jsonify({"error": "Request must include a 'sales' list"}), 400
            sale = Sale()  # Creates a new Sale object (a new sale record)
            db.session.add(sale)
            # adds it to the session but does not commit yet
            db.session.flush()
            # .flush() assigns it an ID immediately, which is needed for the sales details.
            created_details = []
            # Initializes a list to store details of the added sale items.
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
