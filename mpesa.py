import time
import math
import base64
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth

consumer_key = "GmY1LM09qcoUnEe5GuZYslgrMHsRZoPbFmNQoULhwtOtMqxS"
consumer_secret = "GP3EarK9WFGxqygKdKDJDITav0eqRzO7mEB3j9jDV4IOqMkHaEaYbNiGAwGhEht9"
short_code = "600982"
app_url = " https://nonobligatory-microseismic-bernardo.ngrok-free.dev"

saf_pass_key = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
saf_access_token_api = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
saf_stk_push_api = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
saf_stk_push_query_api = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query"


def get_mpesa_access_token():
    try:
        res = requests.get(saf_access_token_api, auth=HTTPBasicAuth(
            consumer_key, consumer_secret))
        token = res.json()['access_token']

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    except Exception as e:
        print(str(e), "error getting access token")
        raise e

    return headers


headers = get_mpesa_access_token()
# print(headers)


def generate_password():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password_str = short_code + saf_pass_key + timestamp
    password_bytes = password_str.encode()
    
    return base64.b64encode(password_bytes).decode("utf-8")