from flask_restful import Resource, reqparse
from resources.task import TaskList
from resources.achievement import AchievementList
from resources.category import CategoryList
from datetime import datetime


class Update(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("last_fetch",
                        type=float,
                        required=False,
                        help="This field must be a date in unix timestamp in float format.",
                        default=0.0
                        )

    @classmethod
    def get(cls):
        data = cls.parser.parse_args()
        print(data["last_fetch"])
        
        categories = CategoryList.get(data["last_fetch"])
        achievements = AchievementList.get(data["last_fetch"])
        tasks = TaskList.get(data["last_fetch"])

        return {"last_fetch": datetime.now().timestamp(), "categories": categories, "achievements": achievements, "tasks": tasks}
