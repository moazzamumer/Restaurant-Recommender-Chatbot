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


    def initialize_prompt(self, conversation_history, curr_qs):
        prompt = f"You are a helpful assistant that helps users find restaurants based on their preferences by asking questions. \
                Given a user's conversation history and current question that is to be asked. \
                Ask this current question in casual tone keeping in view previous responses. \
                Coversation History : {conversation_history}. \
                Current question to be asked : {curr_qs}."
        return prompt

    def ask_next_question(self, conversation_history):
        if self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            response = self.model.generate_content(
                self.initialize_prompt(conversation_history, question)
            )
            self.current_question_index += 1
            return response.text
        return None

    def collect_preferences(self, user_id, user_input):
        crud.insert_chat_message(user_id, "user", user_input)
        question_key = self.questions[self.current_question_index - 1].split()[0].lower()
        self.user_preferences[question_key] = user_input

    def generate_sql_query(self):
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

    def chatbot(self, user_id, user_input):
        conversation_history = crud.get_conversation_history(user_id)
        
        if self.current_question_index > 0:
            self.collect_preferences(user_id, user_input)
        
        if self.current_question_index < len(self.questions):
            next_question = self.ask_next_question(conversation_history)
            crud.insert_chat_message(user_id, "model", next_question)
            print("Model: ", next_question)
            return next_question
        else:
            query = self.generate_sql_query()
            formatted_query = crud.extract_sql_query(query)
            result = crud.execute_sql_query(formatted_query)
            response = f"Okay, I've taken your preferences. Searching restaurants for you....\n\n {result}"
            crud.insert_chat_message(user_id, "model", response)
            print("Model: ", response)
            return response
