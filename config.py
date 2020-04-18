
import os
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = False
#SQLALCHEMY_DATABASE_URI ="postgresql:///photodb" 
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') 
#SQLALCHEMY_DATABASE_URL = 'sqlite:///' + os.path.join(basedir, 'db.tracker_db')

SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')


"""
import os
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI ="postgresql:///tracker" 
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
"""

PAGINATION_PAGE_SIZE = 4
PAGINATION_PAGE_ARGUMENT_NAME = 'page'





PAGINATION_PAGE_SIZE = 4
PAGINATION_PAGE_ARGUMENT_NAME = 'page'


	

