import pandas as pd
import pymysql
from sqlalchemy import create_engine

file = pd.read_csv("customer_shopping_behavior.csv")

# to get the top 5 values including the headers
print(file.head())

# to get the detail info about the dataset
print(file.info())

# to get the statistical info about the dataset
print(file.describe(include="all"))

# to check no of null values present in the dataset
# print(file.isnull().sum())

# Missing Review Rating count : 37

file["Review Rating"] = file.groupby("Category")["Review Rating"].transform(lambda x: x.fillna(x.median()))

# update the all column names to be in lower case with the underscore sepration
file.columns = file.columns.str.lower().str.replace(" ", "_")

# renaming the purchase_amount_(usd) to purchase_amount_usd to make it more readable
file.rename(columns={"purchase_amount_(usd)": "purchase_amount_usd"}, inplace=True)

# create 2 more columns which of age and age_group for more precise detailings and getting insights from the dataset, we mainly have 4 age_group : ["young_adult","adult","middle_age","seniors"]

labels = ["young_adult","adult","middle_age","seniors"]
file["age_group"] = pd.qcut(file["age"], q=4, labels=labels,duplicates='drop')

# create a column of puchase_frequency_days, as we currently have a column of frequency_of_purchases, for better analysis and getting insights from the dataset and converting textual data into numerical format
frequency_mapping = {
    "Fortnightly" : 14,
    "Weekly" : 7,
    "Annually" : 365,
    "Quarterly" : 90,
    "Bi-Weekly" : 14,
    "Monthly" : 30,
    "Every 3 Months" : 90,
}

file["purchase_frequency_days"] = file["frequency_of_purchases"].map(frequency_mapping)

#  remove promo_code_used column
file.drop("promo_code_used", axis=1, inplace=True)

# MySQL credentials
host = "127.0.0.1"
user = "root"
password = "ubaid725061"
port = 3306
database = "customer_trends_data_analysis"

try:
    print("Connecting to MySQL server...")

    # connect to mysql server
    conn = pymysql.connect(
        host=host,
        user=user,
        password=password,
        port=port
    )

    print("Connected successfully")

    cursor = conn.cursor()

    # create database
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS {database}"
    )

    print("Database created successfully")

    # select database
    cursor.execute(f"USE {database}")

    # show tables
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()

    print("Tables:", tables)

    # sqlalchemy engine using pymysql
    engine = create_engine(
        f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    )

    # load dataframe into mysql table
    file.to_sql(
        name="customer_data",
        con=engine,
        if_exists="replace",
        index=False
    )

    print("DataFrame loaded successfully")

except Exception as err:
    print("Error:", type(err).__name__, err)

finally:
    if 'conn' in locals():
        conn.close()
        print("MySQL connection closed")