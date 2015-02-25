from app import app, db

from auth import *
from admin import admin
from models import *
from views import *

admin.setup()


if __name__ == '__main__':
    app.run()
