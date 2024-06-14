import google.generativeai as genai
import crud, constants
import re

class GenAI:
    def __init__(self, api_key):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.user_preferences = {}
        self.questions = [
            "What kind of cuisine are you looking to have?",   #cuisine
            "Where are you looking to eat?",                #location
            "What should be the minimum rating of the restaurant?",  #rating
            "What should be the minimum number of reviews for the restaurant?", # no_of_reviews
            "Any specific dishes or specialties you are looking for?"         # dishes
        ]
        self.current_question_index = 0


    def initialize_prompt(self, conversation_history, curr_qs):
        prompt = f"You are a helpful assistant that helps users find restaurants in Moldova based on their preferences by asking questions. \
                Given a user's conversation history and current question that is to be asked. \
                Ask this current question in casual tone keeping in view previous responses. \
                Coversation History : {conversation_history}. \
                Current question to be asked : {curr_qs}. \
                if there is no conversation history, initiate the chat from the message received from user"
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

        # Mapping questions to preference keys
        question_key_map = {
            "What kind of cuisine are you looking to have?": "keyword",
            "Where are you looking to eat?": "location",
            "What should be the minimum rating of the restaurant?": "rating",
            "What should be the minimum number of reviews for the restaurant?": "no_of_reviews",
            "Any specific dishes or specialties you are looking for?": "speciality"
        }

        if self.current_question_index != 0:
            current_question = self.questions[self.current_question_index - 1]
            if current_question in question_key_map:
                question_key = question_key_map[current_question]
                self.user_preferences[question_key] = user_input


    def query_and_result(self, preferences):
        # Default values or extracted values
        keyword = preferences.get("keyword", "")
        query = f"""SELECT * FROM Keywords where keyword_name like %{keyword}%"""
        if query is None:
            keyword = None
        location = preferences.get("location", "")
        query = f"""SELECT * FROM Restaurant_Info where address like %{location}%"""
        if query is None:
            location = None
        rating = preferences.get("rating", 0)
        match = re.search(r'\d+(\.\d+)?', rating)
        if match:
        # Convert the matched string to float if it contains a decimal point, else to int
            number_str = match.group()
            rating = float(number_str) if '.' in number_str else int(number_str)
        no_of_reviews = preferences.get("no_of_reviews", 0)
        match = re.search(r'\d+(\.\d+)?', no_of_reviews)
        if match:
        # Convert the matched string to float if it contains a decimal point, else to int
            number_str = match.group()
            no_of_reviews = float(number_str) if '.' in number_str else int(number_str)
        speciality = preferences.get("speciality", "")
        query = f"""SELECT * FROM  Speciality where speciality_name like %{speciality}%"""
        if query is None:
            speciality = None

        # SQL query template with placeholders
        base_query = f"""
        SELECT
        RI.name,
        RI.map_link,
        RI.contact_info,
        RI.rating,
        RI.no_of_reviews,
        GROUP_CONCAT(DISTINCT K.keyword_name) AS keyword_name,
        GROUP_CONCAT(DISTINCT S.speciality_name) AS speciality_name,
        GROUP_CONCAT(DISTINCT RSM.url) AS social_media_links
        FROM Restaurant_Info RI
        LEFT JOIN Restaurant_Keywords RK ON RI.restaurant_id = RK.restaurant_id
        LEFT JOIN Keywords K ON RK.keyword_id = K.keyword_id
        LEFT JOIN Restaurant_Speciality RS ON RI.restaurant_id = RS.restaurant_id
        LEFT JOIN Speciality S ON RS.speciality_id = S.speciality_id
        LEFT JOIN Restaurant_Social_Media RSM ON RI.restaurant_id = RSM.restaurant_id
        WHERE 1=1
        """
        
        conditions = []
        # Adding conditions based on preferences
        if keyword:
            conditions.append(f"K.keyword_name LIKE '%{keyword}%'")
        if location:
            conditions.append(f"RI.address LIKE '%{location}%'")
        if rating:
            conditions.append(f"RI.rating >= {rating}")
        if no_of_reviews:
            conditions.append(f"RI.no_of_reviews >= {no_of_reviews}")
        if speciality:
            conditions.append(f"S.speciality_name LIKE '%{speciality}%'")

        # Group by clause
        group_by_clause = """
        GROUP BY
        RI.restaurant_id,
        RI.name,
        RI.map_link,
        RI.contact_info,
        RI.rating,
        RI.no_of_reviews;
        """

        # Try queries by removing one condition at a time
        for i in range(len(conditions) + 1):
            query = base_query
            if i < len(conditions):
                query += " AND " + " AND ".join(conditions[:len(conditions) - i])
            query += group_by_clause
            print("Query printed....",query)
            results = crud.execute_sql_query(query)
            if results:
                return results  # Return results if found

        return [] 

    def format_query_results(self, result):
        prompt = f"""
        Given the results of following query : {constants.db_query}. \
        Format the following restaurant information in a beautiful, easy-to-read format:
        {result}.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error: {e}")

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
            result = self.query_and_result(self.user_preferences)
            formatted_result = self.format_query_results(result)
            response = f"Okay, I've taken your preferences. Searching restaurants for you...." + "\n" + "\n" + f"{formatted_result}"
            crud.insert_chat_message(user_id, "model", response)
            print("Model: ", response)
            return response
