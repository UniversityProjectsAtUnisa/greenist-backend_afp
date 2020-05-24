from flask_restful import Api
from flask_jwt_extended import JWTManager
from blacklist import BLACKLIST

from resources.image import Image, ImageList
from resources.category import Category, CategoryList
from resources.task import Task, TaskCreator, TaskList
from resources.achievement import Achievement, AchievementList
from resources.update import Update
from resources.user import UserRegister, UserLogin, UserLogout, User, UserList, TokenRefresh


def create_app():
    from flask import Flask
    app = Flask(__name__)
    app.config.from_object('config.Config')
    return app


app = create_app()
api = Api(app)


@app.route("/")
def home():
    return "Hello World"


jwt = JWTManager(app)

api.add_resource(ImageList, "/images")
api.add_resource(Image, "/image/<string:name>")
api.add_resource(CategoryList, "/categories")
api.add_resource(Category, "/category/<string:name>")
api.add_resource(TaskList, "/tasks")
api.add_resource(TaskCreator, "/task")
api.add_resource(Task, "/task/<int:id>")
api.add_resource(AchievementList, "/achievements")
api.add_resource(Achievement, "/achievement/<string:name>")
api.add_resource(Update, "/update")
api.add_resource(UserRegister, "/register")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")
api.add_resource(User, "/user/<int:id>")
api.add_resource(UserList, "/users")
api.add_resource(TokenRefresh, "/refresh")

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return jti in BLACKLIST

if __name__ == "__main__":
    from db import db
    db.init_app(app)

    @app.before_first_request
    def create_tables():
        db.create_all()

    app.run()
