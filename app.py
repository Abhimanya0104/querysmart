from dotenv import load_dotenv
import os
import sqlite3
import streamlit as st
import google.generativeai as genai
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Configure Genai Key
genai_key = os.getenv("GOOGLE_API_KEY")
if not genai_key:
    st.error("Google API key not found in environment variables.")
    st.stop()
genai.configure(api_key=genai_key)

# Function to load Google Gemini Model and provide queries as response
def get_gemini_response(question, prompt):
    if not question.strip():
        st.warning("The question cannot be empty. Please enter a valid question.")
        return None

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content([prompt[0], question])
        query = response.text.strip()
        
        # Clean up the query to ensure no extraneous characters
        query = query.replace('```', '').strip()
        
        # Basic validation for the generated SQL query
        if not query or not query.lower().startswith("select"):
            st.error("Generated SQL query is invalid or empty.")
            return None
        logging.info(f"Generated SQL Query: {query}")
        return query
    except Exception as e:
        logging.error(f"Error generating SQL query: {str(e)}")
        st.error("An error occurred while generating the SQL query. Please try again later.")
        return None

# Function to retrieve query from the database
def read_sql_query(sql, db):
    if not sql:
        st.warning("SQL query is empty. Cannot execute.")
        return None
    
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        conn.commit()
        conn.close()
        return rows
    except sqlite3.Error as e:
        logging.error(f"SQLite error: {str(e)}")
        st.error("An SQLite error occurred while executing the query. Please check the query and try again.")
        return None
    except Exception as e:
        logging.error(f"Error executing SQL query: {str(e)}")
        st.error("An error occurred while executing the SQL query. Please try again later.")
        return None

# Define your prompt
prompt = [
    """
    You are an expert in converting English questions to SQL queries! The SQL database is named RETAIL and has the following tables:

    1. SALES:
        - TRANSACTION_ID (integer, primary key): Unique identifier for each transaction.
        - DATE (text): Date of the transaction in YYYY-MM-DD format.
        - PRODUCT_ID (integer, foreign key referencing INVENTORY.PRODUCT_ID): Identifier for the product sold.
        - CUSTOMER_ID (integer, foreign key referencing CUSTOMERS.CUSTOMER_ID): Identifier for the customer who made the purchase.
        - QUANTITY (integer): Number of units sold in the transaction.
        - AMOUNT (real): Total amount of money received for the transaction.

    2. INVENTORY:
        - PRODUCT_ID (integer, primary key): Unique identifier for each product.
        - PRODUCT_NAME (text): Name of the product.
        - CATEGORY (text): Category to which the product belongs (e.g., Electronics, Apparel).
        - STOCK_LEVEL (integer): Number of units currently in stock.
        - PRICE (real): Price per unit of the product.

    3. CUSTOMERS:
        - CUSTOMER_ID (integer, primary key): Unique identifier for each customer.
        - NAME (text): Full name of the customer.
        - EMAIL (text): Email address of the customer.
        - PHONE (text): Phone number of the customer.
        - PREFERRED_CATEGORY (text): Customer's preferred product category (e.g., Electronics, Apparel).

    4. SUPPLIERS:
        - SUPPLIER_ID (integer, primary key): Unique identifier for each supplier.
        - SUPPLIER_NAME (text): Name of the supplier.
        - CONTACT_NAME (text): Name of the contact person at the supplier.
        - CONTACT_EMAIL (text): Email address of the contact person.
        - CONTACT_PHONE (text): Phone number of the contact person.

    5. PURCHASES:
        - PURCHASE_ID (integer, primary key): Unique identifier for each purchase.
        - SUPPLIER_ID (integer, foreign key referencing SUPPLIERS.SUPPLIER_ID): Identifier for the supplier.
        - PRODUCT_ID (integer, foreign key referencing INVENTORY.PRODUCT_ID): Identifier for the product purchased.
        - QUANTITY (integer): Number of units purchased.
        - DATE (text): Date of the purchase in YYYY-MM-DD format.

    Convert the following English questions to SQL queries based on the provided schema:

    Example 1 - How much revenue was generated in January 2024?
    SQL: SELECT SUM(AMOUNT) FROM SALES WHERE DATE LIKE '2024-01%';

    Example 2 - List all products in the Electronics category with stock levels below 50.
    SQL: SELECT * FROM INVENTORY WHERE CATEGORY='Electronics' AND STOCK_LEVEL < 50;

    Example 3 - Retrieve email addresses of customers who prefer Apparel.
    SQL: SELECT EMAIL FROM CUSTOMERS WHERE PREFERRED_CATEGORY='Apparel';

    Example 4 - Find the total number of products purchased from a specific supplier in June 2024.
    SQL: SELECT SUM(QUANTITY) FROM PURCHASES WHERE SUPPLIER_ID = [SUPPLIER_ID] AND DATE LIKE '2024-06%';

    Example 5 - List all suppliers along with their contact names and emails.
    SQL: SELECT SUPPLIER_NAME, CONTACT_NAME, CONTACT_EMAIL FROM SUPPLIERS;

    Example 6 - Retrieve the names and prices of products that have sold more than 100 units.
    SQL: SELECT PRODUCT_NAME, PRICE FROM INVENTORY WHERE PRODUCT_ID IN (SELECT PRODUCT_ID FROM SALES GROUP BY PRODUCT_ID HAVING SUM(QUANTITY) > 100);

    Example 7 - Get the names and contact details of customers who made purchases in the last month.
    SQL: SELECT NAME, EMAIL, PHONE FROM CUSTOMERS WHERE CUSTOMER_ID IN (SELECT DISTINCT CUSTOMER_ID FROM SALES WHERE DATE >= date('now','start of month','-1 month'));

    Example 8 - Find the average stock level for each product category.
    SQL: SELECT CATEGORY, AVG(STOCK_LEVEL) FROM INVENTORY GROUP BY CATEGORY;

    Example 9 - List all products purchased from suppliers along with their quantities and dates of purchase.
    SQL: SELECT INVENTORY.PRODUCT_NAME, PURCHASES.QUANTITY, PURCHASES.DATE FROM PURCHASES JOIN INVENTORY ON PURCHASES.PRODUCT_ID = INVENTORY.PRODUCT_ID;

    Example 10 - Retrieve the total sales amount for each customer.
    SQL: SELECT CUSTOMERS.NAME, SUM(SALES.AMOUNT) AS TOTAL_SALES FROM SALES JOIN CUSTOMERS ON SALES.CUSTOMER_ID = CUSTOMERS.CUSTOMER_ID GROUP BY CUSTOMERS.NAME;

    Example 11 - List the top 5 best-selling products by revenue.
    SQL: SELECT INVENTORY.PRODUCT_NAME, SUM(SALES.AMOUNT) AS TOTAL_REVENUE FROM SALES JOIN INVENTORY ON SALES.PRODUCT_ID = INVENTORY.PRODUCT_ID GROUP BY INVENTORY.PRODUCT_NAME ORDER BY TOTAL_REVENUE DESC LIMIT 5;

    Example 12 - Find the total number of distinct products sold in the last year.
    SQL: SELECT COUNT(DISTINCT PRODUCT_ID) FROM SALES WHERE DATE >= date('now','-1 year');

    Example 13 - Retrieve the details of all electronics products that have been sold but have stock levels below 10.
    SQL: SELECT INVENTORY.PRODUCT_NAME, INVENTORY.STOCK_LEVEL, SALES.QUANTITY, SALES.DATE FROM SALES JOIN INVENTORY ON SALES.PRODUCT_ID = INVENTORY.PRODUCT_ID WHERE INVENTORY.CATEGORY = 'Electronics' AND INVENTORY.STOCK_LEVEL < 10;

    Example 14 - Get the total quantity and total amount of sales per product category.
    SQL: SELECT INVENTORY.CATEGORY, SUM(SALES.QUANTITY) AS TOTAL_QUANTITY, SUM(SALES.AMOUNT) AS TOTAL_AMOUNT FROM SALES JOIN INVENTORY ON SALES.PRODUCT_ID = INVENTORY.PRODUCT_ID GROUP BY INVENTORY.CATEGORY;

    Example 15 - List the names and preferred categories of customers who have purchased more than $1000 worth of products.
    SQL: SELECT CUSTOMERS.NAME, CUSTOMERS.PREFERRED_CATEGORY FROM CUSTOMERS JOIN SALES ON CUSTOMERS.CUSTOMER_ID = SALES.CUSTOMER_ID GROUP BY CUSTOMERS.CUSTOMER_ID HAVING SUM(SALES.AMOUNT) > 1000;

    Example 16 - Retrieve the monthly revenue generated for each product.
    SQL: SELECT INVENTORY.PRODUCT_NAME, strftime('%Y-%m', SALES.DATE) AS MONTH, SUM(SALES.AMOUNT) AS MONTHLY_REVENUE FROM SALES JOIN INVENTORY ON SALES.PRODUCT_ID = INVENTORY.PRODUCT_ID GROUP BY INVENTORY.PRODUCT_NAME, MONTH;

    Example 17 - Find the suppliers who supplied products that were sold more than 500 units in total.
    SQL: SELECT SUPPLIERS.SUPPLIER_NAME FROM SUPPLIERS JOIN PURCHASES ON SUPPLIERS.SUPPLIER_ID = PURCHASES.SUPPLIER_ID WHERE PURCHASES.PRODUCT_ID IN (SELECT PRODUCT_ID FROM SALES GROUP BY PRODUCT_ID HAVING SUM(QUANTITY) > 500);

    Example 18 - List the products with their current stock levels and the total quantity sold.
    SQL: SELECT INVENTORY.PRODUCT_NAME, INVENTORY.STOCK_LEVEL, (SELECT SUM(SALES.QUANTITY) FROM SALES WHERE SALES.PRODUCT_ID = INVENTORY.PRODUCT_ID) AS TOTAL_SOLD FROM INVENTORY;

    Example 19 - Retrieve the customer details and the total amount they spent in the last 6 months.
    SQL: SELECT CUSTOMERS.NAME, CUSTOMERS.EMAIL, CUSTOMERS.PHONE, SUM(SALES.AMOUNT) AS TOTAL_SPENT FROM CUSTOMERS JOIN SALES ON CUSTOMERS.CUSTOMER_ID = SALES.CUSTOMER_ID WHERE SALES.DATE >= date('now','-6 months') GROUP BY CUSTOMERS.CUSTOMER_ID;

    Example 20 - Find the average purchase quantity per supplier.
    SQL: SELECT SUPPLIERS.SUPPLIER_NAME, AVG(PURCHASES.QUANTITY) AS AVERAGE_QUANTITY FROM SUPPLIERS JOIN PURCHASES ON SUPPLIERS.SUPPLIER_ID = PURCHASES.SUPPLIER_ID GROUP BY SUPPLIERS.SUPPLIER_ID;

    Ensure the SQL code does not contain ``` at the beginning or end, and does not include the word 'sql' in the output. The generated SQL should be tailored to the question asked.
    """
]

# Streamlit App
st.set_page_config(page_title="QuerySmart: AI-Powered Retail Data Query Interface")
st.header("QuerySmart: AI-Powered Retail Data Query Interface")

# Initialize chat history in session state if not already present
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

question = st.text_input("Input: ", key="input")
submit = st.button("Ask the question")

# If submit is clicked
if submit:
    if question:
        response = get_gemini_response(question, prompt)
        if response:
            logging.info(f"SQL Query: {response}")  # Log the SQL query for debugging
            query_results = read_sql_query(response, "retail.db")
            if query_results:
                # Update chat history
                st.session_state.chat_history.append({"question": question, "response": query_results})
            else:
                st.warning("No results found or there was an error executing the query. Please check the query or database.")
        else:
            st.warning("Failed to generate SQL query.")
    else:
        st.warning("Please enter a question!")

# Display chat history
st.subheader("Chat History")
for i, chat in enumerate(st.session_state.chat_history):
    st.write(f"Q{i+1}: {chat['question']}")
    st.write(f"A{i+1}: {chat['response']}")

# Display the latest response
if submit and question:
    st.subheader("The Response is")
    if query_results:
        for row in query_results:
            st.write(row)
