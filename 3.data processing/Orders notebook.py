# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC ### _import libries_

# COMMAND ----------

import pandas as pd
import numpy as np

# COMMAND ----------

# MAGIC %md
# MAGIC ### _Data Ingestion_

# COMMAND ----------

orders=spark.table("workspace.default._orders")
orders=orders.toPandas()
display(orders)

# COMMAND ----------

###whats polluted
print(orders.columns.tolist())

# COMMAND ----------

##keeping the real order columns
orders=orders[['OrderID','CustomerID','OrderDate','ProductID','Quantity','Discount','PaymentMethod','Status']]

# COMMAND ----------

# MAGIC %md
# MAGIC ### _Exploratory Data Analysis_

# COMMAND ----------

# basic info
print("shape;",orders.shape)

# COMMAND ----------

# missing values
print("missing values:",orders.isnull().sum())

# COMMAND ----------

# MAGIC %md
# MAGIC too many issues here,orderdate 35 missing,
# MAGIC qty missing 80,
# MAGIC 221 discount missing and 452 payments method

# COMMAND ----------

#data types
print("data types:",orders.dtypes)

# COMMAND ----------

#unique values
print("unique values:",orders.nunique())

# COMMAND ----------

# checking for duplicates
print("duplicates:",orders.duplicated().sum())

# COMMAND ----------

# MAGIC %md
# MAGIC we realize 120 duplicates
# MAGIC

# COMMAND ----------

# checking status
print(orders["Status"].value_counts())


# COMMAND ----------

# payment methods
print(orders["PaymentMethod"].value_counts(dropna=False))



# COMMAND ----------

# MAGIC %md
# MAGIC we noticed 452 payments without a method

# COMMAND ----------

# checking quantity
print(orders["Quantity"].describe())

# COMMAND ----------

# checking invalid quantities
print((orders["Quantity"] <= 0).sum())

# COMMAND ----------

# MAGIC %md
# MAGIC we also noticed a 25 zero quantities which is not normal

# COMMAND ----------

# DBTITLE 1,Discount Analysis
print(orders["Discount"].describe())

# COMMAND ----------

print(orders["Discount"].value_counts(dropna=False))

# COMMAND ----------

# MAGIC %md
# MAGIC discount values ranges from 0% to 30%

# COMMAND ----------

# DBTITLE 1,date range
# checking date range
print (orders["OrderDate"].dropna().min())

# COMMAND ----------

# checking latest date
print (orders["OrderDate"].dropna().max())

# COMMAND ----------

# MAGIC %md
# MAGIC ### _Data Cleaning_

# COMMAND ----------

# DBTITLE 1,Cleaning Order ID
# removing duplicates
orders = orders.drop_duplicates(
    subset="OrderID", keep="first"
)

# COMMAND ----------

# checking size again
print("shape:",orders.shape)

# COMMAND ----------

# MAGIC %md
# MAGIC Now we have 50000 unique orders

# COMMAND ----------

# DBTITLE 1,Cleaning OrderDate
# cleaning OrderDate
orders["OrderDate"] = pd.to_datetime(orders["OrderDate"])

# COMMAND ----------

# DBTITLE 1,cleaning Quantity
# converting invalid values to missing
orders.loc[
    orders["Quantity"]<=0,
    "Quantity"
    ]=np.nan

# COMMAND ----------

# MAGIC %md
# MAGIC ivalid quantities were those quantities less than zroes or egative quantities

# COMMAND ----------

# checking the outcome
print(orders["Quantity"].isnull().sum())

# COMMAND ----------

# MAGIC %md
# MAGIC there will now be 105 missing quantities which we cannot guess

# COMMAND ----------

# DBTITLE 1,discount checks
# checking for invalid discount
(orders["Discount"]>1).sum()

# COMMAND ----------

# MAGIC %md
# MAGIC no invalid discounts,but we still have 221 missing discounts and we cant assume them to be 0 so we just leave it as such
# MAGIC

# COMMAND ----------

# DBTITLE 1,cleaning payments method
# converting missing payment method to UNKNOWN
orders["PaymentMethod"] = orders["PaymentMethod"].fillna("Unknown")

# COMMAND ----------

# checking the outcome
print(orders["PaymentMethod"].isnull().sum())

# COMMAND ----------

# DBTITLE 1,reading the final clean payment table
# checking the final shape
print("shape:",orders.shape)

# COMMAND ----------

## final order check
print("shape:",orders.shape)
print(orders["OrderDate"].isnull().sum())
print(orders["Quantity"].isnull().sum())
print(orders["Discount"].isnull().sum())
print(orders["PaymentMethod"].value_counts())
print(orders["Status"].value_counts())

# COMMAND ----------

import pandas as pd
import os
customers_clean = pd.read_csv('customers_clean.csv')

# COMMAND ----------

print(customers_clean.head())

# COMMAND ----------

#checkcustomerID links
orders["CustomerID"].isin(customers_clean["CustomerID"]).value_counts()

# COMMAND ----------

# MAGIC %md
# MAGIC this results means 30 orders have a customerID that doesnot exist in customers

# COMMAND ----------

# DBTITLE 1,finding the broken customer ID
orders.loc[orders["CustomerID"].isin(customers_clean["CustomerID"]
),"CustomerID"].unique()

# COMMAND ----------

orders.loc[~orders["CustomerID"].isin(customers_clean["CustomerID"]), "CustomerID"].unique()

# COMMAND ----------

# MAGIC %md
# MAGIC

# COMMAND ----------

import pandas as pd
products_clean = pd.read_csv('products_clean.csv')


# COMMAND ----------

# checking orderID links
orders["ProductID"].isin(products_clean["ProductID"]).value_counts()


# COMMAND ----------

#reading clean table
orders = pd.read_csv('orders_clean.csv')
orders.head()
orders["OrderDate"] = pd.to_datetime(orders["OrderDate"])
orders["SignupDate"] = pd.to_datetime(orders["SignupDate"

# COMMAND ----------

# MAGIC %md
# MAGIC ### _### joining tables_

# COMMAND ----------

# DBTITLE 1,joining orders & Customers
##joining orders and customers_clean
orders = orders.merge(customers_clean, how = "left", on = "CustomerID")

# COMMAND ----------

##chec orders shape
orders.shape

# COMMAND ----------

### printing columns
orders.columns

# COMMAND ----------

# MAGIC %md
# MAGIC Here we are reading the new column names which are now 12 
# MAGIC

# COMMAND ----------

##checking first 5 rows
orders.head()


# COMMAND ----------

## reading products_clean
products_clean = pd.read_csv('products_clean.csv')
products_clean.head()

# COMMAND ----------

# DBTITLE 1,joining orders & products
orders = orders.merge(products_clean, how = "left", on = "ProductID")

# COMMAND ----------

##reading orders shape
orders.shape

# COMMAND ----------

##first 5 rows
orders.head()

# COMMAND ----------

# MAGIC %md
# MAGIC

# COMMAND ----------

# DBTITLE 1,joining orders and payments table
##reading payments table
payments_clean = pd.read_csv('payments_clean.csv')

# COMMAND ----------

##read payments first 5 rows
payments_clean.head()

# COMMAND ----------

##joing orders & payments
orders = orders.merge(payments_clean, how = "left", on = "OrderID")

# COMMAND ----------

##reading new order table
orders.shape

# COMMAND ----------

orders.head()

# COMMAND ----------

# DBTITLE 1,final column names of the orders table
##checking column names
orders.columns

# COMMAND ----------

# MAGIC %md
# MAGIC After having completed to joing all 4 tables together this this the final outcomes of 50000 rows and 18 columns

# COMMAND ----------

# saving final orders table
orders.to_csv('orders_final.csv', index = False)
print("orders_final.csv saved")

# COMMAND ----------

orders.shape

# COMMAND ----------

##saving using spark
spark.createDataFrame(orders).write.mode("overwrite").saveAsTable("orders_final")

print("orders_final saved as table")