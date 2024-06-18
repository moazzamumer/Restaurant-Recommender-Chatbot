# Restaurant Recommender Chatbot

This project is a restaurant recommender chatbot built using FastAPI and Google Generative AI (Gemini API). The chatbot interacts with users to collect their preferences and generates SQL queries to fetch restaurant recommendations from a database based on these preferences.

## Features

- Interactive chatbot to collect user preferences for restaurant recommendations.
- Uses Google Generative AI (Gemini API) to format responses and generate SQL queries.
- Iteratively relaxes search criteria if no results are found.
- Asynchronous API built with FastAPI.

## Project Structure

- init.py # Main FastAPI application
- genai.py # GenAI class to handle chatbot logic and interactions
- crud.py # CRUD operations for interacting with the SQLite database
- chat.db # SQLite database file
- requirements.txt # Python dependencies
- README.md # Project README file
- models.py # SQL schema for database setup

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- SQLite

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests.
