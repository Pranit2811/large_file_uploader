# large_file_uploader


------Prerequisites------

Database Setup
Ensure you have a PostgreSQL database up and running. You can use tools like DBeaver or pgAdmin for database management.

Database Table Creation
Execute the following SQL commands to set up your database:

sql

CREATE TABLE information_schema.users (
    id serial NOT NULL,
    username varchar(10485760) NULL,
    hashed_password varchar(10485760) NULL
);

INSERT INTO public.users
(id, username, hashed_password)
VALUES(2, 'pranit', '$2b$12$Yd8TwpmvfZj.lQ2rW.YBfuT2niSHab6il03N5FaETfW7UKADiVrRC');

Note: The default username is pranit and the password is pass.

----Step-by-Step Instructions---

1. Clone the Project
Open your terminal or command prompt and run the following command to clone the project repository:
git clone https://github.com/Pranit2811/large_file_uploader.git

2. Navigate to the Project Directory
Change your current directory to the cloned project folder:
cd large_file_uploader

3. Install Required Packages
Make sure you have Python installed on your system. Then, install the necessary dependencies by executing:
pip install -r requirements.txt

4. Start the FastAPI Server
To run the FastAPI application, execute the following command:
python main.py
You should see output indicating that the server is running, typically on http://127.0.0.1:8000.

****Start Consumer Using Command: celery -A task worker -B -Q FILE_UPLOADER

6. Access the Login Page
Open your web browser and navigate to the following URL:
http://127.0.0.1:8000/login/

7. Log In
Use the default credentials to log in:

Username: pranit
Password: pass
After successfully logging in, you will be redirected to the home page.

Home Page Overview
On the home page, you will find links to different functionalities of the application:

Upload Data: Use this option to upload large files to the server.(Db)

Query Builder: This feature allows you to build and execute queries against your database.

Users: Manage user accounts and access permissions.

****Additional Notes****
Ensure your PostgreSQL server is running and accessible when you start the FastAPI application.
You may need to adjust the database connection settings in the application’s configuration file, typically found in the project directory.
If you encounter any issues, check the console output for error messages and troubleshooting tips.
