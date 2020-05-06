from flask_restful import Resource, reqparse
from models.achievement import AchievementModel
from sqlalchemy.exc import IntegrityError


class Achievement(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("desc", type=str, required=True,
                        help="Missing or incorrect field")
    parser.add_argument("goal", type=int, required=True,
                        help="Missing or incorrect field")
    parser.add_argument("below", type=bool, required=True,
                        help="Missing or incorrect field")
    parser.add_argument("category", type=str, required=True,
                        help="Missing or incorrect field")

    @classmethod
    def get(cls, name):
        achievement = AchievementModel.find_by_name(name)
        if not achievement:
            return {"message": "Achievement not found"}, 404

        return achievement.json(), 200

    @classmethod
    def post(cls, name):
        achievement = AchievementModel.find_by_name(name)
        if achievement:
            return {"message": "An Achievement with name '{}' already exists".format(name)}, 400
        
        data = cls.parser.parse_args()
        
        achievement = AchievementModel(name, **data)
        try:
            achievement.save_to_db()
        except IntegrityError as e:
            return {"database_exception": str(e)}, 400
        except:
            return {"message": "Internal error occurred during insertion."}, 500

        return achievement.json(), 201

    @classmethod
    def put(cls, name):
        data = cls.parser.parse_args()
        achievement = AchievementModel.find_by_name(name)

        if not achievement:
            achievement = AchievementModel(**data)
        else:
            for k in data:
                if k == "category": 
                    setattr(achievement, "category_name", data[k])
                else:
                    setattr(achievement, k, data[k])

        try:
            achievement.save_to_db()
        except IntegrityError as e:
            return {"database_exception": str(e)}, 400
        except:
            return {"message": "Internal error occurred during the update."}, 500

        return achievement.json(), 201

    @classmethod
    def delete(cls, name):
        achievement = AchievementModel.find_by_name(name)

        if achievement:
            try:
                achievement.delete_from_db()
            except IntegrityError as e:
                return {"database_exception": str(e)}, 400
            except:
                return {"message": "Internal error occurred during the update."}, 500

        return {"message": "Achievement deleted from database"}, 200


class AchievementList(Resource):
    @classmethod
    def get(cls):
        return {"achievements": [achievement.json() for achievement in AchievementModel.find_all()]}, 200
