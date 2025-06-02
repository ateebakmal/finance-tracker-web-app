import psycopg2 as psgSQL
from utility import print_green, print_red
import json
import traceback

# Establish connection
conn = psgSQL.connect(
    dbname="finance-tracker-db",
    user="postgres",
    password="ateeb123",
    host="localhost",
    port="5432"  # default PostgreSQL port
)

def email_exists(email:str):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users WHERE email = %s
        """,(email,))
    
    users = cursor.fetchall()
    response = False
    if users:
        response = True
    
    cursor.close()
    return response

def username_exists(username:str):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users WHERE username = %s
        """,(username,))
    
    users = cursor.fetchall()
    response = False
    if users:
        response = True
    
    cursor.close()
    return response

def create_user(username,email,password):
    """
    This function takes username, email and password as arguments and create the entry in database.
    Returns: True, If successfully added the value. False: If some db error occurs
    Error Logs: In case of an error, It prints the error logs in red
    """
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users(username,email,password_hash)
            VALUES(%s,%s,%s)       
            """,(username,email,password))
        
        conn.commit()
        cursor.close()
        return True
    except Exception as e:
        conn.rollback()
        print_red("Some database error occured")
        print_red("---------------Error Log------------")
        print_red(e)
        
def check_username_and_password(email, password):
    """
    This function checks if a user exists by comparing email and password with database.
    If user exists it returns a dictionary {"user_id" : user_id}
    If user doesnt exists it returns None.
    """
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE email = %s AND password_hash = %s
        """, (email,password))
    
    users = cursor.fetchone()

    response = None # Response to return to the server 
    if users is not None:
        response = {
            "user_id" : users[0]
        }
    
    cursor.close()
    return response 


def get_recent_transactions_as_dataframe(user_id, limit):
    """
    This function takes in user_id and returns its top 5 transactions as a pandas DataFrame
    Note: This function has been updated to only return income and expenses
    """
    import pandas as pd

    cursor = conn.cursor()
    query_result = None
    column_names = None
    try:
        cursor.execute(
            """
            SELECT
                transaction_date as "Date",
                category_name as "Category",
                transaction_amount as "Amount",
                transaction_type as  "Type",
                account_type_name as "Account"
            FROM
                "transaction"
            LEFT JOIN
                "category"
                ON
                    transaction.category_id = category.category_id
            LEFT JOIN 
                "accounttype"
                ON 
                    transaction.account_type_id = accounttype.account_type_id
            WHERE 
                user_id = %s
                AND ( transaction_type = 'income' OR transaction_type = 'expense')  
            ORDER BY 
                transaction_date DESC
            LIMIT 
                %s;
            """
        ,(user_id,limit))

        query_result = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description] 

    except Exception as e:
        print_red("Error Occured")
        print_red(e)
        conn.rollback()

    return_value = None
    if query_result is not None and column_names is not None:
        return_value = pd.DataFrame(query_result, columns=column_names) 

    cursor.close()
    return return_value

def get_transfer_transactions_from_db(user_id):
    """
    This function takes in user_id and returns its top 5 transactions as a pandas DataFrame
    Note: This function has been updated to only return income and expenses
    """
    import pandas as pd

    cursor = conn.cursor()
    query_result = None
    column_names = None
    try:
        cursor.execute(
            """
            WITH q1 AS (
                SELECT 
                    transaction_name AS "Name",
                    account_type_name AS "From",
                    source_account_type_id AS "source_id",
                    destination_account_type_id AS "dest_id",
                    transaction_amount AS "Amount",
                    transaction_date AS "Date"
                FROM
                    transaction
                JOIN
                    accounttype
                        ON transaction.source_account_type_id = accounttype.account_type_id
                WHERE user_id = %s
            )

            SELECT 
                "Name",
                "From",
                account_type_name AS "To",
                "Amount",
                "Date" FROM q1
            JOIN accounttype 
                ON accounttype.account_type_id = q1.dest_id
            ORDER BY
                "Date" DESC;
            """
        ,(user_id,))

        query_result = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description] 
    except Exception as e:
        print_red("Error Occured")
        print_red(e)
        conn.rollback()

    return_value = None
    if query_result is not None and column_names is not None:
        return_value = pd.DataFrame(query_result, columns=column_names) 

    cursor.close()
    return return_value


def get_expense_vs_monthly_data(user_id):
    import pandas as pd
    
    cursor = conn.cursor()

    rows = None
    column_names = None
    try:

        cursor.execute("""
    WITH income_tb AS (
    	SELECT 
    		EXTRACT (MONTH FROM transaction_date) AS month,
    		SUM(transaction_amount)
    	FROM
    		"transaction"
    	WHERE
    		user_id = %s AND transaction_type = 'income'
    	GROUP BY
    		EXTRACT(MONTH FROM transaction_date)
    	ORDER BY
    		EXTRACT(MONTH FROM transaction_date)
    ),
    expense_tb AS (
    	SELECT 
    		EXTRACT (MONTH FROM transaction_date) as month,
    		SUM(transaction_amount)
    	FROM
    		"transaction"
    	WHERE
    		user_id = %s AND transaction_type = 'expense'
    	GROUP BY
    		EXTRACT(MONTH FROM transaction_date)
    	ORDER BY
    		EXTRACT(MONTH FROM transaction_date)
    )
    
    SELECT 
    	income_tb.month as "Month",
    	income_tb.sum as "Income",
    	expense_tb.sum as "expense"
    FROM income_tb JOIN expense_tb ON income_tb.month = expense_tb.month;
        """, (user_id, user_id))
    
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description] 
        
    except Exception as e:
        print("Error")
        print(e)
        conn.rollback()

    df = pd.DataFrame(data=rows, columns=column_names)
    return df

def get_monthly_categorical_spendings_data(user_id, month):
    """
    This function is used to return a dataframe by querying the data base for user spendings per category for a specific
    month.
    The main use for this function is to get data for plotting pie chart
    """
    #Get user_id
    import pandas as pd
    cursor = conn.cursor()

    rows = None
    try:
        cursor.execute(
            f"""
        SELECT category_name, SUM(transaction_amount)
        FROM
            "transaction"
        JOIN category
            ON transaction.category_id = category.category_id
        WHERE
            user_id = {user_id}
            AND EXTRACT(MONTH FROM transaction_date) = {month}
        GROUP BY category_name;
            """
        )

        rows = cursor.fetchall()
    except Exception as e:
        print_red("Error")
        print_red(e)
        conn.rollback()
    
    df = pd.DataFrame(rows , columns = ["category_name","amount_spent"])
    # display(df)
    df['amount_spent'] = df["amount_spent"].astype("float")

    cursor.close()
    return df


def get_user_accounts_from_db(user_id):
    """
    This function takes in a user_id and then returns their accounts and balance as pandas dataframe
    """
    import pandas as pd

    cursor = conn.cursor()
    rows = None
    column_names = None
    
    try:
        cursor.execute(
            """
            SELECT 
                account_type_name AS "Account",
                current_amount AS "Balance"
            FROM
                useraccount
            JOIN 
                users
                ON users.user_id = useraccount.user_id
                
            JOIN 
                accounttype
                ON accounttype.account_type_id = useraccount.account_type_id
            WHERE 
                users.user_id = %s;
            """
        ,(user_id,))

        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]

    except Exception as e:
        print_red("Error Occured")
        print_red(e)
        conn.rollback()

    
    df = pd.DataFrame(data = rows, columns= column_names)
    cursor.close()
    return df


def get_user_financial_summary_from_db(user_id, month, year):
    """
    This functions takes in user_id , month and a year.
    Returns a json object as
    {
        "balance" : value,
        "expense" : value,
        "income" : value
    }
    """

    import pandas as pd


    cursor = conn.cursor()
    json_data = None
    try:
        cursor.execute(
            """
            WITH balance_tb AS (
                SELECT 
                    'balance' AS transaction_type,
                    SUM(current_amount)
                FROM
                    useraccount
                WHERE 
                    user_id = %s
                GROUP BY 
                    user_id
            ),
            expense_tb AS (
                SELECT
                    transaction_type,
                    SUM(transaction_amount)
                FROM 
                    "transaction"
                WHERE
                    EXTRACT(MONTH FROM transaction_date) = %s
                    AND EXTRACT(YEAR FROM transaction_date) = %s
                    AND user_id = %s
                GROUP BY
                    user_id,
                    transaction_type
            )
            SELECT * FROM balance_tb
            UNION
            SELECT * FROM expense_tb;
            """
        ,(user_id,month,year,user_id))
        
        rows = cursor.fetchall()
        print_green(rows)
            # First check if any of the following is missing:
            # balance, income, expense
            # By default the json data is zero, we check if a value exists in df, then update it
            # 1)Make a df so querying is easy
            # 2)If any of the following is missing just add zero for it
            
        df = pd.DataFrame(data= rows, columns=["type","balance"])
        json_data  = {
            "balance" : 0,
            "income" : 0,
            "expense" : 0
        }


        for i in ["balance","income", "expense"]:
            if i in df["type"].to_list():
                print_green(i)
                json_data[i] = float(df[ df["type"] == i]["balance"])

        print_green("json_data:")
        print_green(json_data)

    except Exception as e:
        print_red("Error Occured")
        print_red(e)
        print_red(traceback.format_exc())
        conn.rollback()

    cursor.close()
    return json_data

def get_user_categories_from_db(user_id):
    """
    This function takes in user_id and returns all the categories the user has saved.
    Returns an array
    """

    cursor = conn.cursor()
    return_value = None
    try:
        cursor.execute(
            """
            SELECT
                category_name
            FROM
                usercategory
            JOIN
                category ON category.category_id = usercategory.category_id
            WHERE user_id  = %s;
            """
        ,(user_id,))
        rows = cursor.fetchall()
        return_value = [i[0] for i in rows]
    except Exception as e:
        print_red("Error occured")
        print_red(e)
        conn.rollback


    return return_value


def add_account_type_to_db(user_id : int, account_type : str):

    # Set of steps to do:
    # 1) Check if the account_type is already in the accounttype table
    #    If the accounttype table has the entry, get its key.
    # 2) If the accounttype dont have the entry for the account type
    #    Insert into account_type the new id and get the key for the new entry
    # 3) Insert into useraccount with user_id, account_type_ID and current_amount = 0


    cursor = conn.cursor()
    return_data = None
    try:
        cursor.execute("""
            SELECT * 
            FROM accounttype
            WHERE account_type_name = %s;
        """,(account_type,))

        rows = cursor.fetchall()

        primary_key = None
        
        if rows:    
            # If there is some row get its primary key
            print_green("The rows are not none")
            print(rows)
            primary_key = rows[0][0]

            # If there is a primary key check, if user already has this account
            cursor.execute(
                """
                SELECT * from useraccount
                WHERE user_id = %s AND account_type_id = %s
                """
            ,(user_id,primary_key))

            rows = cursor.fetchall()

            # If there are some rows and user account already exists
            if rows:
                return {"success" : False, "message" : "Account already exists"}
        else:
            print_green("The rows are none")
            print_green("Inerting a new entry")
            #If rows are none add a new entry to db
            cursor.execute(
                """
            INSERT INTO accounttype(account_type_name)
            VALUES(%s)
                """,(account_type,))
            
            conn.commit()

            print_green("Getting the new primary key")
            # Now get the primary key
            cursor.execute("""
                SELECT * 
                FROM accounttype
                WHERE account_type_name = %s;
            """,(account_type,))

            rows = cursor.fetchall()
            primary_key = rows[0][0]

        #Now add the row to useraccount
        cursor.execute("""
            INSERT INTO useraccount(user_id, account_type_id, current_amount)
            VALUES (%s,%s,%s)
        """,(user_id,primary_key,0))

        conn.commit()
    except Exception as e:
        print_red("Error Occured")
        print_red(e)
        conn.rollback()
        return {"success" : False, "message" : "Server error"}

    cursor.close()
    return {"success" : True, "message" : "Account added successfully"}

def remove_user_account_from_db(account_type_name : str, user_id : int):
    # This function removes an account_type from user accounts
    # Get account_type_id to remove from accounttype table
    # Drop the row

    cursor = conn.cursor()

    return_message = None
    try:
        # 1 Get primary key for account_type_name
        cursor.execute(
            """
            SELECT * FROM accounttype
            WHERE account_type_name = %s
            """
        ,(account_type_name,))

        row = cursor.fetchone()
        account_type_id = row[0]

        # Remove account from useraccount
        cursor.execute(
            """
            DELETE FROM useraccount
            where user_id = %s AND account_type_id = %s
            """
            ,(user_id,account_type_id))
        
        conn.commit()

        return_message =  {"success" : True}
    except psgSQL.DatabaseError as e:
        print_red("Some database error occured")
        print_red(e)
        print_red(traceback.format_exc())
        return_message = {"success" : False}
    except Exception as e:
        print_red("Some error occured")
        print_red(e)
        print_red(traceback.format_exc())
        return_message = {"success" : False}

    return return_message


def add_category_to_db(user_id : int, category : str):

    # Set of steps to do:
    # 1) Check if the category is already in the category table
    #    If the category table has the entry, get its key.
    # 2) If the category dont have the entry for the account type
    #    Insert into category the new id and get the key for the new entry
    # 3) Insert into categiry with user_id, category


    cursor = conn.cursor()
    return_data = None
    try:
        cursor.execute("""
            SELECT * 
            FROM category
            WHERE category_name = %s;
        """,(category,))

        rows = cursor.fetchall()

        primary_key = None
        
        if rows:    
            # If there is some row get its primary key
            print_green("The rows are not none")
            print(rows)
            primary_key = rows[0][0]
        else:
            print_green("The rows are none")
            print_green("Inerting a new entry")
            #If rows are none add a new entry to db
            cursor.execute(
                """
            INSERT INTO category(category_name)
            VALUES(%s)
                """,(category,))
            
            conn.commit()

            print_green("Getting the new primary key")
            # Now get the primary key
            cursor.execute("""
                SELECT * 
                FROM category
                WHERE category_name = %s;
            """,(category,))

            rows = cursor.fetchall()
            primary_key = rows[0][0]

        #Now add the row to usercategory
        cursor.execute("""
            INSERT INTO usercategory(user_id, category_id)
            VALUES (%s,%s)
        """,(user_id,primary_key))

        conn.commit()
    except Exception as e:
        print_red("Error Occured")
        print_red(e)
        print_red(traceback.format_exc())
        conn.rollback()
        return False

    cursor.close()
    return True

def get_category_id_from_db(category : str):
    """
    This function returns the id for a category passed in parameter.
    Returns none if no key found
    """

    cursor = conn.cursor()
    return_value = None

    try:
        cursor.execute("""
        SELECT * FROM category where category_name = %s
        LIMIT 1
        """,(category,))

        rows = cursor.fetchone()
        return_value = rows[0]
    except Exception as e:
        print_red("Error occured")
        print_red(e)
        conn.rollback()

    cursor.close()
    return return_value

def get_account_id_from_db(account_type_name : str):
    """
    This function returns the id for a category passed in parameter.
    Returns none if no key found
    """

    cursor = conn.cursor()
    return_value = None

    try:
        cursor.execute("""
        SELECT * FROM accounttype where account_type_name = %s
        LIMIT 1
        """,(account_type_name,))

        rows = cursor.fetchone()
        return_value = rows[0]
    except Exception as e:
        print_red("Error occured")
        print_red(e)
        conn.rollback()

    cursor.close()
    return return_value

# def get_filtered_transactions_from_db(json_data : dict , user_id):
def get_filtered_transaction_from_db(json_data : dict, user_id):
    # What we would do in this function is fetch data and apply queries on it as we go
    from pandas import DataFrame
    query_counter = 0
    query = f"""
        WITH q{0} AS (
        SELECT * 
        FROM transaction
        JOIN category 
            ON transaction.category_id = category.category_id
        JOIN accounttype
            ON transaction.account_type_id = accounttype.account_type_id
        WHERE user_id = {user_id}
        )
        """

    #1 Check if user has filtered on date

    #1.1) Check if user has filtered on both dates
    start_date = json_data.get("start_date")
    end_date = json_data.get("end_date")

    query_addition = """"""
    if( start_date != "" and end_date != ""):
        query_counter += 1
        query_addition = f"""
        ,q{query_counter} AS (
        SELECT * FROM q{query_counter - 1}
        WHERE transaction_date >= '{start_date}' AND transaction_date <= '{end_date}'
        )
        """

    # 1.2 if user has selected only start date
    elif (start_date != ""):
        query_counter += 1
        query_addition = f"""
        ,q{query_counter} AS (
        SELECT * FROM q{query_counter - 1}
        WHERE transaction_date >= '{start_date}'
        )
        """
    
    elif(end_date != ""):
        query_counter += 1
        query_addition = f"""
        ,q{query_counter} AS (
        SELECT * FROM q{query_counter - 1}
        WHERE transaction_date <= '{end_date}'
        )
        """

    #1.4 up until now we either will have a query_addition = some query or nothing
    # so just add it

    query += query_addition


    #2 Now build up query for category.
    query_addition = ""
    # 2.1 If category != "all", build up query else skip
    category = json_data.get("category")

    if ( category != "all" ):
        # Get category id from db
        category_id = get_category_id_from_db(category)

        query_counter += 1
        query_addition = f"""
        ,q{query_counter} AS (
        SELECT * FROM q{query_counter - 1}
        WHERE category_name = '{category}'
        )
        """
    
    query += query_addition

    query_addition = ""

    # 3 Now build query for account
    # 3.1 Do the same stuff as account
    account = json_data.get("account")
    if ( account != "all" ):
        query_counter += 1
        query_addition = f"""
        ,q{query_counter} AS (
        SELECT * FROM q{query_counter - 1}
        WHERE account_type_name = '{account}'
        )
        """
    
    query += query_addition

    #4 Now do the same stuff with amount as we did with date
    minimum_amount = float(json_data.get("minimum_amount"))
    maximum_amount = float(json_data.get("maximum_amount"))


    #4.1) Check if user has filtered on both amounts

    query_addition = """"""
    if( minimum_amount != 0 and maximum_amount != 0):
        query_counter += 1
        query_addition = f"""
        ,q{query_counter} AS (
        SELECT * FROM q{query_counter - 1}
        WHERE transaction_amount > {minimum_amount} AND transaction_amount < {maximum_amount}
        )
        """

    # 4.2 if user has selected only minimum amout
    elif (minimum_amount != 0):
        query_counter += 1
        query_addition = f"""
        ,q{query_counter} AS (
        SELECT * FROM q{query_counter - 1}
        WHERE transaction_amount > {minimum_amount}
        )
        """
    
    elif(maximum_amount != 0):
        query_counter += 1
        query_addition = f"""
        ,q{query_counter} AS (
        SELECT * FROM q{query_counter - 1}
        WHERE transaction_amount < {maximum_amount}
        )
        """

    #1.4 up until now we either will have a query_addition = some query or nothing
    # so just add it

    query += query_addition

    # Lastly filter everything from last with

    # ---Update needed here: join this to get category and accounts
    query += f"""
        SELECT 
        transaction_date as "Date",
        category_name as "Category",
        transaction_amount as "Amount",
        transaction_type as "Type",
        account_type_name as "Account"
        FROM
        q{query_counter}
        ORDER BY "Date" DESC
        LIMIT 15
    """
    print(query)

    #Final Step
    # Execute this query

    cursor = conn.cursor()
    df = None
    try:
        cursor.execute(query,())
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        df = DataFrame(data= rows, columns= column_names)
        print_green("We here")

    except psgSQL.DatabaseError as e:
        print_red("Data Base Error occured")
        print_red(e)
        print_red(traceback.format_exc())
        conn.rollback()
    except Exception as e:
        print_red("Error occured")
        print_red(e)
        print_red(traceback.format_exc())
        conn.rollback()

    cursor.close()
    return df


def get_filtered_transfer_transaction_from_db(json_data : dict, user_id):
    # What we would do in this function is fetch data and apply queries on it as we go
    from pandas import DataFrame
    query_counter = 1 #1 because we have already used q1 in first query

    # This will be initial query setting up some inital data
    query = f"""
            WITH q0 AS (

                SELECT 
                    transaction_name,
                    user_id,
                    transaction_amount,
                    transaction_date,
                    source_account_type_id AS "source_id",
                    account_type_name AS "source_acc",
                    destination_account_type_id AS "dest_id",
                    transaction_type
                FROM transaction
                
                JOIN
                    accounttype
                    ON accounttype.account_type_id = transaction.source_account_type_id
                    
                WHERE transaction_type = 'transfer' AND user_id = {user_id}
            ),
            q1 AS(

                SELECT 
                    transaction_name,
                    transaction_amount,
                    transaction_date,
                    source_acc,
                    account_type_name as "dest_acc"
                FROM q0
                JOIN accounttype
                ON q0.dest_id = accounttype.account_type_id
            )
            """
    #1 Check if user has filtered on date

    #1.1) Check if user has filtered on both dates
    start_date = json_data.get("start_date")
    end_date = json_data.get("end_date")

    query_addition = """"""
    if( start_date != "" and end_date != ""):
        query_counter += 1
        query_addition = f"""
        ,q{query_counter} AS (
        SELECT * FROM q{query_counter - 1}
        WHERE transaction_date >= '{start_date}' AND transaction_date <= '{end_date}'
        )
        """

    # 1.2 if user has selected only start date
    elif (start_date != ""):
        query_counter += 1
        query_addition = f"""
        ,q{query_counter} AS (
        SELECT * FROM q{query_counter - 1}
        WHERE transaction_date >= '{start_date}'
        )
        """
    
    elif(end_date != ""):
        query_counter += 1
        query_addition = f"""
        ,q{query_counter} AS (
        SELECT * FROM q{query_counter - 1}
        WHERE transaction_date <= '{end_date}'
        )
        """

    #1.4 up until now we either will have a query_addition = some query or nothing
    # so just add it

    query += query_addition


    #2 Now build up query for amount
    minimum_amount = float(json_data.get("minimum_amount"))
    maximum_amount = float(json_data.get("maximum_amount"))


    #2.1) Check if user has filtered on both amounts

    query_addition = """"""
    if( minimum_amount != 0 and maximum_amount != 0):
        query_counter += 1
        query_addition = f"""
        ,q{query_counter} AS (
        SELECT * FROM q{query_counter - 1}
        WHERE transaction_amount > {minimum_amount} AND transaction_amount < {maximum_amount}
        )
        """

    # 2.2 if user has selected only minimum amout
    elif (minimum_amount != 0):
        query_counter += 1
        query_addition = f"""
        ,q{query_counter} AS (
        SELECT * FROM q{query_counter - 1}
        WHERE transaction_amount > {minimum_amount}
        )
        """
    
    elif(maximum_amount != 0):
        query_counter += 1
        query_addition = f"""
        ,q{query_counter} AS (
        SELECT * FROM q{query_counter - 1}
        WHERE transaction_amount < {maximum_amount}
        )
        """

    #2.3 up until now we either will have a query_addition = some query or nothing
    # so just add it

    query += query_addition

    #3 Now filter on account
    query_counter += 1
    query_addition =    f"""
    ,q{query_counter} AS (
    SELECT * FROM q{query_counter - 1}
    WHERE 
        source_acc = '{json_data["from_dropdown"]}'
        AND dest_acc = '{json_data["to_dropdown"]}'
        )
    """
    # Lastly filter everything from last with

    query += query_addition
    print_green("we here")
    
    query += f"""
        SELECT 
        transaction_name AS "Name",
        source_acc AS "From",
        dest_acc AS "To",
        transaction_amount as "Amount",
        transaction_date as "Date"
        FROM
        q{query_counter}
        ORDER BY "Date"
        LIMIT 15
    """
    print(query)

    #Final Step
    # Execute this query

    cursor = conn.cursor()
    try:
        cursor.execute(query,())
        rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        df = DataFrame(data= rows, columns= column_names)
        print_green("We here")
    
    except psgSQL.DatabaseError as e:
        print_red("Database Error occured")
        print_red(e)
        print_red(traceback.format_exc())

        conn.rollback()
    except Exception as e:
        print_red("Error occured")
        print_red(e)
        print_red(traceback.format_exc())

    cursor.close()
    return df



def add_user_transaction_to_db(json_data , user_id):
    """
    This function adds transaction to transaction.
    It works in following way:

    1) if transaction_type = "expense":
            1.1) Check if transaction amount is less than account amount
                    return {success : false , message : }
                else:
                    add the transaction.
    
    2) if transction_type = "income"
            2.1) Add the transaction to the transaction_table
            2.2) Add the amount to the accounts table
    
    3) If transaction_type = "transfer"
            3.1) Check if transaction amount is less than account amount
                    return {success : false , message : }
            3.2) Else:
                Add the transaction to the transaction table

            3.3) Subtract the amount from from_account
            3.4) Add the amount to to_account.

            Json Request Recieved : {'transaction_name': 'Spotify', 'amount_input': '350.97',
              'transaction_date': '2025-05-23', 'transaction_type': 'expense', 'account_type': 'cash',
              'category_dropdown': 'travel', 'from_dropdown': 'cash', 'to_dropdown': 'cash'}
    """

    cursor = conn.cursor()

    transaction_type = json_data.get("transaction_type")
    transaction_name = json_data.get("transaction_name")
    transaction_date = json_data.get("transaction_date")
    account_type_name = json_data.get("account_type")
    account_type_id = get_account_id_from_db(account_type_name)
    transaction_amount = float(json_data.get("amount_input"))

    try:
        # 1) transaction_type = "expense"
        if transaction_type == "expense":

            #1.1 check if transaction_amount is less than current_amount in user account
            cursor.execute("""
                SELECT * FROM useraccount
                WHERE user_id = %s AND account_type_id = %s
                """, (user_id , account_type_id))
            
            rows = cursor.fetchone()
            current_amount = float(rows[2])

            if (current_amount < transaction_amount):
                return {"success" : False, "message" : "Transaction amount exceeds current amount"}
            
            # 1.2 if it is not true add the transaction to the transaction table
            category_id = get_category_id_from_db(json_data.get("category_dropdown"))
            cursor.execute(
                """
                INSERT INTO 
                    transaction(transaction_name , user_id , account_type_id , category_id, transaction_amount , transaction_date , transaction_type)
                    VALUES(%s,%s,%s,%s,%s,%s,%s)
                """
            ,(transaction_name, user_id , account_type_id, category_id,transaction_amount, transaction_date,"expense"))

            # 1.3 Subtract the amount from useraccount
            cursor.execute(
                """
                UPDATE useraccount
                    SET current_amount = current_amount - %s
                    WHERE user_id = %s AND account_type_id = %s
                """
            ,(transaction_amount, user_id, account_type_id))

            # If we are here transaction has been added

        #2 If transaction_type = transfer
        elif transaction_type == "transfer":
            # 2.1) Check if two and from are same
            from_account = json_data.get("from_dropdown")
            to_account = json_data.get("to_dropdown")

            source_account_type_id = get_account_id_from_db(from_account)
            destination_account_type_id = get_account_id_from_db(to_account)

            if from_account == to_account:
                return {"success" : False, "message" : "To and From accounts cannot be same"}
            
            # 2.2) Check if transaction_amount is less than account_amount
            cursor.execute("""
                SELECT * FROM useraccount
                WHERE user_id = %s AND account_type_id = %s
                """, (user_id , source_account_type_id))
            
            rows = cursor.fetchone()
            current_amount = float(rows[2])

            if (current_amount < transaction_amount):
                return {"success" : False, "message" : "Transaction amount exceeds Current amount"}
            
            # We have handled both Edge Cases
            # 2.3) Add transaction to transaction_table

            cursor.execute(
                """
                INSERT INtO 
                transaction(transaction_name , user_id, transaction_amount , transaction_date,source_account_type_id , destination_account_type_id, transaction_type)
                VALUES(%s,%s,%s,%s,%s,%s,%s)
                """
                , (transaction_name, user_id, transaction_amount, transaction_date, source_account_type_id, destination_account_type_id , transaction_type))
            
            # 2.4) Subtract amount from 'from_account' and add it to 'to_account'
            cursor.execute(
                """
                UPDATE useraccount
                    SET 
                        current_amount = current_amount - %s
                    WHERE 
                        user_id = %s AND account_type_id = %s
                """
                , ( transaction_amount , user_id , source_account_type_id ) )
            
            # Add the amount to 'to_account'
            cursor.execute(
                """
                UPDATE useraccount
                    SET 
                        current_amount = current_amount + %s
                    WHERE 
                        user_id = %s AND account_type_id = %s
                """
                , ( transaction_amount , user_id , destination_account_type_id ) )
            

            # If we are here we have have successfull

        # 3 if transaction_type = "income"
        elif transaction_type == "income":
            print_green("Inside if (transaction_type == 'income'")
            # 3.1 Add to transaction_table
            cursor.execute(
            """
            INSERT INTO 
            Transaction(transaction_name, user_id , account_type_id , transaction_amount , transaction_date , transaction_type )
            VALUES(%s,%s,%s,%s,%s,%s)
            """
            ,(transaction_name , user_id , account_type_id, transaction_amount , transaction_date ,transaction_type) )

            # 3.2 Add the amount to current_amount
            cursor.execute(
                """
                UPDATE useraccount
                    SET 
                        current_amount = current_amount + %s
                    WHERE 
                        user_id = %s AND account_type_id = %s
                """
                , ( transaction_amount , user_id , account_type_id ) )
        
        else:
            return {"success" : False, "message" : "transaction_type invalid (Internal Server Error)"}
    
    except psgSQL.DatabaseError as E:
        print_red("DataBase Error occured")
        print_red(E)
        print_red(traceback.format_exc())
        return {"success" : False , "message" : "Data Base Error Occured"}
    except Exception as E:
        print_red("Error Occured")
        print_red(E)
        print_red(traceback.format_exc())
        return {"success" : False , "message" : "Some internal server error occured"}

    # we have done everything perfectly
    conn.commit()
    cursor.close()
    return {"success" : True , "message" : "Transaction Added Successfully"}


def add_budget_in_db(user_id, json_data):
    budget_name = json_data["budget_name"]
    budget_type = json_data["budget_type"]
    category = json_data["category"]
    amount = json_data["amount"]

    category_id = get_category_id_from_db(category=category)

    cursor = conn.cursor()

    try:
        cursor.execute("""
        INSERT INTO BUDGET(budget_type,category_id,user_id, budget_amount, budget_name)
        VALUES(%s,%s,%s,%s,%s)
        """, (budget_type, category_id , user_id, amount, budget_name) )

        conn.commit()
        return {"success" : True , "message" : "Successfully Added Budget"}
    except psgSQL.DatabaseError as E:
        print_red("DataBase Error occured")
        print_red(E)
        print_red(traceback.format_exc())
        return {"success" : False , "message" : "Data Base Error Occured"}
    except Exception as E:
        print_red("Error Occured")
        print_red(E)
        print_red(traceback.format_exc())
        return {"success" : False , "message" : "Some internal server error occured"}
    finally:
        cursor.close()