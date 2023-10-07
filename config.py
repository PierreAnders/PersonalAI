from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')



# class Config:
#     SECRET_KEY = "50c34e5139cb598bf297a67910047d29a422b1bd828557ec"
#     SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:3568@localhost/aria'
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

# basedir = os.path.abspath(os.path.dirname(__file__))
# class Config:
#     SECRET_KEY = os.environ.get('SECRET_KEY')
#     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')\
#         or 'sqlite:///' + os.path.join(basedir, 'app.db')
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

# class Config:
#     SECRET_KEY = "50c34e5139cb598bf297a67910047d29a422b1bd828557ec"
#     SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:3568@localhost/aria'
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

