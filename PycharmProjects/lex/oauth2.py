from flask import Flask, redirect, request
import logging
import requests
from simple_salesforce import Salesforce
logging.basicConfig(level=logging.DEBUG)

consumer_key = "#######"
consumer_secret = "######"
access_token_url = 'https://login.salesforce.com/services/oauth2/token'
redirect_uri = 'http://localhost:5000/callback'
authorize_url = 'https://login.salesforce.com/services/oauth2/authorize'

app = Flask(__name__)


@app.route('/login')
def login():
    url = get_authorization_url()
    return redirect(url)


def get_authorization_url():
    url = "{}?response_type=code&client_id={}&redirect_uri={}".format(authorize_url, consumer_key, redirect_uri)
    return url


@app.route('/callback')
def callback():
    try:
        error = request.args.get('error', '')
        if error:
            raise Exception("Error in callback path")
        code = request.args.get('code')
        if code is None:
            raise Exception("Authorization code not found")
        accesstoken, instanceurl = get_tokens(code)
        print("access token is ", accesstoken)
        print("instace url is ", instanceurl)
        if accesstoken is None:
            raise Exception("Cannot get access_token")
    except Exception as e:
        logging.info("Exception %s is raise", str(e))
    return "StatusOK"


def get_tokens(code):
    access_token, instance_url= None, None
    try:
        data = {
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
            'code': code,
            'client_id': consumer_key,
            'client_secret': consumer_secret
        }
        headers = {
            'content-type': 'application/x-www-form-urlencoded'
        }
        req = requests.post(access_token_url, data=data, headers=headers)
        response = req.json()
        access_token, instance_url = response["access_token"], response['instance_url']
    except Exception as e:
        logging.info("Exception %s is raised ", str(e))
    return access_token, instance_url


def get_contacts2(access_token, instance_url):
    records_list=[]
    try:
        sf = Salesforce(instance_url=instance_url, session_id= access_token)
        records = sf.query("SELECT Name FROM Contact")
        records = records['records']
        for rows in records:
            print(records)
            records_list.append(rows)
    except Exception as e:
        logging.info("Exception %s is raised ", str(e))
    return records_list


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')