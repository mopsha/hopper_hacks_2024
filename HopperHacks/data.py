import mysql.connector
from mysql.connector import Error
import pandas as pd

def create_server_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

pw = "Misha100!"

connection = create_server_connection("localhost", "root", pw)

def create_database(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        print("Database created successfully")
    except Error as err:
        print(f"Error: '{err}'")


def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as err:
        print(f"Error: '{err}'")

def execute_query_params(connection, query, params):
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"Error: '{e}'")
    finally:
        cursor.close()
    

create_database_query = "CREATE DATABASE IF NOT EXISTS todo_calendar_db"
create_database(connection, create_database_query)
create_database_query = "CREATE DATABASE IF NOT EXISTS tasks_db"
create_database(connection, create_database_query)


def create_tasks_table(connection):
    create_tasks_table_query = """
    CREATE TABLE IF NOT EXISTS tasks (
        task_id INT AUTO_INCREMENT PRIMARY KEY,
        description VARCHAR(255),
        completed BOOLEAN,
        date_created DATE
    );
    """

    execute_query(connection, create_tasks_table_query)
    print("Tasks table created successfully")

alter_table_query = """
ALTER TABLE daily_completion
ADD COLUMN completion_percentage FLOAT;
"""

execute_query(connection, alter_table_query)

def create_daily_completion_table(connection):

    create_daily_completion_query = """
    CREATE TABLE IF NOT EXISTS daily_completion (
        completion_id INT AUTO_INCREMENT PRIMARY KEY,
        date DATE,
        tasks_completed INT,
        total_tasks INT,
        completion_percantage INT
    );
    """
    execute_query(connection, create_daily_completion_query)
    print("Daily completion table created successfully")

def update_task(connection, completed, description):
    update_statement = """
    UPDATE tasks
    SET completed = %s
    WHERE description = %s;
    """
    
    parameters = (completed, description)
    
    execute_query_params(connection, update_statement, parameters)
    print("Tasks table altered successfully")

def clear_database(connection):
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        for table in tables:
            table_name_key = next(iter(table))  
            table_name = table[table_name_key]
            delete_statement = f"DELETE FROM `{table_name}`;" 
            cursor.execute(delete_statement)
        print("All data has been removed from the database.")
        
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        
        connection.commit()
    except Error as e:
        print(f"Error: '{e}'")
        connection.rollback() 
    finally:
        cursor.close()
    
def alter_daily_completion_table_add_fk(connection):
    alter_table_query = """
    ALTER TABLE daily_completion
    ADD FOREIGN KEY (user_id) REFERENCES users(user_id);
    """
    execute_query(connection, alter_table_query)
    print("Daily completion table altered successfully with a foreign key")


db_name = "todo_calendar_db"
connection = create_db_connection("localhost", "root", pw, db_name)
create_daily_completion_table(connection)

db_name = "tasks_db"
connection = create_db_connection("localhost", "root", pw, db_name)
create_tasks_table(connection)

def add_task(connection, description, completed):
    add_task_query = """
    INSERT INTO tasks (description, completed, date_created)
    VALUES (%s, %s, CURDATE());
    """
    values = (description, completed)  
    cursor = connection.cursor()
    try:
        cursor.execute(add_task_query, values) 
        connection.commit()  
        print("Task added successfully")
    except Error as err:
        print(f"Error: '{err}'")
    finally:
        cursor.close()  

def remove_entry_by_name(connection, description):
    """
    Removes an entry from the 'tasks_db' table based on the given item name.

    :param connection: The MySQL connection object.
    :param description: The name of the item to be removed.
    """
    try:
        cursor = connection.cursor()
    
        delete_statement = "DELETE FROM tasks WHERE description = %s;"
        cursor.execute(delete_statement, (description,))
        connection.commit()
        print(f"Entry with name '{description}' was removed successfully.")

    except mysql.connector.Error as error:
        print(f"Failed to remove entry: {error}")
        connection.rollback() 
    
    finally:
        if cursor:
            cursor.close()

add_task(connection, "Die", True)