from flask_restful import Resource, reqparse
from models.task import TaskModel
from sqlalchemy.exc import IntegrityError


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
        task = TaskModel.find_by_id(id)
        if not task:
            return {"message": "Task not found"}, 404

        return task.json(), 200

    @classmethod
    def put(cls, id):
        data = parser.parse_args()
        task = TaskModel.find_by_id(id)

        if not task:
            task = TaskModel(**data)
        else:
            for k in data:
                if k == "category":
                    setattr(task, "category_name", data[k])
                else:
                    setattr(task, k, data[k])

        try:
            task.save_to_db()
        except IntegrityError as e:
            return {"database_exception": str(e)}, 400
        except:
            return {"message": "Internal error occurred during the update."}, 500

        return task.json(), 201

    @classmethod
    def delete(cls, id):
        task = TaskModel.find_by_id(id)

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
        task = TaskModel(**data)

        try:
            task.save_to_db()
        except IntegrityError as e:
            return {"database_exception": str(e)}, 400
        except Exception as e:
            return {"message": "Internal error occurred during insertion."}, 500

        return task.json(), 201

class TaskList(Resource):
    @classmethod
    def get(cls):
        return {"tasks": [task.json() for task in TaskModel.find_all()]}, 200
