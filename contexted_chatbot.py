import google.generativeai as genai
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
        self.state = {
            'user_inputs': [],
            'parameters': {
                'rating': None,
                'speciality': None,
                'no_of_reviews': None,
                'location': None
            },
            'interaction_count': 0,
            'max_interactions': 3
        }

    def generate_json_content(self, prompt):
        max_retries = 1
        while max_retries != 0:
            try:
                response = self.model.generate_content(prompt)
                time.sleep(2)
                print(f"Response Text: {response.text}")  
                return response.text
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
            except Exception as e:
                print(f"Error: {e}")
            max_retries -= 1
        return {}

    def get_parsed_input(self, text):
        self.state['user_inputs'].append(text)
        self.state['interaction_count'] += 1
        system_prompt = f"""
        Given user text input, your task is to interact with the user and extract parameters for our database SQL (SQLite Query). Our database contains restaurant info like restaurant name, rating, no_of_reviews, speciality, and location_link.
        The user could give you info like what he/she wants to eat, the minimum rating the restaurant should have.
        If any information is not given, initialize it as None in JSON.
        Here's the schema: {schema}
        Your task is to create a SQL Query that would extract restaurants from the database according to the user's preferences.
        You should understand natural language inputs and accurately identify the required details.
        """
        
        # Add context from previous interactions
        context = '\n'.join(self.state['user_inputs'])
        prompt = f"{system_prompt}\nPrevious context: {context}\nUser input: {text}"

        # Generate content and update parameters
        response = self.generate_json_content(prompt)
        self.update_parameters(response)
        
        # Check if we have enough parameters to generate the final query
        if (all(value is not None for value in self.state['parameters'].values()) or
            self.state['interaction_count'] >= self.state['max_interactions']):
            return self.finalize_query()
        else:
            return self.ask_for_more_info()

    def update_parameters(self, response):
        # Parse the response to extract parameters
        try:
            response_data = json.loads(response)
            if isinstance(response_data, dict):
                if 'rating_min' in response_data:
                    self.state['parameters']['rating'] = response_data['rating_min']
                if 'cuisine' in response_data:
                    self.state['parameters']['speciality'] = response_data['cuisine']
                if 'no_of_reviews_min' in response_data:
                    self.state['parameters']['no_of_reviews'] = response_data['no_of_reviews_min']
                if 'location' in response_data:
                    self.state['parameters']['location'] = response_data['location']
        except json.JSONDecodeError:
            pass

    def finalize_query(self):
        # Generate the final SQL query based on the collected parameters
        query = "SELECT * FROM Restaurant_Info WHERE 1=1"
        if self.state['parameters']['rating']:
            query += f" AND rating >= {self.state['parameters']['rating']}"
        if self.state['parameters']['speciality']:
            query += f""" AND restaurant_id IN (
                SELECT restaurant_id FROM Restaurant_Speciality
                WHERE speciality_id = (
                    SELECT speciality_id FROM Speciality
                    WHERE name = '{self.state['parameters']['speciality']}'
                )
            )"""
        if self.state['parameters']['no_of_reviews']:
            query += f" AND no_of_reviews >= {self.state['parameters']['no_of_reviews']}"
        if self.state['parameters']['location']:
            query += f" AND map_link LIKE '%{self.state['parameters']['location']}%'"
        return query

    def ask_for_more_info(self):
        # Determine which parameter is missing and ask the user for it
        if self.state['parameters']['rating'] is None:
            return "Can you specify the minimum rating the restaurant should have?"
        elif self.state['parameters']['speciality'] is None:
            return "What type of cuisine or speciality are you looking for?"
        elif self.state['parameters']['no_of_reviews'] is None:
            return "How many minimum reviews should the restaurant have?"
        elif self.state['parameters']['location'] is None:
            return "Do you have any specific location or area in mind?"
        return "Please provide more information to refine the search."

# Instantiate the GenAI class
gen_ai = GenAI(api_key)

# Example interaction loop
while True:
    user_input = input("User: ")
    response = gen_ai.get_parsed_input(user_input)
    print(f"Model: {response}")

    # Check if the response is a SQL query
    if response.lower().startswith("select"):
        print(f"Generated SQL Query: {response}")
        break
