from dotenv import load_dotenv
import os

load_dotenv() 

API_KEY = os.getenv("API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

DB_QUERY = """SELECT
  RI.name,
  RI.map_link,
  RI.contact_info,
  RI.rating,
  RI.no_of_reviews,
  GROUP_CONCAT(DISTINCT K.keyword_name) AS keyword_name,
  GROUP_CONCAT(DISTINCT S.name) AS name,
  GROUP_CONCAT(DISTINCT RSM.url) AS url
FROM Restaurant_Info RI
LEFT JOIN Restaurant_Keywords RK ON RI.restaurant_id = RK.restaurant_id
LEFT JOIN Keywords K ON RK.keyword_id = K.keyword_id
LEFT JOIN Restaurant_Speciality RS ON RI.restaurant_id = RS.restaurant_id
LEFT JOIN Speciality S ON RS.speciality_id = S.speciality_id
LEFT JOIN Restaurant_Social_Media RSM ON RI.restaurant_id = RSM.restaurant_id
GROUP BY
  RI.restaurant_id,
  RI.name,
  RI.map_link,
  RI.contact_info,
  RI.rating,
  RI.no_of_reviews;"""


SCHEMA = """
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