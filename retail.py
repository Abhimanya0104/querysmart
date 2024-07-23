import sqlite3

# Connect to SQLite
connection = sqlite3.connect("retail.db")

# Create a cursor object to insert record and create tables
cursor = connection.cursor()

# Drop tables if they already exist
cursor.execute("DROP TABLE IF EXISTS SALES")
cursor.execute("DROP TABLE IF EXISTS INVENTORY")
cursor.execute("DROP TABLE IF EXISTS CUSTOMERS")
cursor.execute("DROP TABLE IF EXISTS SUPPLIERS")
cursor.execute("DROP TABLE IF EXISTS PURCHASES")

# Create the SALES table
table_sales = """
CREATE TABLE SALES (
    TRANSACTION_ID INTEGER PRIMARY KEY,
    DATE TEXT,
    PRODUCT_ID INTEGER,
    CUSTOMER_ID INTEGER,
    QUANTITY INTEGER,
    AMOUNT REAL,
    FOREIGN KEY (PRODUCT_ID) REFERENCES INVENTORY(PRODUCT_ID),
    FOREIGN KEY (CUSTOMER_ID) REFERENCES CUSTOMERS(CUSTOMER_ID)
);
"""
cursor.execute(table_sales)

# Create the INVENTORY table
table_inventory = """
CREATE TABLE INVENTORY (
    PRODUCT_ID INTEGER PRIMARY KEY,
    PRODUCT_NAME TEXT,
    CATEGORY TEXT,
    STOCK_LEVEL INTEGER,
    PRICE REAL
);
"""
cursor.execute(table_inventory)

# Create the CUSTOMERS table
table_customers = """
CREATE TABLE CUSTOMERS (
    CUSTOMER_ID INTEGER PRIMARY KEY,
    NAME TEXT,
    EMAIL TEXT,
    PHONE TEXT,
    PREFERRED_CATEGORY TEXT
);
"""
cursor.execute(table_customers)

# Create the SUPPLIERS table
table_suppliers = """
CREATE TABLE SUPPLIERS (
    SUPPLIER_ID INTEGER PRIMARY KEY,
    SUPPLIER_NAME TEXT,
    CONTACT_NAME TEXT,
    CONTACT_EMAIL TEXT,
    CONTACT_PHONE TEXT
);
"""
cursor.execute(table_suppliers)

# Create the PURCHASES table
table_purchases = """
CREATE TABLE PURCHASES (
    PURCHASE_ID INTEGER PRIMARY KEY,
    SUPPLIER_ID INTEGER,
    PRODUCT_ID INTEGER,
    QUANTITY INTEGER,
    DATE TEXT,
    FOREIGN KEY (SUPPLIER_ID) REFERENCES SUPPLIERS(SUPPLIER_ID),
    FOREIGN KEY (PRODUCT_ID) REFERENCES INVENTORY(PRODUCT_ID)
);
"""
cursor.execute(table_purchases)

# Insert sample data into SALES table
cursor.execute("INSERT INTO SALES (DATE, PRODUCT_ID, CUSTOMER_ID, QUANTITY, AMOUNT) VALUES('2024-01-01', 1, 1, 2, 1500.00)")
cursor.execute("INSERT INTO SALES (DATE, PRODUCT_ID, CUSTOMER_ID, QUANTITY, AMOUNT) VALUES('2024-01-03', 2, 2, 5, 250.00)")
cursor.execute("INSERT INTO SALES (DATE, PRODUCT_ID, CUSTOMER_ID, QUANTITY, AMOUNT) VALUES('2024-01-05', 3, 1, 3, 2000.00)")
cursor.execute("INSERT INTO SALES (DATE, PRODUCT_ID, CUSTOMER_ID, QUANTITY, AMOUNT) VALUES('2024-01-10', 4, 2, 10, 150.00)")
cursor.execute("INSERT INTO SALES (DATE, PRODUCT_ID, CUSTOMER_ID, QUANTITY, AMOUNT) VALUES('2024-01-15', 5, 3, 4, 400.00)")

# Insert sample data into INVENTORY table
cursor.execute("INSERT INTO INVENTORY (PRODUCT_NAME, CATEGORY, STOCK_LEVEL, PRICE) VALUES('Laptop', 'Electronics', 20, 750.00)")
cursor.execute("INSERT INTO INVENTORY (PRODUCT_NAME, CATEGORY, STOCK_LEVEL, PRICE) VALUES('Shoes', 'Apparel', 50, 50.00)")
cursor.execute("INSERT INTO INVENTORY (PRODUCT_NAME, CATEGORY, STOCK_LEVEL, PRICE) VALUES('Phone', 'Electronics', 30, 667.00)")
cursor.execute("INSERT INTO INVENTORY (PRODUCT_NAME, CATEGORY, STOCK_LEVEL, PRICE) VALUES('T-shirt', 'Apparel', 100, 15.00)")
cursor.execute("INSERT INTO INVENTORY (PRODUCT_NAME, CATEGORY, STOCK_LEVEL, PRICE) VALUES('Headphones', 'Electronics', 40, 100.00)")

# Insert sample data into CUSTOMERS table
cursor.execute("INSERT INTO CUSTOMERS (NAME, EMAIL, PHONE, PREFERRED_CATEGORY) VALUES('John Doe', 'john.doe@example.com', '123-456-7890', 'Electronics')")
cursor.execute("INSERT INTO CUSTOMERS (NAME, EMAIL, PHONE, PREFERRED_CATEGORY) VALUES('Jane Smith', 'jane.smith@example.com', '123-456-7891', 'Apparel')")
cursor.execute("INSERT INTO CUSTOMERS (NAME, EMAIL, PHONE, PREFERRED_CATEGORY) VALUES('Mike Johnson', 'mike.johnson@example.com', '123-456-7892', 'Electronics')")

# Insert sample data into SUPPLIERS table
cursor.execute("INSERT INTO SUPPLIERS (SUPPLIER_NAME, CONTACT_NAME, CONTACT_EMAIL, CONTACT_PHONE) VALUES('Supplier A', 'Alice', 'alice@supplier.com', '123-456-7893')")
cursor.execute("INSERT INTO SUPPLIERS (SUPPLIER_NAME, CONTACT_NAME, CONTACT_EMAIL, CONTACT_PHONE) VALUES('Supplier B', 'Bob', 'bob@supplier.com', '123-456-7894')")

# Insert sample data into PURCHASES table
cursor.execute("INSERT INTO PURCHASES (SUPPLIER_ID, PRODUCT_ID, QUANTITY, DATE) VALUES(1, 1, 10, '2024-01-01')")
cursor.execute("INSERT INTO PURCHASES (SUPPLIER_ID, PRODUCT_ID, QUANTITY, DATE) VALUES(2, 2, 20, '2024-01-02')")
cursor.execute("INSERT INTO PURCHASES (SUPPLIER_ID, PRODUCT_ID, QUANTITY, DATE) VALUES(1, 3, 15, '2024-01-03')")
cursor.execute("INSERT INTO PURCHASES (SUPPLIER_ID, PRODUCT_ID, QUANTITY, DATE) VALUES(2, 4, 25, '2024-01-04')")
cursor.execute("INSERT INTO PURCHASES (SUPPLIER_ID, PRODUCT_ID, QUANTITY, DATE) VALUES(1, 5, 30, '2024-01-05')")

# Display all the records inserted
print("Sample data inserted successfully.")

# Commit changes and close connection
connection.commit()
connection.close()
