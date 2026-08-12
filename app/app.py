"""
app.py - Local Food Wastage Management System
Complete Streamlit dashboard with filters, CRUD, queries, and charts.
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os




db_path = os.path.join("database", "food_wastage.db")

def get_connection():
    return sqlite3.connect(db_path, check_same_thread=False)

def run_query(query, params=None):
    conn = get_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df

def run_action(query, params=None):
    """For INSERT/UPDATE/DELETE"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params or ())
    conn.commit()
    conn.close()


# Page config

st.set_page_config(page_title="Food Wastage Management", layout="wide")
st.title("🍲 Local Food Wastage Management System")


# Sidebar navigation

page = st.sidebar.radio("Navigate", ["Home & Filters", "SQL Queries & Insights", "Manage Listings (CRUD)", "Charts"])


# PAGE 1: Home & Filters

if page == "Home & Filters":
    st.header("Browse Food Listings")

    # Load filter options from database
    cities = run_query("SELECT DISTINCT Location FROM food_listings")["Location"].tolist()
    providers = run_query("SELECT DISTINCT Name FROM providers")["Name"].tolist()
    food_types = run_query("SELECT DISTINCT Food_Type FROM food_listings")["Food_Type"].tolist()
    meal_types = run_query("SELECT DISTINCT Meal_Type FROM food_listings")["Meal_Type"].tolist()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        selected_city = st.selectbox("City", ["All"] + sorted(cities))
    with col2:
        selected_provider = st.selectbox("Provider", ["All"] + sorted(providers))
    with col3:
        selected_food_type = st.selectbox("Food Type", ["All"] + sorted(food_types))
    with col4:
        selected_meal_type = st.selectbox("Meal Type", ["All"] + sorted(meal_types))

    # Build dynamic query based on filters
    query = """
    SELECT f.Food_ID, f.Food_Name, f.Quantity, f.Expiry_Date,
           p.Name AS Provider_Name, p.Contact AS Provider_Contact,
           f.Location, f.Food_Type, f.Meal_Type
    FROM food_listings f
    JOIN providers p ON f.Provider_ID = p.Provider_ID
    WHERE 1=1
    """
    if selected_city != "All":
        query += f" AND f.Location = '{selected_city}'"
    if selected_provider != "All":
        query += f" AND p.Name = '{selected_provider}'"
    if selected_food_type != "All":
        query += f" AND f.Food_Type = '{selected_food_type}'"
    if selected_meal_type != "All":
        query += f" AND f.Meal_Type = '{selected_meal_type}'"

    results = run_query(query)
    st.write(f"**{len(results)} food listings found**")
    st.dataframe(results, use_container_width=True)


# PAGE 2: SQL Queries & Insights

elif page == "SQL Queries & Insights":
    st.header("SQL Queries & Insights")

    query_options = {
        "1. Providers & Receivers per city": """
            SELECT City, COUNT(*) AS Provider_Count FROM providers GROUP BY City ORDER BY Provider_Count DESC
        """,
        "2. Provider type contributing most food": """
            SELECT Provider_Type, SUM(Quantity) AS Total_Quantity FROM food_listings
            GROUP BY Provider_Type ORDER BY Total_Quantity DESC
        """,
        "3. Total food quantity available": """
            SELECT SUM(Quantity) AS Total_Food_Available FROM food_listings
        """,
        "4. City with highest food listings": """
            SELECT Location AS City, COUNT(*) AS Listing_Count FROM food_listings
            GROUP BY Location ORDER BY Listing_Count DESC
        """,
        "5. Most common food types": """
            SELECT Food_Type, COUNT(*) AS Count FROM food_listings GROUP BY Food_Type ORDER BY Count DESC
        """,
        "6. Claims per food item": """
            SELECT f.Food_Name, COUNT(c.Claim_ID) AS Times_Claimed FROM claims c
            JOIN food_listings f ON c.Food_ID = f.Food_ID GROUP BY f.Food_Name ORDER BY Times_Claimed DESC
        """,
        "7. Top receivers by claims": """
            SELECT r.Name, COUNT(c.Claim_ID) AS Total_Claims FROM claims c
            JOIN receivers r ON c.Receiver_ID = r.Receiver_ID GROUP BY r.Name ORDER BY Total_Claims DESC LIMIT 10
        """,
        "8. Provider with most successful claims": """
            SELECT p.Name, COUNT(c.Claim_ID) AS Completed_Claims FROM claims c
            JOIN food_listings f ON c.Food_ID = f.Food_ID
            JOIN providers p ON f.Provider_ID = p.Provider_ID
            WHERE c.Status = 'Completed' GROUP BY p.Name ORDER BY Completed_Claims DESC LIMIT 10
        """,
        "9. Claim status percentage": """
            SELECT Status, COUNT(*) AS Count,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) AS Percentage
            FROM claims GROUP BY Status
        """,
        "10. Avg quantity claimed per receiver": """
            SELECT r.Name, AVG(f.Quantity) AS Avg_Quantity_Claimed FROM claims c
            JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
            JOIN food_listings f ON c.Food_ID = f.Food_ID
            GROUP BY r.Name ORDER BY Avg_Quantity_Claimed DESC LIMIT 10
        """,
        "11. Most claimed meal type": """
            SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims FROM claims c
            JOIN food_listings f ON c.Food_ID = f.Food_ID GROUP BY f.Meal_Type ORDER BY Total_Claims DESC
        """,
        "12. Total donated by each provider": """
            SELECT p.Name, SUM(f.Quantity) AS Total_Donated FROM food_listings f
            JOIN providers p ON f.Provider_ID = p.Provider_ID GROUP BY p.Name ORDER BY Total_Donated DESC LIMIT 10
        """,
        "13. Food nearing expiry": """
            SELECT Food_Name, Quantity, Expiry_Date, Location FROM food_listings
            WHERE Expiry_Date <= (SELECT DATE(MAX(Expiry_Date), '-15 days') FROM food_listings)
            ORDER BY Expiry_Date ASC LIMIT 15
        """,
        "14. Cities with most claims": """
            SELECT f.Location AS City, COUNT(c.Claim_ID) AS Total_Claims FROM claims c
            JOIN food_listings f ON c.Food_ID = f.Food_ID GROUP BY f.Location ORDER BY Total_Claims DESC
        """,
        "15. Receiver counts per city": """
            SELECT City, COUNT(*) AS Receiver_Count FROM receivers GROUP BY City ORDER BY Receiver_Count DESC
        """,
    }

    selected = st.selectbox("Choose a query to run", list(query_options.keys()))
    result_df = run_query(query_options[selected])
    st.dataframe(result_df, use_container_width=True)


# PAGE 3: CRUD Operations

elif page == "Manage Listings (CRUD)":
    st.header("Manage Food Listings")

    tab1, tab2, tab3 = st.tabs(["➕ Add Listing", "✏️ Update Listing", "🗑️ Delete Listing"])

    # --- CREATE ---
    with tab1:
        st.subheader("Add a new food listing")
        providers_df = run_query("SELECT Provider_ID, Name, Type, City FROM providers")

        with st.form("add_form"):
            food_name = st.text_input("Food Name")
            quantity = st.number_input("Quantity", min_value=1, step=1)
            expiry_date = st.date_input("Expiry Date")
            provider_choice = st.selectbox(
                "Provider",
                providers_df.apply(lambda r: f"{r['Provider_ID']} - {r['Name']}", axis=1)
            )
            food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])
            submitted = st.form_submit_button("Add Listing")

            if submitted:
                provider_id = int(provider_choice.split(" - ")[0])
                provider_row = providers_df[providers_df["Provider_ID"] == provider_id].iloc[0]
                # Get next Food_ID
                max_id_result = run_query("SELECT MAX(Food_ID) AS max_id FROM food_listings")
                max_id_value = max_id_result["max_id"].iloc[0]
                if max_id_value is None or pd.isna(max_id_value):
                    new_id = 1
                else:
                    new_id = int(max_id_value) + 1
                run_action("""
                    INSERT INTO food_listings
                    (Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (new_id, food_name, quantity, str(expiry_date), provider_id,
                      provider_row["Type"], provider_row["City"], food_type, meal_type))
                st.success(f"Added '{food_name}' with Food_ID {new_id}")

    # --- UPDATE ---
    with tab2:
        st.subheader("Update an existing listing")
        listings_df = run_query("SELECT Food_ID, Food_Name, Quantity FROM food_listings")
        if len(listings_df) > 0:
            choice = st.selectbox(
                "Select listing to update",
                listings_df.apply(lambda r: f"{r['Food_ID']} - {r['Food_Name']} (Qty: {r['Quantity']})", axis=1)
            )
            food_id = int(choice.split(" - ")[0])

            new_quantity = st.number_input("New Quantity", min_value=0, step=1)
            if st.button("Update Quantity"):
                run_action("UPDATE food_listings SET Quantity = ? WHERE Food_ID = ?", (new_quantity, food_id))
                st.success(f"Updated Food_ID {food_id} to quantity {new_quantity}")

    # --- DELETE ---
    with tab3:
        st.subheader("Delete a listing")
        listings_df = run_query("SELECT Food_ID, Food_Name FROM food_listings")
        if len(listings_df) > 0:
            choice = st.selectbox(
                "Select listing to delete",
                listings_df.apply(lambda r: f"{r['Food_ID']} - {r['Food_Name']}", axis=1),
                key="delete_select"
            )
            food_id = int(choice.split(" - ")[0])
            if st.button("Delete Listing", type="primary"):
                run_action("DELETE FROM food_listings WHERE Food_ID = ?", (food_id,))
                st.success(f"Deleted Food_ID {food_id}")

# ===========================================================
# PAGE 4: Charts
# ===========================================================
elif page == "Charts":
    st.header("Visual Insights")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Food Quantity by Provider Type")
        df1 = run_query("SELECT Provider_Type, SUM(Quantity) AS Total FROM food_listings GROUP BY Provider_Type")
        fig1 = px.bar(df1, x="Provider_Type", y="Total", color="Provider_Type")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.subheader("Claim Status Breakdown")
        df2 = run_query("SELECT Status, COUNT(*) AS Count FROM claims GROUP BY Status")
        fig2 = px.pie(df2, names="Status", values="Count")
        st.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Food Listings by City")
        df3 = run_query("SELECT Location AS City, COUNT(*) AS Count FROM food_listings GROUP BY Location ORDER BY Count DESC")
        fig3 = px.bar(df3, x="City", y="Count", color="City")
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.subheader("Claims by Meal Type")
        df4 = run_query("""
            SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims FROM claims c
            JOIN food_listings f ON c.Food_ID = f.Food_ID GROUP BY f.Meal_Type
        """)
        fig4 = px.bar(df4, x="Meal_Type", y="Total_Claims", color="Meal_Type")
        st.plotly_chart(fig4, use_container_width=True)
