# Personal AI

This app is a personal AI assistant API that can do the following:

- [x] Create a user account
- [x] Login a user
- [x] ...


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

