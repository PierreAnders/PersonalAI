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
