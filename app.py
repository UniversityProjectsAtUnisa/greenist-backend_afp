from flask_restful import Api

from resources.image import Image, ImageList
from resources.category import Category, CategoryList
from resources.task import Task, TaskCreator, TaskList
from resources.achievement import Achievement, AchievementList


def create_app():
    from flask import Flask
    app = Flask(__name__)
    app.config.from_object('config.Config')
    return app


app = create_app()
api = Api(app)


@app.before_first_request
def create_tables():
    db.create_all()


@app.route("/")
def home():
    return "Hello World"

api.add_resource(ImageList, "/images")
api.add_resource(Image, "/image/<string:name>")

api.add_resource(CategoryList, "/categories")
api.add_resource(Category, "/category/<string:name>")

api.add_resource(TaskList, "/tasks")
api.add_resource(TaskCreator, "/task")
api.add_resource(Task, "/task/<int:id>")

api.add_resource(AchievementList, "/achievements")
api.add_resource(Achievement, "/achievement/<string:name>")

if __name__ == "__main__":
    from db import db
    db.init_app(app)
    app.run()
