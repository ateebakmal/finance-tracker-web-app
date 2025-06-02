from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, get_flashed_messages, make_response, session
import database_functions as db_function
from database_functions import email_exists, create_user, check_username_and_password, username_exists, get_recent_transactions_as_dataframe
from database_functions import get_user_accounts_from_db, get_user_financial_summary_from_db, get_user_categories_from_db, add_account_type_to_db , get_filtered_transaction_from_db
from utility import print_green

from plots import get_expense_vs_monthly_plot, get_monthly_categorical_spending_plot

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import User

#Liveserver alternative to automatically reload page for html and css
from livereload import Server


app = Flask(__name__)
app.secret_key = "your-secret-key"

# app.config['SECRET_KEY'] = 'your-secret-key'

#Setup Flask Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@app.route("/", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        print_green("Got POST request")
        request_json = request.get_json()
        print_green(f"Json Data Recieved : {request_json}")

        #Extract data from json
        email = request_json["email"]
        password = request_json["password"]

        #Check if email and password is valid or not
        response_from_db = check_username_and_password(email,password)


        print(response_from_db)

        #If username or password is invalid
        if response_from_db is None:
            return jsonify({
                "success" : False,
                "message" : "Invalid Username or Password"
                })
        
        #if username or password is valid

        #1. Log them in
        user = User(id=response_from_db["user_id"])
        login_user(user)

        #2. Return a json message to indicate you have logged in
        return jsonify({
                "success" : True,
                "message" : "Valid Username or Password"
                })
    return render_template("login.html")


@app.route("/signup", methods = ["GET", "POST"])
def signup():
    if request.method == "POST":
        print("Got Post Request")

        json_text = request.get_json()
        print_green(json_text)

        #Extract json data
        email = json_text.get("email")
        password = json_text.get("password")
        username = json_text.get("username")

        #Check if email exists
        if(email_exists(email)):
            return jsonify(
                {
                    "success" : False,
                    "message" : "email already exists"
                 }
            ),200
        
        #Check if email exists
        if(username_exists(username)):
            return jsonify(
                {
                    "success" : False,
                    "message" : "username already exists"
                 }
            ),200
        #Email and username is unique, Now create a account
        create_user(username,email,password)
        return jsonify({"success" : True, "message" : "user registered successfully"},200)
        
    return render_template("register.html")

@login_manager.user_loader
def load_user(user_id):
    if user_id is None:
        return None
    return User(id=user_id)  # your lightweight user


@app.route("/dashboard")
@login_required
def dashboard():
    get_expense_vs_monthly_plot(current_user.id)
    get_monthly_categorical_spending_plot(current_user.id, 12)
    
    return render_template("dashboard.html", active='dashboard', title="Dashboard")

@app.route("/account")
@login_required
def account():
    return render_template("account.html", active='account', title="Dashboard")

@app.route("/reports")
@login_required
def report():
    return render_template("report.html", active='report', title="Dashboard")

@app.route("/transaction")
@login_required
def transaction():
    return render_template("transaction.html", active='transaction', title="Dashboard")

@app.route("/budget")
@login_required
def budget():
    return render_template("budget.html", active='budget', title="Budgets")

@app.route("/logout")
@login_required
def logout():
    
    logout_user()
    return redirect(url_for("login"))


#-----Following code is for data end point api
@app.route("/api/get_recent_transactions_table/<int:limit>")
@login_required
def get_recent_transactions(limit):
    df = get_recent_transactions_as_dataframe(current_user.id,limit)

    html_table = df.to_html(index=False, border=1)
    # print_green(html_table)
    return html_table

@app.route("/api/get_transfer_transactions_table")
@login_required
def get_transfer_transactions():
    df = db_function.get_transfer_transactions_from_db(current_user.id)

    html_table = df.to_html(index=False, border=1)
    # print_green(html_table)
    return html_table

@app.route("/api/get_user_accounts_table")
@login_required
def get_user_accounts_table():
    df = get_user_accounts_from_db(current_user.id)

    html_table = df.to_html(index = False)
    # print(html_table)
    return html_table


@app.route("/api/get_user_financial_summary")
@login_required
def get_user_financial_summary():
    # Commenting following line to get income and expense for current month and year
    # json_data = get_user_financial_summary_from_db(current_user.id, 12 , 2024)

    from datetime import datetime
    year = datetime.today().year
    month = datetime.today().month
    json_data = get_user_financial_summary_from_db(current_user.id , month , year)
    return jsonify(json_data)

@app.route("/api/add_user_account",methods = ["GET", "POST"])
@login_required
def add_user_account():
    if request.method == "POST":
        print_green("Got POST request")
        json_data = request.get_json()
        print_green(json_data)

    return jsonify({"success" : True})

@app.route("/api/get_user_categories")
@login_required
def get_user_categories():
    categories = get_user_categories_from_db(current_user.id)
    return jsonify({"categories" : categories})


@app.route("/api/get_user_accounts")
@login_required
def get_user_accounts():
    df = get_user_accounts_from_db(current_user.id)
    accounts = df["Account"].to_list()
    return jsonify({ "accounts" : accounts })

@app.route("/api/add_acount_type", methods = ["POST"])
@login_required
def add_accout_type():
    print_green("Got request")
    request_json = request.get_json()
    account_type = request_json.get("account_type")
    
    account_type = account_type.lower().strip() # Make the text lowercase and remove any spaces
    
    db_response = add_account_type_to_db(current_user.id, account_type)

    print_green(db_response)
    return jsonify(db_response)

@app.route("/api/remove_user_account", methods = ["POST"])
@login_required
def remove_user_account():
    json_request = request.get_json()
    print_green(f"json_request : {json_request}")

    account_type_name = json_request.get("account_type_name")
    db_response  = db_function.remove_user_account_from_db(account_type_name=account_type_name, user_id= current_user.id)

    return jsonify(db_response)

@app.route("/api/add_user_category", methods = ["POST"])
@login_required
def add_user_category():
    json_request = request.get_json()
    print_green(json_request)
    category_name = json_request.get("category_name")
    print_green(category_name)

    success = db_function.add_category_to_db(user_id= current_user.id,category=category_name)

    if success:
        return jsonify({"success" : True})
    else:
        return jsonify({"success" : False})


@app.route("/api/get_filtered_transactions", methods = ["POST"])
@login_required
def get_filtered_transactions():
    json_request = request.get_json()

    print_green(json_request)

    if(json_request["filter_type"] == "transfer"):
        print_green("we here")
        df = db_function.get_filtered_transfer_transaction_from_db(json_request,current_user.id)
    
    #Else return the income_and expense 
    df = get_filtered_transaction_from_db(json_request, current_user.id)

    #return html table
    return df.to_html(index=False)


@app.route("/api/add_transaction", methods = ["POST"])
@login_required
def add_transaction():
    json_data = request.get_json()
    transaction_data = json_data["transactionData"]
    print_green(f"Json Request Recieved : {transaction_data}" )

    response = db_function.add_user_transaction_to_db(transaction_data, current_user.id)
    print_green(f"DB response : {response}")
    return jsonify( response )


@app.route("/api/add_user_budget",methods = ["POST"])
@login_required
def add_user_budget():
    json_data = request.get_json()

    db_response = db_function.add_budget_in_db(current_user.id , json_data)
    return jsonify( db_response )

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    server = Server(app.wsgi_app)
    server.watch('templates/')
    server.watch('static/')
    server.serve(port=1100)

    