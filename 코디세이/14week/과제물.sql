CREATE DATABASE IF NOT EXISTS testdb;
use testdb


CREATE TABLE mars_weather (
    weather_id INT AUTO_INCREMENT PRIMARY KEY,
    mars_date DATETIME NOT NULL,
    temp INT,
    storm INT
);
select * from mars_weather