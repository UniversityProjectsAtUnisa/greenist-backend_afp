from flask_restful import Resource, reqparse
from models.achievement import AchievementModel
from flask_jwt_extended import jwt_required, jwt_optional, get_jwt_identity
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from config import DEBUG


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
        achievement = AchievementModel.find_existing_by_name(name)
        if not achievement:
            return {"message": "Achievement not found"}, 404

        return achievement.json(), 200

    @classmethod
    @jwt_required
    def post(cls, name):
        achievement = AchievementModel.find_existing_by_name(name)
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
    @jwt_required
    def put(cls, name):
        data = cls.parser.parse_args()
        achievement = AchievementModel.find_existing_by_name(name)

        if not achievement:
            print(data)
            achievement = AchievementModel(name, **data)
        else:
            achievement.update(data)

        try:
            achievement.save_to_db()
        except IntegrityError as e:
            return {"database_exception": str(e)}, 400
        except Exception as e:
            return {"message": "Internal error occurred during the update."}, 500

        return achievement.json(), 201

    @classmethod
    @jwt_required
    def delete(cls, name):
        achievement = AchievementModel.find_existing_by_name(name)

        if not achievement:
            return {"message": "Achievement not found"}, 404
        
        try:
            achievement.delete_from_db()
        except IntegrityError as e:
            return {"database_exception": str(e)}, 400
        except:
            return {"message": "Internal error occurred during the update."}, 500

        return {"message": "Achievement deleted from database"}, 200


class AchievementList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("last_fetch",
                        type=float,
                        required=False,
                        help="This field must be a date in unix timestamp in float format.",
                        default=0.0
                        )

    @classmethod
    @jwt_optional
    def get(cls, last_fetch=None):

        user = get_jwt_identity()
        if user: 
            return {
                "achievement": [achievement.json() for achievement in AchievementModel.find_all_existing()]
            }

        last_fetch = last_fetch if last_fetch is not None else cls.parser.parse_args()["last_fetch"]

        if DEBUG:
            return {"new": [achievement.json() for achievement in AchievementModel.find_new(last_fetch)],
                    "deleted": [achievement.json() for achievement in AchievementModel.find_deleted(last_fetch)],
                    "updated": [achievement.json() for achievement in AchievementModel.find_updated(last_fetch)],
                    "all": [achievement.json() for achievement in AchievementModel.find_all()]
                    }
        return {"new": [achievement.json() for achievement in AchievementModel.find_new(last_fetch)],
                "deleted": [achievement.json() for achievement in AchievementModel.find_deleted(last_fetch)],
                "updated": [achievement.json() for achievement in AchievementModel.find_updated(last_fetch)]
                }
