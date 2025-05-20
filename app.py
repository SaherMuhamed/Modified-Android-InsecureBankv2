import getopt
import sys
from html import escape as html_escape
from functools import wraps
from flask import Flask, request, jsonify
from werkzeug.serving import run_simple
from models import User, Account
from database import db_session
import json
from art import logo

makejson = json.dumps
app = Flask(__name__)

DEFAULT_PORT_NO = 8888


def usageguide():
    print(logo)
    print("InsecureBankv2 Backend-Server")
    print("Options: ")
    print("  --port p    serve on port p (default 8888)")
    print("  --help      print this message")


@app.errorhandler(500)
def internal_servererror(error):
    print(" [!]", error)
    return "Internal Server Error", 500


@app.route('/login', methods=['POST'])
def login():
    Responsemsg = "fail"
    user = request.form['username']
    u = User.query.filter(User.username == request.form["username"]).first()
    print("u=", u)
    if u and u.password == request.form["password"]:
        Responsemsg = "Correct Credentials"
    elif u and u.password != request.form["password"]:
        Responsemsg = "Wrong Password"
    elif not u:
        Responsemsg = "User Does not Exist"
    else:
        Responsemsg = "Some Error"
    data = {"message": Responsemsg, "user": user}
    print(makejson(data))
    return makejson(data)


@app.route('/getaccounts', methods=['POST'])
def getaccounts():
    Responsemsg = "fail"
    acc1 = acc2 = from_acc = to_acc = 0
    user = request.form['username']
    u = User.query.filter(User.username == user).first()
    if not u or u.password != request.form["password"]:
        Responsemsg = "Wrong Credentials so trx fail"
    else:
        Responsemsg = "Correct Credentials so get accounts will continue"
        a = Account.query.filter(Account.user == user)
        for i in a:
            if (i.type == 'from'):
                from_acc = i.account_number
        for j in a:
            if (i.type == 'to'):
                to_acc = i.account_number
    data = {"message": Responsemsg, "from": from_acc, "to": to_acc}
    print(makejson(data))
    return makejson(data)


@app.route('/changepassword', methods=['POST'])
def changepassword():
    newpassword = request.form.get('newpassword')
    user = request.form.get('username')
    
    if not newpassword or not user:
        return jsonify({"message": "Missing username or password"}), 400

    u = User.query.filter_by(username=user).first()
    if not u:
        return jsonify({"message": "User not found"}), 404

    u.password = newpassword  # plain text (⚠️ not secure)
    db_session.commit()
    
    return jsonify({"message": "Change Password Successful"})


@app.route('/dotransfer', methods=['POST'])
def dotransfer():
    Responsemsg = "fail"
    user = request.form['username']
    amount = request.form['amount']
    u = User.query.filter(User.username == user).first()
    if not u or u.password != request.form["password"]:
        Responsemsg = "Wrong Credentials so trx fail"
    else:
        Responsemsg = "Success"
        from_acc = request.form["from_acc"]
        to_acc = request.form["to_acc"]
        amount = request.form["amount"]
        from_account = Account.query.filter(Account.account_number == from_acc).first()
        to_account = Account.query.filter(Account.account_number == to_acc).first()
        to_account.balance += int(request.form['amount'])
        from_account.balance -= int(request.form['amount'])
        db_session.commit()
    data = {"message": Responsemsg, "from": from_acc, "to": to_acc, "amount": amount}
    return makejson(data)


@app.route('/devlogin', methods=['POST'])
def devlogin():
    user = request.form['username']
    Responsemsg = "Correct Credentials"
    data = {"message": Responsemsg, "user": user}
    print(makejson(data))
    return makejson(data)


if __name__ == '__main__':
    port = DEFAULT_PORT_NO
    options, args = getopt.getopt(sys.argv[1:], "", ["help", "port="])
    for op, arg1 in options:
        if op == "--help":
            usageguide()
            sys.exit(2)
        elif op == "--port":
            port = int(arg1)

    print(logo)
    print(f"[+] The server is hosted on port: {port}")
    run_simple('0.0.0.0', port, app)
