from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, jwt_optional, get_jwt_identity
from models.category import CategoryModel
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from config import DEBUG


class Category(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("image",
                        type=str,
                        required=True,
                        help="This field must not be empty."
                        )

    @classmethod
    def get(cls, name):
        category = CategoryModel.find_existing_by_name(name)
        if not category:
            return {"message": "Category not found."}, 404

        return category.json(), 200

    @classmethod
    def post(cls, name):
        category = CategoryModel.find_existing_by_name(name)
        if category:
            return {"message": "Category with name '{}' already exists".format(name)}, 400

        data = cls.parser.parse_args()

        category = CategoryModel(name, **data)
        try:
            category.save_to_db()
        except IntegrityError as e:
            return {"database_exception": str(e)}, 400
        except:
            return {"message": "Internal error occurred during insertion."}, 500

        return category.json(), 201

    @classmethod
    def put(cls, name):
        category = CategoryModel.find_existing_by_name(name)

        data = cls.parser.parse_args()

        if not category:
            category = CategoryModel(name, **data)
        else:
            category.update(data)

        try:
            category.save_to_db()
        except IntegrityError as e:
            return {"database_exception": str(e)}, 400
        except:
            return {"message": "Internal error occurred during the update."}, 500

        return category.json(), 201

    @classmethod
    def delete(cls, name):
        category = CategoryModel.find_existing_by_name(name)

        if not category:
            return {"message": "Category not found"}, 404
        
        try:
            category.delete_from_db()
        except IntegrityError as e:
            return {"database_exception": str(e)}, 400
        except Exception as e:
            return {"message": "Internal error occurred during deletion."}, 500
        
        return {"message": "Category deleted from database."}, 200


class CategoryList(Resource):
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
                "categories": [category.json() for category in CategoryModel.find_all_existing()]
            }

        last_fetch = last_fetch if last_fetch is not None else cls.parser.parse_args()[
            "last_fetch"]

        if DEBUG:
            return {"new": [category.json() for category in CategoryModel.find_new(last_fetch)],
                    "deleted": [category.json() for category in CategoryModel.find_deleted(last_fetch)],
                    "updated": [category.json() for category in CategoryModel.find_updated(last_fetch)],
                    "all": [category.json() for category in CategoryModel.find_all()]
                    }
        return {"new": [category.json() for category in CategoryModel.find_new(last_fetch)],
                "deleted": [category.json() for category in CategoryModel.find_deleted(last_fetch)],
                "updated": [category.json() for category in CategoryModel.find_updated(last_fetch)]
                }
