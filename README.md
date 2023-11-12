# AI-Assisted Document Management System

**Description**: The AI-Assisted Document Management System is a Flask-based web application that empowers users to create folders, upload documents, and engage in conversations with an AI assistant that possesses knowledge about the stored information.

## Installation

To get started, you will need Python3 installed: https://www.python.org/downloads/ 
(Dont' forget to choose "Add python.exe" to PATH at the begininng of the installation on Windows).
If you don't have any Relational Database Management System, you can install Postgres Database and PgAdmin here : https://www.postgresql.org/download/windows/ 

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

4. Create a folder named 'data' at the root of the project.

5. Create a file named '.env' at the root of the project.

IN PROGRESS ...



- [x] Create a user account
- [x] Login a user
- [x] Create user folders
- [X] Upload documents in folders
- [X] Chat with a custom assistant based on the user documents
- [X] Chat with a generic assistant to help coding
- [X] Add personnal informations in SQL database


## Installation

### Updating python3 and pip3
```
brew update
brew upgrade python3
pip3 install --upgrade pip
```

### Creating a virtual environment
```
python3 -m venv personal_ai_env
source personal_ai_env/bin/activate

python3 --version 
Python 3.9.7

pip3 --version
pip 21.2.4 
```

### Installing dependencies
```
pip3 install -r requirements.txt
```

en cas d'installation d'un nouveau package : 

```
pip3 freeze > requirements.txt
```

### Installing postgresql

```
brew install postgresql 
brew services start postgresql

```



### Initializing the database

```
flask db init  # Initialise le dossier des migrations
flask db migrate -m "Initial migration."  # Crée la première migration
flask db upgrade  # Applique la migration et crée la base de données
```

#### Gestion des migrations

À chaque fois que vous apportez des modifications à vos modèles, vous devrez créer une nouvelle migration et l'appliquer :
```
flask db migrate -m "Description of the changes."
flask db upgrade
```
À ce stade, votre base de données devrait être initialisée. Si vous utilisez SQLite, vous devriez voir un fichier site.db (ou tout autre nom que vous avez choisi) dans le répertoire racine de votre projet.

