import streamlit as st
import pandas as pd
import pymysql
import plotly.express as px

# -------------------------------
# Database connection
# -------------------------------
def create_connection():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='ranjanaa',
            database='police_secure_check1',
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        return None


# -------------------------------
# Fetch data from database
# -------------------------------
def fetch_data(query):
    connection = create_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                df = pd.DataFrame(result)
                return df
        finally:
            connection.close()
    else:
        return pd.DataFrame()


# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="🖥️📊SecureCheck Police Dashboard", layout="wide")

st.title("🚨👮‍♂️SecureCheck: Police Check Post Digital Ledger")
st.markdown("Real-time monitoring and insights for law enforcement 🚓")

# Show full table
# -------------------------------
st.header("📄 Police Logs Overview")

query = "SELECT * FROM secure_check"
data = fetch_data(query)

st.dataframe(data, use_container_width=True)


# -------------------------------
# Quick Metrics
# -------------------------------
st.header("📊 Key Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_stops = data.shape[0]
    st.metric("Total Police Stops", total_stops)

with col2:
    arrests = data[data['stop_outcome'].str.contains("arrest", case=False, na=False)].shape[0]
    st.metric("Total Arrests", arrests)

with col3:
    warnings = data[data['stop_outcome'].str.contains("warning", case=False, na=False)].shape[0]
    st.metric("Total Warnings", warnings)
with col4:
    drug_related = data[data['drugs_related_stop'] == 1].shape[0]
    st.metric("Drug Related Stops", drug_related)

# -------------------------------
# Advanced Queries
# -------------------------------
st.header("✨ Insights")

selected_query_1 = st.selectbox(
    "Select a Query to Run",
    [
        "Top 10 vehicle_Number involved in drug-related stops",
        "Most frequently searched vehicle",
        "Which driver age group had the highest arrest rate?",
        "What is the gender distribution of drivers stopped in each country?",
        "Which race and gender combination has the highest search rate?",
        "What time of day sees the most traffic stops?",
        "What is the average stop duration for different violations?",
        "Are stops during the night more likely to lead to arrests?",
        "Which violations are most associated with searches or arrests?",
        "Which violations are most common among younger drivers (<25)?",
        "Is there a violation that rarely results in search or arrest?",
        "Which countries report the highest rate of drug-related stops?",
        "What is the arrest rate by country and violation?",
        "Which country has the most stops with search conducted?"
    ]
)




query_map_1= {
    "Top 10 vehicle_Number involved in drug-related stops":
        "SELECT vehicle_number, COUNT(*) AS total_stops FROM secure_check WHERE drugs_related_stop = 1 GROUP BY vehicle_number ORDER BY total_stops DESC LIMIT 10",

    "Most frequently searched vehicle":
        "SELECT vehicle_number, COUNT(*) AS total_searches FROM secure_check WHERE search_conducted = 1 GROUP BY vehicle_number ORDER BY total_searches DESC LIMIT 1",

    "Which driver age group had the highest arrest rate?":
        """SELECT 
  CASE 
    WHEN driver_age < 18 THEN 'Under 18'
    WHEN driver_age BETWEEN 18 AND 25 THEN '18-25'
    WHEN driver_age BETWEEN 26 AND 40 THEN '26-40'
    WHEN driver_age BETWEEN 41 AND 60 THEN '41-60'
    ELSE '60+'
  END AS driver_age_group,
  COUNT(*) AS arrest_count
FROM secure_check
WHERE is_arrested = TRUE
GROUP BY driver_age_group
ORDER BY arrest_count DESC
LIMIT 1""",
    "What is the gender distribution of drivers stopped in each country?":
        "SELECT driver_gender, COUNT(*) AS count FROM secure_check GROUP BY driver_gender",

    "Which race and gender combination has the highest search rate?":
        "SELECT driver_race, driver_gender, COUNT(*) AS search_count FROM secure_check WHERE search_conducted = 1 GROUP BY driver_race, driver_gender ORDER BY search_count DESC LIMIT 5",

    "What time of day sees the most traffic stops?":
        "SELECT HOUR(stop_time) AS hour_of_day, COUNT(*) AS stop_count FROM secure_check GROUP BY hour_of_day ORDER BY stop_count DESC LIMIT 1",
    "What is the average stop duration for different violations?":
        "SELECT violation, AVG(stop_duration) AS avg_stop_duration FROM secure_check GROUP BY violation ORDER BY avg_stop_duration DESC",
     "Are stops during the night more likely to lead to arrests?":
        "SELECT CASE WHEN HOUR(stop_time) >= 20 OR HOUR(stop_time) < 6 THEN 'Night' ELSE 'Day' END AS time_of_day, AVG(is_arrested) AS arrest_rate FROM secure_check GROUP BY time_of_day",
    "Which violations are most associated with searches or arrests?":
        "SELECT violation, AVG(search_conducted) AS search_rate, AVG(is_arrested) AS arrest_rate FROM secure_check GROUP BY violation ORDER BY search_rate DESC, arrest_rate DESC",
    "Which violations are most common among younger drivers (<25)?":
        "SELECT violation, COUNT(*) AS count FROM secure_check WHERE driver_age < 25 GROUP BY violation ORDER BY count DESC LIMIT 5",
    "Is there a violation that rarely results in search or arrest?":
        "SELECT violation, AVG(search_conducted) AS search_rate, AVG(is_arrested) AS arrest_rate FROM secure_check GROUP BY violation ORDER BY search_rate ASC, arrest_rate ASC",
    "Which countries report the highest rate of drug-related stops?":
        "SELECT country_name, AVG(drugs_related_stop) AS drug_related_rate FROM secure_check GROUP BY country_name ORDER BY drug_related_rate DESC LIMIT 5",
    "What is the arrest rate by country and violation?":
        "SELECT country_name, violation, AVG(is_arrested) AS arrest_rate FROM secure_check GROUP BY country_name, violation",
    "Which country has the most stops with search conducted?":
        "SELECT country_name, COUNT(*) AS search_count FROM secure_check WHERE search_conducted = 1 GROUP BY country_name ORDER BY search_count DESC LIMIT 1"
}

if st.button("Run Query", key="btn1"):
    result = fetch_data(query_map_1[selected_query_1])

    if not result.empty:
        st.dataframe(result, use_container_width=True)
    else:
        st.warning("No results found for the selected query.")

st.header("✨ Advanced Insights")

selected_query_2 = st.selectbox(
    "Select a Query to Run",
    [
        "Yearly Breakdown of Stops and Arrests by Country",
        "Driver Violation Trends Based on Age and Race ",
        "Time Period Analysis of Stops (Joining with Date Functions) , Number of Stops by Year,Month, Hour of the Day",
        "Violations with High Search and Arrest Rates ",
        "Driver Demographics by Country (Age, Gender, and Race)",
        "Top 5 Violations with Highest Arrest Rates"
    ]
)



query_map_2 = {
    "Yearly Breakdown of Stops and Arrests by Country":
      """ SELECT 
    country_name,
    stop_year,
    stop_count,
    arrest_count,
    RANK() OVER (PARTITION BY stop_year ORDER BY stop_count DESC) AS rank_in_year
FROM (
    SELECT 
        country_name,
        YEAR(STR_TO_DATE(CONCAT(stop_date, ' ', stop_time), '%Y-%m-%d %H:%i')) AS stop_year,
        COUNT(*) AS stop_count,
        SUM(is_arrested) AS arrest_count
    FROM secure_check
    GROUP BY country_name, stop_year
) AS sub
WHERE stop_year IS NOT NULL
  AND stop_year <= YEAR(CURDATE())""",

    "Driver Violation Trends Based on Age and Race ":"""SELECT 
    driver_age,
    driver_race,
    violation,
    COUNT(*) AS total_violations
FROM secure_check
WHERE driver_age IS NOT NULL
  AND driver_race IS NOT NULL
  AND violation IS NOT NULL
  AND STR_TO_DATE(stop_date, '%Y-%m-%d') <= CURDATE()  -- exclude future dates
  AND STR_TO_DATE(stop_date, '%Y-%m-%d') IS NOT NULL   -- exclude bad date strings
GROUP BY driver_age, driver_race, violation
ORDER BY total_violations DESC""",

    "Time Period Analysis of Stops (Joining with Date Functions) , Number of Stops by Year,Month, Hour of the Day":"""SELECT 
    YEAR(STR_TO_DATE(stop_date, '%Y-%m-%d'))  AS stop_year,
    MONTH(STR_TO_DATE(stop_date, '%Y-%m-%d')) AS stop_month,
    HOUR(STR_TO_DATE(stop_time, '%H:%i'))     AS stop_hour,
    COUNT(*) AS total_stops
FROM secure_check
WHERE STR_TO_DATE(stop_date, '%Y-%m-%d') IS NOT NULL
  AND STR_TO_DATE(stop_date, '%Y-%m-%d') <= CURDATE()
GROUP BY stop_year, stop_month, stop_hour
ORDER BY stop_year, stop_month, stop_hour""",
    "Violations with High Search and Arrest Rates": 
    """SELECT 
        violation, 
        AVG(search_conducted) AS search_rate,
        AVG(is_arrested) AS arrest_rate
    FROM secure_check
    GROUP BY violation
    ORDER BY search_rate DESC, arrest_rate DESC""",
    "Driver Demographics by Country (Age, Gender, and Race)":
       "SELECT country_name, driver_age, driver_gender, driver_race, COUNT(*) AS total_stops FROM secure_check GROUP BY country_name, driver_age, driver_gender, driver_race",
    "Top 5 Violations with Highest Arrest Rates":
       "SELECT violation, AVG(is_arrested) AS arrest_rate FROM secure_check GROUP BY violation ORDER BY arrest_rate DESC LIMIT 5"

}

selected_query_2 = selected_query_2.strip()

if st.button("Run Query", key="btn2"):
    result = fetch_data(query_map_2[selected_query_2])

    if not result.empty:
        st.dataframe(result, use_container_width=True)
    else:
        st.warning("No results found for the selected query.")

st.markdown("---")
st.markdown("✨ Built with ❤️ for Law Enforcement by **SecureCheck** 🚓")

st.header("📋 Add New Police Log & Predict Outcome and Violation")

with st.form("new_log_form"):

    stop_date = st.date_input("Stop Date")
    stop_time = st.time_input("Stop Time")
    country_name = st.text_input("Country Name")

    driver_gender = st.selectbox("Driver Gender", ["M", "F"])
    driver_age = st.number_input("Driver Age", min_value=16, max_value=100, value=27)
    driver_race = st.text_input("Driver Race")

    search_conducted = st.selectbox("Was a Search Conducted?", [0, 1])
    search_type = st.text_input("Search Type")

    drugs_related_stop = st.selectbox("Was it Drug Related?", [0, 1])
    stop_duration = st.selectbox(
        "Stop Duration",
        data["stop_duration"].dropna().unique()
    )

    vehicle_number = st.text_input("Vehicle Number")

    timestamp = pd.Timestamp.now()

    submitted = st.form_submit_button("Predict Stop Outcome & Violation")

    if submitted:
        # -------------------------------
        # Filter data based on input
        # -------------------------------
        filtered_data = data[
           (data["driver_gender"] == driver_gender) &
           (data["search_conducted"] == search_conducted) &
           (data["drugs_related_stop"] == drugs_related_stop) &
           (data["driver_age"].between(driver_age - 5, driver_age + 5))
        ]
        
        if not filtered_data.empty:
            predicted_outcome = filtered_data["stop_outcome"].mode()[0]
            predicted_violation = filtered_data["violation"].mode()[0]

            st.success(f"Predicted Outcome: {predicted_outcome}")
            st.success(f"Predicted Violation: {predicted_violation}")

            search_text = "a search was conducted" if int(search_conducted) else "no search was conducted"
            drug_text = "was drug-related" if int(drugs_related_stop) else "was not drug-related"

            st.markdown(f"""
            ### 📊 Prediction Summary
            - **Predicted Violation:** {predicted_violation}  
            - **Predicted Outcome:** {predicted_outcome}

            📝 A {driver_age}-year-old {driver_gender} driver in {country_name} was stopped at 
            {stop_time.strftime('%I:%M %p')} on {stop_date}.  
            During the stop, {search_text}, and the stop {drug_text}.

            ⏱ **Stop Duration:** {stop_duration}  
            🚗 **Vehicle Number:** {vehicle_number}
            """)

        else:
            st.warning("No matching data found for prediction.")


st.markdown("---")

st.markdown("""
<div style="
    background: linear-gradient(135deg, #1f4037, #99f2c8);
    padding: 30px;
    border-radius: 18px;
    color: white;
    text-align: center;
    box-shadow: 0 8px 20px rgba(0,0,0,0.25);
    margin-top: 20px;
">

<h2 style="margin-bottom:10px;">👩‍💻 Creator of this Project</h2>

<p style="font-size:20px; margin:5px 0;"><b>Keerthana Gc</b></p>

<p style="font-size:15px; line-height:1.6;">
📊 Data Science Enthusiast <br>
💡 Skilled in Python, SQL, Data Analysis <br>
🚀 Technologies: Streamlit, Pandas
</p>

<hr style="border:1px solid rgba(255,255,255,0.4); width:60%; margin:15px auto;">

<p style="font-size:14px;">
🔐 Building data-driven solutions for smarter decision-making
</p>

</div>
""", unsafe_allow_html=True)