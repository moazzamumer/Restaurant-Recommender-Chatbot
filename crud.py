import sqlite3
from datetime import datetime
import re

db_path = 'chat.db'  

import sqlite3

# def chatbot_prompt(prompt, context):


def insert_chat_message(user_id, role, text):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get the current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Insert the data into the chat_messages table
    cursor.execute('''
        INSERT INTO chat_messages (user_id, role, text, timestamp) 
        VALUES (?, ?, ?, ?)
    ''', (user_id, role, text, timestamp))
    
    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

def get_user_messages(user_id):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Execute the query to get all entries for the given user_id, ordered by timestamp
    cursor.execute('''
        SELECT role, text
        FROM chat_messages 
        WHERE user_id = ? 
        ORDER BY timestamp ASC
    ''', (user_id,))
    
    # Fetch all the results
    messages = cursor.fetchall()
    
    # Close the connection
    conn.close()
    
    return messages

def get_conversation_history(user_id):
    messages = get_user_messages(user_id)
    return "\n".join([f"{role}: {text}" for role, text in messages])

# Example usage:
# insert_chat_message('your_database.db', 1, 'user', 'Hello, how are you?')

def extract_sql_query(response_text):
    match = response_text.split("```")[1].split('sql')[1]
    if match:
        return match
    return None

def execute_sql_query(query):
    conn = sqlite3.connect('restaurant.db')
    cursor = conn.cursor()
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        conn.commit()
        return results
    except sqlite3.Error as e:
        print(f"SQL error: {e}")
        return None
    finally:
        conn.close()


# Assuming the response_text is obtained from the model
# response_text = """
# Okay, I've taken your preferences. Here's your SQL query:
# ```sql
# SELECT
#   RI.name,
#   RI.map_link,
#   RI.contact_info,
#   RI.rating,
#   RI.no_of_reviews
# FROM Restaurant_Info AS RI
# JOIN Restaurant_Keywords AS RK
#   ON RI.restaurant_id = RK.restaurant_id
# JOIN Keywords AS K
#   ON RK.keyword_id = K.keyword_id
# WHERE
#   K.keyword_name = 'pizza'
#   AND RI.restaurant_id IN (
#     SELECT
#       restaurant_id
#     FROM Restaurant_Info
#     WHERE
#       name LIKE '%30%'
#   )
#   AND RI.restaurant_id IN (
#     SELECT
#       restaurant_id
#     FROM Restaurant_Speciality
#     WHERE
#       speciality_id = 3
#   );```
# """

# x = extract_sql_query(response_text)
# print(x)