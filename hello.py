from flask import Flask, request
app = Flask(__name__)

import braintree
import smtplib
import json
from threading import Timer

from email.mime.text import MIMEText

app.debug = True
email_delay = 5   # seconds
rate = 0.01

braintree.Configuration.configure(braintree.Environment.Sandbox,
                                  merchant_id="g53yg6dxy83ybsdk",
                                  public_key="nz6xw7t9v32yyptt",
                                  private_key="ce415d3953de47c63ccd37b06d6290a1")

people = {}


@app.route("/")
def hello():
    return "Hello!"


@app.route("/client_token", methods=["GET"])
def client_token():
        return braintree.ClientToken.generate()


@app.route("/update_database", methods=["POST"])
def updateDb():
        global rate
        decoded = request.get_json()
        user  = decoded[0]
        rate = float(decoded[1])
        sites = decoded[2]
        if user not in people.keys():
                people[user] = {}
                timer = Timer(email_delay, lambda: sendInvoice(user)).start()

        for site in sites.keys():
                if site not in people[user].keys():
                        people[user][site] = sites[site]
                else:
                        people[user][site] += sites[site]
        return str(people) + "\n"



def sendInvoice(user_email):
        msg = json.dumps(people[user_email])
        gmail_user = "piggybankhacknotts@gmail.com"
        gmail_pwd = "sleepingguy1"
        smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo()
        smtpserver.login(gmail_user, gmail_pwd)
        header = 'To:' + user_email + '\n' + 'From: ' + gmail_user + '\n' + 'Subject:Your daily savings invoice! \n'
        msg = header + '\n'
        msg += "Good day,\n\n"
        msg += "Here is your Piggy Jar savings invoice:\n"
        for key in people[user_email].keys():
                msg += key + "   $ " + str(float(people[user_email][key]) * rate) + " (rate: $ " + str(rate) + ")\n"
        msg += '\nLive long and prosper!\n'
        msg += "- PiggyJar\n\n"
        smtpserver.sendmail(gmail_user, user_email, msg)
        smtpserver.close()

        # delete user data
        del people[user_email]


@app.route("/checkout", methods=["POST"])
def create_purchase():
  nonce = request.form["payment_method_nonce"]
  amount = request.form["amount"]
  result = braintree.Transaction.sale({
        "amount": amount,
        "payment_method_nonce": nonce
        })


if __name__ == "__main__":
    app.run('0.0.0.0', 5000)

