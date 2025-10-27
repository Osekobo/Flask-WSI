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

purchases_list = []
sales_list = []


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
        return jsonify({"error": "Ensure all fields are filled"}), 400
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

# https://jsonplaceholder.typicode.com

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





# import { useState, useEffect } from "react";
# // import 'bootstrap/dist/css/bootstrap.min.css';
# // import 'bootstrap/dist/js/bootstrap.bundle.min.js';
# import '/src/index.css'

# function EggsProduction() {
#     const [eggsproduction, setEggsproduction] = useState([])
#     const [error, setError] = useState("")
#     const [formData, setFormData] = useState({
#         batch_id: "",
#         date: "",
#         eggs_collected: "",
#         broken_eggs: "",
#         remarks: "",
#     })
#     const [showForm, setShowForm] = useState(false);

#     const handleChange = (e) => {
#         setFormData({
#             ...formData,
#             [e.target.name]: e.target.value,
#         });
#     };

#     const handleSubmit = async (e) => {
#         e.preventDefault();
#         try {
#             const response = await fetch("http://127.0.0.1:5000/eggsproduction", {
#                 method: "POST",
#                 headers: { "Content-Type": "application/json" },
#                 body: JSON.stringify(formData),
#             });
#             const data = await response.json();

#             if (response.ok) {
#                 setShowForm(false);
#                 setFormData({ batch_id: "", date: "", eggs_collected: "", broken_eggs: "", remarks: "" })
#                 setError("")
#             } else {
#                 setError(data.message)
#             }
#         } catch (err) {
#             console.error(err);
#             setError(err.message);
#         }
#     }

#     useEffect(() => {
#         const fetchCollection = async () => {
#             try {
#                 const response = await fetch("http://127.0.0.1:5000/eggsproduction")
#                 const data = await response.json();

#                 if (response.ok) {
#                     if (Array.isArray(data)) {
#                         setEggsproduction(data)
#                     } else {
#                         setEggsproduction([])
#                         setError(data.message || "Error with the data format")
#                     }

#                 } else {
#                     setError(data.message || "Failed to load eggs collection data!")
#                 }
#             } catch (err) {
#                 setError("Server: " + err.message)
#             }
#         }
#         fetchCollection()
#     }, [])

#     return (
#         <div className="collection-page mt-4">
#             {error && <p className="text-danger text-center">{error}</p>}
#             <h3 className="text-center mb-3">Collection Data</h3>
#             {error && <p className="text-danger text-center emsg">{error}</p>}
#             <div className="d-flex justify-content-end mb-3 position-relative">
#                 <button className="btn btn-secondary bt1" onClick={() => setShowForm(!showForm)}>{showForm ? "Cancel" : "Add new Collection Data"}</button>
#                 {showForm && (
#                     <form onSubmit={handleSubmit} className="mb-4 frm">
#                         <div className="row g-2 form-row">
#                             <div className="col-md-2"> <input type="text" name="batch_id" placeholder="Batch ID" value={formData.batch_id} onChange={handleChange} required className="form-control expense-input" /></div>
#                             <div className="col-md-2"> <input type="date" name="date" placeholder="Date" value={formData.date} onChange={handleChange} required className="form-control expense-input" /></div>
#                             <div className="col-md-2">     <input type="text" name="eggs_collected" placeholder="Eggs Collected" value={formData.eggs_collected} onChange={handleChange} required className="form-control expense-input" /></div>
#                             <div className="col-md-2">   <input type="text" name="broken_eggs" placeholder="Broken Eggs" value={formData.broken_eggs} onChange={handleChange} required className="form-control expense-input" /></div>
#                             <div className="col-md-3">
#                                 <input type="text" name="remarks" placeholder="Remarks on Collection" value={formData.remarks} onChange={handleChange} className="form-control expense-input" /></div>
#                             <div className="col-md-1 d-flex align-items-center justify-content-center"><button type="submit" className="btn btn-secondary mt-3 sbtn">Save</button></div>
#                         </div>
#                     </form>
#                 )}
#             </div>
#             <div>
#                 <table className="table table-hover text-center align-middle batch-table">
#                     <thead className="table-secondary">
#                         <tr>
#                             <td>Batch ID</td>
#                             <td>Date</td>
#                             <td>Eggs Collected</td>
#                             <td>Broken Eggs</td>
#                             <td>Remaining Eggs</td>
#                             <td>Number of Crates</td>
#                             <td>Remarks</td>
#                             <td>Extra Eggs</td>
#                         </tr>
#                     </thead>
#                     <tbody>
#                         {eggsproduction.map((e) => (
#                             <tr key={e.id} className="batch-row">
#                                 <td>{e.batch_id}</td>
#                                 <td>{e.date}</td>
#                                 <td>{e.eggs_collected}</td>
#                                 <td>{e.broken_eggs}</td>
#                                 <td>{e.remaining_eggs}</td>
#                                 <td>{e.quantity_in_crates}</td>
#                                 <td>{e.remarks}</td>
#                                 <td>{e.extra_eggs}</td>
#                             </tr>
#                         ))}
#                     </tbody>
#                 </table>
#             </div>
#         </div>
#     )
# }
# export default EggsProduction;