import pymongo
import pandas as pd
# Connect to MongoDB (local or remote)
client = pymongo.MongoClient("mongodb://localhost:27017/")  # Change URL for remote DB

# Select a database
db = client["finance-tracking-db"]

# Select a collection
user_collection = db["user"]
account_type_collection = db["account_type"]
transaction_collection = db["transaction"]
category_collection = db["category"]
count_collection = db["count"]


def get_recent_transactions_as_dataframe(user_id, limit):
    """
    This function takes in user_id and returns its top 5 transactions as a pandas DataFrame
    """
    import pandas as pd

    query_result = transaction_collection.aggregate(
                pipeline = [
                    { "$match" : {
                                            "user_id" : user_id
                                                    }
                            },
                    { "$lookup" : {
                                    "from" : "account_type",
                                    "localField" : "account_id",
                                    "foreignField" : "_id" ,
                                    "as" : "account"
                                                } 
                        },
                    { "$unwind" : "$account"
                        },
                    { "$lookup" : {
                                    "from" : "category",
                                    "localField" : "category_id",
                                    "foreignField" : "_id" ,
                                    "as" : "category"
                                                } 
                        },
                    { "$unwind" : "$category"
                        },
                    {
                            "$project" : { "_id" : 0 , "transaction_name" : 1, "transaction_type"  : 1,
                                        "transaction_amount" : 1, "transaction_date" : 1 , 
                                    "account_type" : "$account.account_type_name", "category_type" : "$category.category_name"}
                        },
                    {
                            "$sort" : { "transaction_date" : -1 }
                        },
                    { "$limit" : limit
                        }
                ]
            )

    if query_result is None:
        return None
    
    
    return_value = pd.DataFrame(data= [doc for doc in query_result]) 

    return return_value

print(get_recent_transactions_as_dataframe(10,10))
# { "$match" : {
#       					 "user_id" : 1
# 								}
# 		},
# { "$lookup" : {
#                 "from" : "account_type",
#                 "localField" : "account_id",
#                 "foreignField" : "_id" ,
#                 "as" : "account"
#                             } 
#     },
# { "$unwind" : "$account"
#     },
# { "$lookup" : {
#                 "from" : "category",
#                 "localField" : "category_id",
#                 "foreignField" : "_id" ,
#                 "as" : "category"
#                             } 
#     },
# { "$unwind" : "$category"
#     },
# {
#         "$project" : { "_id" : 0 , "transaction_name" : 1, "transaction_type"  : 1,
#                     "transaction_amount" : 1, "transaction_date" : 1 , 
#                 "account_type" : "$account.account_type_name", "category_type" : "$category.category_name"}
#     },
# {
#         "$sort" : { "transaction_date" : -1 }
#     },
# { "$limit" : 10
#     }