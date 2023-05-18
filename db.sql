CREATE TABLE Students (
  id INT PRIMARY KEY AUTO_INCREMENT,
  first_name VARCHAR(50),
  last_name VARCHAR(50),
  username VARCHAR(50),
  password VARCHAR(50)
);

INSERT INTO Students (first_name, last_name, username, password)
VALUES
  ('John', 'Doe', 'johndoe', 'password1'),
  ('Jane', 'Smith', 'janesmith', 'password2'),
  ('Michael', 'Johnson', 'michaelj', 'password3'),
  ('Emily', 'Davis', 'emilyd', 'password4'),
  ('David', 'Anderson', 'davida', 'password5'),
  ('Sarah', 'Wilson', 'sarahw', 'password6'),
  ('Robert', 'Martinez', 'robertm', 'password7'),
  ('Jessica', 'Taylor', 'jessicat', 'password8'),
  ('William', 'Thomas', 'williamt', 'password9'),
  ('Olivia', 'White', 'oliviaw', 'password10');