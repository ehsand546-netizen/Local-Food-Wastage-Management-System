"""
queries.py
------------------
This script runs our SQL analysis queries against the food_wastage database
and prints the results.
"""

import sqlite3
import pandas as pd
import os

db_path = os.path.join("database", "food_wastage.db")
conn = sqlite3.connect(db_path)

# ===========================================================
# QUERY 1: Providers and receivers count per city
# ===========================================================
print("=" * 60)
print("QUERY 1: Providers and Receivers count per city")
print("=" * 60)

query1_providers = """
SELECT City, COUNT(*) AS Provider_Count
FROM providers
GROUP BY City
ORDER BY Provider_Count DESC
"""
df1a = pd.read_sql_query(query1_providers, conn)
print("\nProviders per city:")
print(df1a)

query1_receivers = """
SELECT City, COUNT(*) AS Receiver_Count
FROM receivers
GROUP BY City
ORDER BY Receiver_Count DESC
"""
df1b = pd.read_sql_query(query1_receivers, conn)
print("\nReceivers per city:")
print(df1b)

# ===========================================================
# QUERY 2: Provider type contributing the most food
# ===========================================================
print("\n" + "=" * 60)
print("QUERY 2: Provider type contributing the most food")
print("=" * 60)

query2 = """
SELECT Provider_Type, SUM(Quantity) AS Total_Quantity
FROM food_listings
GROUP BY Provider_Type
ORDER BY Total_Quantity DESC
"""
df2 = pd.read_sql_query(query2, conn)
print(df2)

# ===========================================================
# QUERY 3: Provider contacts in Mumbai
# ===========================================================
print("\n" + "=" * 60)
print("QUERY 3: Provider contacts in Mumbai")
print("=" * 60)

query3 = """
SELECT Name, Type, Address, Contact
FROM providers
WHERE City = 'Mumbai'
"""
df3 = pd.read_sql_query(query3, conn)
print(df3)

# ===========================================================
# QUERY 4: Top receivers by number of claims
# ===========================================================
print("\n" + "=" * 60)
print("QUERY 4: Top receivers by number of claims")
print("=" * 60)

query4 = """
SELECT r.Name, COUNT(c.Claim_ID) AS Total_Claims
FROM claims c
JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
GROUP BY r.Name
ORDER BY Total_Claims DESC
LIMIT 10
"""
df4 = pd.read_sql_query(query4, conn)
print(df4)

# ===========================================================
# QUERY 5: Total quantity of food available (all providers)
# ===========================================================
print("\n" + "=" * 60)
print("QUERY 5: Total quantity of food available (all providers)")
print("=" * 60)

query5 = """
SELECT SUM(Quantity) AS Total_Food_Available
FROM food_listings
"""
df5 = pd.read_sql_query(query5, conn)
print(df5)

# ===========================================================
# QUERY 6: City with highest number of food listings
# ===========================================================
print("\n" + "=" * 60)
print("QUERY 6: City with highest number of food listings")
print("=" * 60)

query6 = """
SELECT Location AS City, COUNT(*) AS Listing_Count
FROM food_listings
GROUP BY Location
ORDER BY Listing_Count DESC
"""
df6 = pd.read_sql_query(query6, conn)
print(df6)

# ===========================================================
# QUERY 7: Most common food types
# ===========================================================
print("\n" + "=" * 60)
print("QUERY 7: Most common food types")
print("=" * 60)

query7 = """
SELECT Food_Type, COUNT(*) AS Count
FROM food_listings
GROUP BY Food_Type
ORDER BY Count DESC
"""
df7 = pd.read_sql_query(query7, conn)
print(df7)

# ===========================================================
# QUERY 8: Number of claims per food item
# ===========================================================
print("\n" + "=" * 60)
print("QUERY 8: Number of claims per food item")
print("=" * 60)

query8 = """
SELECT f.Food_Name, COUNT(c.Claim_ID) AS Times_Claimed
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
GROUP BY f.Food_Name
ORDER BY Times_Claimed DESC
"""
df8 = pd.read_sql_query(query8, conn)
print(df8)
# ===========================================================
# QUERY 9: Provider with highest number of successful claims
# ===========================================================
print("\n" + "=" * 60)
print("QUERY 9: Provider with most successful (Completed) claims")
print("=" * 60)

query9 = """
SELECT p.Name, COUNT(c.Claim_ID) AS Completed_Claims
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
JOIN providers p ON f.Provider_ID = p.Provider_ID
WHERE c.Status = 'Completed'
GROUP BY p.Name
ORDER BY Completed_Claims DESC
LIMIT 10
"""
df9 = pd.read_sql_query(query9, conn)
print(df9)

# ===========================================================
# QUERY 10: Percentage of claims - Completed vs Pending vs Cancelled
# ===========================================================
print("\n" + "=" * 60)
print("QUERY 10: Claim status percentage breakdown")
print("=" * 60)

query10 = """
SELECT Status,
       COUNT(*) AS Count,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) AS Percentage
FROM claims
GROUP BY Status
"""
df10 = pd.read_sql_query(query10, conn)
print(df10)

# ===========================================================
# QUERY 11: Average quantity of food claimed per receiver
# ===========================================================
print("\n" + "=" * 60)
print("QUERY 11: Average quantity of food claimed per receiver")
print("=" * 60)

query11 = """
SELECT r.Name, AVG(f.Quantity) AS Avg_Quantity_Claimed
FROM claims c
JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
JOIN food_listings f ON c.Food_ID = f.Food_ID
GROUP BY r.Name
ORDER BY Avg_Quantity_Claimed DESC
LIMIT 10
"""
df11 = pd.read_sql_query(query11, conn)
print(df11)
# ===========================================================
# QUERY 12: Which meal type is claimed the most?
# ===========================================================
print("\n" + "=" * 60)
print("QUERY 12: Most claimed meal type")
print("=" * 60)

query12 = """
SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
GROUP BY f.Meal_Type
ORDER BY Total_Claims DESC
"""
df12 = pd.read_sql_query(query12, conn)
print(df12)

# ===========================================================
# QUERY 13: Total quantity of food donated by each provider
# ===========================================================
print("\n" + "=" * 60)
print("QUERY 13: Total quantity donated by each provider")
print("=" * 60)

query13 = """
SELECT p.Name, SUM(f.Quantity) AS Total_Donated
FROM food_listings f
JOIN providers p ON f.Provider_ID = p.Provider_ID
GROUP BY p.Name
ORDER BY Total_Donated DESC
LIMIT 10
"""
df13 = pd.read_sql_query(query13, conn)
print(df13)

# ===========================================================
# QUERY 14: Food items nearing expiry (within next 5 days
#           from the latest date in our data)
# ===========================================================
print("\n" + "=" * 60)
print("QUERY 14: Food items nearing expiry")
print("=" * 60)

query14 = """
SELECT Food_Name, Quantity, Expiry_Date, Location
FROM food_listings
WHERE Expiry_Date <= (
    SELECT DATE(MAX(Expiry_Date), '-15 days') FROM food_listings
)
ORDER BY Expiry_Date ASC
LIMIT 15
"""
df14 = pd.read_sql_query(query14, conn)
print(df14)

# ===========================================================
# QUERY 15: Cities with the most claims (demand hotspots)
# ===========================================================
print("\n" + "=" * 60)
print("QUERY 15: Cities with the most claims")
print("=" * 60)

query15 = """
SELECT f.Location AS City, COUNT(c.Claim_ID) AS Total_Claims
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
GROUP BY f.Location
ORDER BY Total_Claims DESC
"""
df15 = pd.read_sql_query(query15, conn)
print(df15)
conn.close()