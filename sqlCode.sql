CREATE DATABASE todo_app;

CREATE TABLE users(
	user_id SERIAL PRIMARY KEY,
	user_name VARCHAR(25),
	password VARCHAR(10)
);

CREATE TABLE todo_list(
	task_id SERIAL PRIMARY KEY,
	task VARCHAR(100),
	create_date DATE,
	status VARCHAR(20),
	user_id INT,
	FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE 
);

CREATE TABLE sub_task(
	subtask_id SERIAL,
	task_id INT,
	subtask VARCHAR(100),
	status VARCHAR(20),
	PRIMARY KEY (task_id, subtask_id),
	FOREIGN KEY(task_id) REFERENCES todo_list(task_id) ON DELETE CASCADE
);

INSERT INTO users(user_name, password) VALUES('Dileep K A','password');
INSERT INTO users(user_name, password) VALUES('Midhun','john123');
INSERT INTO users(user_name, password) VALUES('Jayanth','1234');
INSERT INTO users(user_name, password) VALUES('Saurav','chepad');

select * from pg_settings where name ='port' ;

select * from users;
select * from todo_list;
select * from sub_task;
