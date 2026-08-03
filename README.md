# Flask-WSI — Inventory & Sales Management REST API

A Flask-based REST API for managing products, purchases, sales, and users. It includes JWT-based authentication, M-Pesa (Safaricom) STK push payment integration, OTP-based password reset via the Brevo API, and Sentry error tracking.

## Features

- User registration and login with JWT authentication
- Product management (create, list, update)
- Purchase management
- Sales management with multiple line items (`SalesDetails`)
- Dashboard analytics (remaining stock per product)
- Product stock trend analytics (by hour, day, week, month)
- M-Pesa STK push (Sandbox) integration for payments
- OTP-based password reset delivered via email or SMS (Brevo API)
- Sentry integration for error tracking
- CORS enabled for cross-origin clients

## Tech Stack

- **Language:** Python 3
- **Framework:** Flask
- **Database:** PostgreSQL (SQLAlchemy ORM)
- **Authentication:** Flask-JWT-Extended
- **Payments:** M-Pesa Daraja API (Sandbox)
- **Email/SMS:** Brevo API
- **Error tracking:** Sentry
- **CORS:** Flask-CORS
- **Environment:** python-dotenv

## Project Structure

```
Flask-WSI/
├── main.py          # Flask app, routes, and app configuration
├── models.py        # SQLAlchemy database models
├── utils.py         # Helper functions (OTP, phone formatting, Brevo SMS/email)
├── mpesa.py         # M-Pesa STK push integration
├── password.py      # Password generation utility
├── reset_db.py      # Drops and recreates all database tables
├── mytest.py        # Unit tests for the API
├── trial.py         # Scratch/example file
├── Api/             # (empty) API directory
└── templates/
    └── index.html   # Demo Vue.js frontend page
```

## Prerequisites

- Python 3.8+
- PostgreSQL running locally
- A Brevo API key (for email/SMS OTP)
- M-Pesa Sandbox credentials (consumer key, secret, short code, pass key)

## Installation

1. **Clone the repository and navigate to the project folder:**

   ```bash
   git clone <your-repo-url>
   cd Flask-WSI
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install flask flask-sqlalchemy flask-jwt-extended flask-cors psycopg2-binary python-dotenv requests sentry-sdk africastalking
   ```

4. **Create a `.env` file** in the project root with the variables listed below.

5. **Configure the database** in `main.py` (default):

   ```python
   app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres:12039@localhost:5432/flask_api"
   ```

6. **Run the application:**

   ```bash
   python main.py
   ```

   The app runs on `http://127.0.0.1:5000` by default.

## Environment Variables

Set these in a `.env` file (or export them in your shell):

| Variable        | Description                                   |
| --------------- | --------------------------------------------- |
| `BREVO_API_KEY` | API key for sending OTP via email/SMS (Brevo) |

## Database Models

Defined in `models.py`:

| Model          | Table           | Purpose                               |
| -------------- | --------------- | ------------------------------------- |
| `Product`      | `products`      | Products with buying/selling prices   |
| `Purchase`     | `purchases`     | Stock purchases for products          |
| `Sale`         | `sales`         | Sales records                         |
| `SalesDetails` | `sales_details` | Line items within a sale              |
| `User`         | `users`         | Registered users                      |
| `Payment`      | `payments`      | Payment records (M-Pesa)              |
| `OTP`          | `otps`          | One-time passwords for password reset |

To reset the database (drops all tables and recreates them):

```bash
python reset_db.py
```

## API Endpoints

> All routes except `register`, `login`, and the password-reset endpoints require a valid JWT in the `Authorization` header: `Authorization: Bearer <token>`.

### General

| Method | Endpoint | Auth | Description      |
| ------ | -------- | ---- | ---------------- |
| GET    | `/`      | No   | API version info |

### Authentication

| Method | Endpoint        | Auth | Description                            |
| ------ | --------------- | ---- | -------------------------------------- |
| POST   | `/api/register` | No   | Register a new user, returns JWT token |
| POST   | `/api/login`    | No   | Login and get a JWT token              |
| GET    | `/api/users`    | Yes  | List all users                         |

**Register — request body:**

```json
{
  "name": "John Doe",
  "phone": "0712345678",
  "email": "john@example.com",
  "password": "secret123"
}
```

**Login — request body:**

```json
{
  "email": "john@example.com",
  "password": "secret123"
}
```

### Products

| Method | Endpoint             | Auth | Description            |
| ------ | -------------------- | ---- | ---------------------- |
| GET    | `/api/products`      | Yes  | List all products      |
| POST   | `/api/products`      | Yes  | Create a product       |
| PUT    | `/api/products/<id>` | Yes  | Update a product by ID |

**Create/update product — request body:**

```json
{
  "name": "Toyota Corolla",
  "buying_price": 1500000,
  "selling_price": 1800000,
  "model": "Corolla",
  "year": 2020,
  "condition": "Used",
  "fuel": "Petrol"
}
```

### Purchases

| Method | Endpoint         | Auth | Description        |
| ------ | ---------------- | ---- | ------------------ |
| GET    | `/api/purchases` | Yes  | List all purchases |
| POST   | `/api/purchases` | Yes  | Record a purchase  |

**Record purchase — request body:**

```json
{
  "product_id": 1,
  "quantity": 10
}
```

### Sales

| Method | Endpoint     | Auth | Description                       |
| ------ | ------------ | ---- | --------------------------------- |
| GET    | `/api/sales` | Yes  | List all sales (grouped by sale)  |
| POST   | `/api/sales` | Yes  | Create a sale with multiple items |

**Create sale — request body:**

```json
{
  "sales": [
    { "product_id": 1, "quantity": 2 },
    { "product_id": 2, "quantity": 1 }
  ]
}
```

### Analytics

| Method | Endpoint                              | Auth | Description                                   |
| ------ | ------------------------------------- | ---- | --------------------------------------------- |
| GET    | `/api/dashboard`                      | Yes  | Remaining stock per product                   |
| GET    | `/api/product-stock-trend?period=day` | Yes  | Stock trend by `hour`, `day`, `week`, `month` |

### M-Pesa

| Method   | Endpoint              | Auth | Description                 |
| -------- | --------------------- | ---- | --------------------------- |
| GET/POST | `/api/mpesa/callback` | No   | M-Pesa payment callback URL |

### Password Reset (Auth Blueprint)

Registered under the `/auth` prefix.

| Method | Endpoint                         | Description                               |
| ------ | -------------------------------- | ----------------------------------------- |
| POST   | `/auth/forgot-password`          | Request OTP via email or phone            |
| POST   | `/auth/verify-code/<user_id>`    | Verify an OTP code                        |
| POST   | `/auth/reset-password/<user_id>` | Set a new password after OTP verification |

**Forgot password — request body (email or phone):**

```json
{ "email": "john@example.com" }
```

```json
{ "phone": "0712345678" }
```

## M-Pesa Integration

The `mpesa.py` module integrates with the Safaricom M-Pesa Daraja **Sandbox** API:

- Generates an access token using the consumer key/secret
- Builds a base64-encoded password from the short code, pass key, and timestamp
- Performs an STK push request
- The callback URL is configured to hit `/api/mpesa/callback`

> **Note:** The M-Pesa credentials in `mpesa.py` are hard-coded for the sandbox. For production, move them to environment variables and never commit real secrets.

## Testing

Run the unit tests with:

```bash
python mytest.py
```

Tests cover registration, login, products, purchases, and sales endpoints.

## Security Notes

- Passwords are stored hashed using `werkzeug.security` (`generate_password_hash`).
- Most routes are protected with JWT (`jwt_required()`).
- The JWT secret key and M-Pesa credentials are currently hard-coded in the source. For production, move these to environment variables.
- OTP codes expire after 5 minutes and are single-use (deleted after verification).

## License

This project is for educational/development purposes.
