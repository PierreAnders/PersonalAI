# Personal AI


**Description**: "Personal IA" is a Flask-based web application designed to enhance daily life. Users can effortlessly create folders, upload documents, input health-related information, track expenses and income for a monthly budget overview, and engage in conversations with an AI assistant that possesses knowledge about the stored information. Experience seamless organization and assistance in various aspects of your everyday life.


## Installation


To get started, you will need Python 3.11 installed: https://www.python.org/downloads/ 
(Don't forget to choose "Add python.exe" to PATH at the begining of the installation on Windows).
If you don't have any Relational Database Management System, you can install PostgreSQL and PgAdmin here : https://www.postgresql.org/download/windows/ 


1. Create a Virtual Environment: 
```
python -m venv venv
```


2. Activate the Virtual Environment:
```
venv/Scripts/activate 
```


3. Install Dependencies from requirements.txt:

```
pip install -r requirements.txt
```


4. Create a folder named `data` at the root of the project.
When a user registers, a user folder with their UUID will be created in the `data` folder, where it will store their documents.


5. Create a file named `.env` at the root of the project and add the global variables:
```
OPENAI_API_KEY="your_open_ai_api_key"

SECRET_KEY=your_flak_secret_key

SQLALCHEMY_DATABASE_URI=your_database_connection_string
SQLALCHEMY_TRACK_MODIFICATIONS=False
```
To create your Flask secret key you can execute: 
```
python key_creation.py
```
To obtain an OpenAI Key, you need to create an account on the official Open AI website and generate an API Key.


## Initializing the database


```
flask db init  # initialize the migration folder
```
You will now see an `Migrations` folder. Inside, in the `env.py`, add this code:

```
from app.users.model import User
from app.expenses.model import Expense
from app.incomes.model import Income
from app.healths.model import Health
from app.folders.model import Folder
from app.files.model import File

target_metadata = User.metadata
target_metadata = Expense.metadata
target_metadata = Income.metadata
target_metadata = Health.metadata
target_metadata = Folder.metadata
target_metadata = File.metadata
```

You can know make the migration:
```
flask db migrate -m "Initial migration."  # Create the first migration file
flask db upgrade  # Execute the migration
```


## Running the Application
To run the application, use the following command:


```
flask run
```


## Features

- Create a user account
- Login a user
- Create user folders
- Upload documents in folders
- Chat with a custom assistant based on the user documents
- Chat with a generic assistant to help coding
- Add personnal informations in SQL database



## Contribution
We welcome contributions from fellow developers to enhance "Personal IA." If you're interested in contributing, follow these steps:


Fork the repository.
Create a new branch for your feature or bug fix: git checkout -b feature-name.
Make your changes and commit them: git commit -m 'Description of the changes'.
Push your changes to your fork: git push origin feature-name.
Open a pull request, detailing the changes you made and why they're valuable.
For bug reports, feature requests, or other issues, please utilize the GitHub issue tracker. We appreciate your efforts to make "Personal IA" even better!


## License
This project is released under the MIT License, allowing for flexibility in its use, modification, and distribution..


### Authors
The primary contributor to this project is Pierre Untas.

