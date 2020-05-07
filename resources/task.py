from flask_restful import Resource, reqparse
from models.task import TaskModel
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from config import DEBUG


parser = reqparse.RequestParser()
parser.add_argument("desc", type=str, required=True,
                    help="Missing or incorrect field")
parser.add_argument("ecoPoints", type=int, required=True,
                    help="Missing or incorrect field")
parser.add_argument("savings", type=float, required=True,
                    help="Missing or incorrect field")
parser.add_argument("weekly", type=bool, required=True,
                    help="Missing or incorrect field")
parser.add_argument("category", type=str, required=True,
                    help="Missing or incorrect field")


class Task(Resource):

    @classmethod
    def get(cls, id):
        task = TaskModel.find_existing_by_id(id)
        if not task:
            return {"message": "Task not found"}, 404

        return task.json(), 200

    @classmethod
    def put(cls, id):
        data = parser.parse_args()
        task = TaskModel.find_existing_by_id(id)

        if not task:
            task = TaskModel(**data)
        else:
            task.update(data)

        try:
            task.save_to_db()
        except IntegrityError as e:
            return {"database_exception": str(e)}, 400
        except:
            return {"message": "Internal error occurred during the update."}, 500

        return task.json(), 201

    @classmethod
    def delete(cls, id):
        task = TaskModel.find_existing_by_id(id)

        if task:
            try:
                task.delete_from_db()
            except IntegrityError as e:
                return {"database_exception": str(e)}, 400
            except:
                return {"message": "Internal error occurred during the update."}, 500

        return {"message": "Task deleted from database"}, 200


class TaskCreator(Resource):
    @classmethod
    def post(cls):
        data = parser.parse_args()

        try:
            task = TaskModel(**data)
            task.save_to_db()
        except IntegrityError as e:
            return {"database_exception": str(e)}, 400
        except Exception as e:
            return {"message": "Internal error occurred during insertion."}, 500

        return task.json(), 201


class TaskList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("last_fetch",
                        type=float,
                        required=False,
                        help="This field must be a date in unix timestamp in float format.",
                        default=0.0
                        )

    @classmethod
    def get(cls, last_fetch=None):
        last_fetch = last_fetch if last_fetch is not None else cls.parser.parse_args()["last_fetch"]

        if DEBUG:
            return {"new": [task.json() for task in TaskModel.find_new(last_fetch)],
                    "deleted": [task.json() for task in TaskModel.find_deleted(last_fetch)],
                    "updated": [task.json() for task in TaskModel.find_updated(last_fetch)],
                    "all": [task.json() for task in TaskModel.find_all()]
                    }
        return {"new": [task.json() for task in TaskModel.find_new(last_fetch)],
                "deleted": [task.json() for task in TaskModel.find_deleted(last_fetch)],
                "updated": [task.json() for task in TaskModel.find_updated(last_fetch)]
                }
