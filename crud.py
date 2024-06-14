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




# query = """SELECT
#         RI.name,
#         RI.map_link,
#         RI.contact_info,
#         RI.rating,
#         RI.no_of_reviews,
#         GROUP_CONCAT(DISTINCT K.keyword_name) AS keyword_name,
#         GROUP_CONCAT(DISTINCT S.speciality_name) AS speciality_name,
#         GROUP_CONCAT(DISTINCT RSM.url) AS social_media_links
#         FROM Restaurant_Info RI
#         LEFT JOIN Restaurant_Keywords RK ON RI.restaurant_id = RK.restaurant_id
#         LEFT JOIN Keywords K ON RK.keyword_id = K.keyword_id
#         LEFT JOIN Restaurant_Speciality RS ON RI.restaurant_id = RS.restaurant_id
#         LEFT JOIN Speciality S ON RS.speciality_id = S.speciality_id
#         LEFT JOIN Restaurant_Social_Media RSM ON RI.restaurant_id = RSM.restaurant_id
#         WHERE 1=1
#          OR K.keyword_name LIKE '%Asian%' OR RI.address LIKE '%Moldova%' OR RI.rating >= 4 OR RI.no_of_reviews >= 20 OR S.speciality_name LIKE '%Coffee%'
#         GROUP BY
#         RI.restaurant_id,
#         RI.name,
#         RI.map_link,
#         RI.contact_info,
#         RI.rating,
#         RI.no_of_reviews;"""


# x = execute_sql_query(query)
# print(x)