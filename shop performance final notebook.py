# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# dependencies = [
#   "openpyxl",
# ]
# ///
import pandas as pd
orders_final = pd.read_csv("/Workspace/Users/arreyeva31@gmail.com/orders_final.csv")

# COMMAND ----------

orders_final.head()


# COMMAND ----------

orders_final.shape

# COMMAND ----------

###creating revenue column
orders_final['revenue'] = orders_final['Quantity'] * orders_final['UnitPrice']*(1-orders_final['Discount'])


# COMMAND ----------

orders_final.shape

# COMMAND ----------

# MAGIC %md
# MAGIC here we calculated total Revenue using qty*unit price *(1-discount)
# MAGIC this now increase our number of columns to 19

# COMMAND ----------

orders_final.head()

# COMMAND ----------

orders_final.columns

# COMMAND ----------

# DBTITLE 1,converting the orderDate to date
import pandas as pd
orders_final['OrderDate'] = pd.to_datetime(orders_final['OrderDate'], errors='coerce')
orders_final['PaymentDate'] = pd.to_datetime(orders_final['PaymentDate'], errors='coerce')
orders_final['SignupDate'] = pd.to_datetime(orders_final['SignupDate'], errors='coerce')



# COMMAND ----------

orders_final.head()

# COMMAND ----------

# DBTITLE 1,converting year &month for orderdate
###year and month columns
orders_final['year'] = orders_final['OrderDate'].dt.year
orders_final['month'] = orders_final['OrderDate'].dt.month
orders_final['OrderMonthName'] = orders_final['OrderDate'].dt.month_name()

# COMMAND ----------

orders_final.head()

# COMMAND ----------

# DBTITLE 1,converting year & month for paymentdate
orders_final['paymentYear'] = orders_final['PaymentDate'].dt.year
orders_final['paymentMonth'] = orders_final['PaymentDate'].dt.month
orders_final['paymentMonthName'] = orders_final['PaymentDate'].dt.month_name()
orders_final.head()

# COMMAND ----------

# DBTITLE 1,final  orders_table
orders_final.shape

# COMMAND ----------

# MAGIC %md
# MAGIC finally our clean or final table has 50000 rows and 25 columns

# COMMAND ----------

# save to filestore
orders_final.to_csv("/Workspace/Users/arreyeva31@gmail.com/orders_final_25columns.csv", index=False)
print("saved")

# COMMAND ----------

# MAGIC %md
# MAGIC ### first revenue Analysis

# COMMAND ----------

## checking how many are not real sales
print(orders_final['Status'].value_counts())
print(orders_final['PaymentStatus'].value_counts())



# COMMAND ----------

# MAGIC %md
# MAGIC Cancelled orders this produces negative revenue because products were not shipped, orders was cancelled before shippment.No product left the warehouse' therefore no money left the bank,ifwe count it then we are lieing about sales. Returned orders this produces 0 revenue or negative revenue because products went out ,then came back and refunds were made so Net Money = 0 but for stock analysis we include them as returned UNPAID ORDERS when payments status = Unpaid/failed/ pending means we have not received money yet,in real accounting we only recognized revenue when money is paid or Payment status = PAID,untill then it is just potential demand not sales

# COMMAND ----------

# DBTITLE 1,Analizing real Revenue
#Real revenue = only completed + paid
real_sales = orders_final[
    (orders_final['Status'] == 'Completed') & 
    (orders_final['PaymentStatus'] == 'Paid')
]

lost_sales = orders_final[
    ~orders_final.index.isin(real_sales.index)
]

print(f"Total orders:{len(orders_final)}")
print(f"Real sales for revenue: {len(real_sales)} = {len(real_sales)/len(orders_final)*100:.1f}%")
print(f"Lost sales:{len(lost_sales)}")


# COMMAND ----------

## calculating clean revenue corectly
real_sales['revenue'] = real_sales['Quantity'] * real_sales['UnitPrice']*(1-real_sales['Discount'])
print(f"Total revenue sum: {real_sales['revenue'].sum():,.0f}")

# COMMAND ----------

# MAGIC %md
# MAGIC Final Analysis is the total revenue is 2,979893 from 45,996 completed & paid orders. i excluded 4,004 orders (cancelled 2,472 + Returned 1,532/ Failed 1,924 + Refunded 1,507) because they are not cash received.

# COMMAND ----------

# saving the Real sales for Excel
real_sales.to_csv('/Workspace/Users/arreyeva31@gmail.com/Real_Sales_for_excel.csv', index=False)
print("saved")

# COMMAND ----------

# DBTITLE 1,saving orders final as excel file
df = spark.table("orders_final")


# COMMAND ----------

#conert to pandas for excel
pdf = df.toPandas()
print(f"loaded: {len(pdf)} rows * {len(pdf.columns)} columns")

# COMMAND ----------

# DBTITLE 1,Install openpyxl for Excel export
# MAGIC %pip install openpyxl

# COMMAND ----------

## save as excel file
pdf.to_excel("/Workspace/Users/arreyeva31@gmail.com/Orders_Final.xlsx", index=False)
print("saved as Orders_Final.xlsx in your workspace - Go to /Workspace/Users/arreyeva31@gmail.com/ to download")


# COMMAND ----------

##installing pip
dbutils.library.restartPython()

# COMMAND ----------

df = spark.table("orders_final")
pdf = df.toPandas()
print(f"loaded: {len(pdf)} rows * {len(pdf.columns)} columns")
pdf.to_excel("/Workspace/Users/arreyeva31@gmail.com/Orders_Final.xlsx", index=False)
print("saved as Orders_Final.xlsx in your workspace - Go to /Workspace/Users/arreyeva31@gmail.com/ to download")

# COMMAND ----------

print(pdf.columns.tolist())