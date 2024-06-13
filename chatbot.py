import google.generativeai as genai
import crud
import json
import time

api_key = "AIzaSyCq6AMEGQCc73BNKgUvpUQ5JI0H66vGsug"

schema = """
CREATE TABLE Keywords (
    keyword_id INT PRIMARY KEY,
    keyword_name TEXT
);
CREATE TABLE Speciality (
    speciality_id INT PRIMARY KEY,
    name TEXT
);
CREATE TABLE Restaurant_Info (
    restaurant_id INT PRIMARY KEY,
    name TEXT,
    map_link TEXT,
    contact_info TEXT,
    rating FLOAT,
    no_of_reviews INT
);
CREATE TABLE Restaurant_Keywords (
    restaurant_id INT,
    keyword_id INT,
    PRIMARY KEY (restaurant_id, keyword_id),
    FOREIGN KEY (restaurant_id) REFERENCES Restaurant_Info(restaurant_id),
    FOREIGN KEY (keyword_id) REFERENCES Keywords(keyword_id)
);
CREATE TABLE Restaurant_Speciality (
    restaurant_id INT,
    speciality_id INT,
    PRIMARY KEY (restaurant_id, speciality_id),
    FOREIGN KEY (restaurant_id) REFERENCES Restaurant_Info(restaurant_id),
    FOREIGN KEY (speciality_id) REFERENCES Speciality(speciality_id)
);
CREATE TABLE Restaurant_Social_Media (
    restaurant_id INT,
    url TEXT,
    PRIMARY KEY (restaurant_id, url),
    FOREIGN KEY (restaurant_id) REFERENCES Restaurant_Info(restaurant_id)
);
"""

class GenAI:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.user_preferences = {}
        self.questions = [
            "What kind of food are you looking to have?",
            "Where are you looking to eat?",
            "What should be the minimum rating of the restaurant?",
            "What should be the minimum number of reviews for the restaurant?",
            "Any specific keywords or specialties you are looking for?"
        ]
        self.current_question_index = 0

    def ask_next_question(self):
        if self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None

    def collect_preferences(self, user_id, user_input):
        crud.insert_chat_message(user_id, "user", user_input)
        question_key = self.questions[self.current_question_index].split()[0].lower()
        self.user_preferences[question_key] = user_input
        self.current_question_index += 1

    def generate_sql_query(self):
            # Construct the prompt for the Gemini API using the collected preferences
            prompt = f"""
            Given the following schema:
            {schema}

            And the following user preferences:
            {json.dumps(self.user_preferences, indent=2)}

            Generate a SQL query that retrieves restaurant information based on these preferences.
            """
            max_retries = 3
            while max_retries > 0:
                try:
                    response = self.model.generate_content(prompt)
                    return response.text
                except Exception as e:
                    print(f"Error: {e}")
                    max_retries -= 1
                    time.sleep(2)
            return "Error generating SQL query."

    def chatbot(self, user_id, prompt):
        if self.current_question_index < len(self.questions):
            self.collect_preferences(user_id, prompt)
            next_question = self.ask_next_question()

            if next_question:
                response = next_question
            else:
                query = self.generate_sql_query()
                response = f"Okay, I've taken your preferences. Here's your SQL query: {query}"

            crud.insert_chat_message(user_id, "model", response)
            print("Model: ", response)
            return response
        else:
            query = self.generate_sql_query()
            response = f"Okay, I've taken your preferences. Here's your SQL query:\n {query}"
            crud.insert_chat_message(user_id, "model", response)
            print("Model: ", response)
            return response

# # Instantiate the GenAI class
# gen_ai = GenAI(api_key)

# # Example of sequentially calling the chatbot method
# user_inputs = [
#     "I'm looking for Italian food.",
#     "In Chisinau.",
#     "Minimum rating should be 4.5.",
#     "At least 100 reviews.",
#     "Outdoor seating."
# ]

# for user_input in user_inputs:
#     gen_ai.chatbot(1069, user_input)
