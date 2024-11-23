import sqlite3

# Path to your SQLite database
database_path = "user.db"

# Table name to delete records from
table_name = "user_9608144523"

try:
    # Connect to the SQLite database
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # SQL query to delete all rows from the table
    delete_query = f"DELETE FROM {table_name};"

    # Execute the delete query
    cursor.execute(delete_query)

    # Commit the changes
    conn.commit()

    # Get the count of deleted rows
    rows_deleted = cursor.rowcount
    print(f"Successfully deleted {rows_deleted} rows from the table '{table_name}'.")

except sqlite3.Error as e:
    print(f"An error occurred: {e}")

finally:
    # Close the connection
    if conn:
        conn.close()
