from flask_restful import Resource, reqparse
from models.category import CategoryModel

from sqlalchemy.exc import IntegrityError


class Category(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument("image",
                        type=str,
                        required=True,
                        help="This field must not be emtpy for category creation."
                        )

    @classmethod
    def get(cls, name):
        category = CategoryModel.find_by_name(name)
        if not category:
            return {"message": "Category not found."}, 404

        return category.json(), 200

    @classmethod
    def post(cls, name):
        category = CategoryModel.find_by_name(name)
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
        category = CategoryModel.find_by_name(name)

        data = cls.parser.parse_args()

        if not category:
            category = CategoryModel(name, **data)
        else:
            for k in data:
                if k == "image":
                    setattr(category, "image_name", data[k])
                else:
                    setattr(category, k, data[k])

        try:
            category.save_to_db()
        except IntegrityError as e:
            return {"database_exception": str(e)}, 400
        except:
            return {"message": "Internal error occurred during the update."}, 500

        return category.json(), 201

    @classmethod
    def delete(cls, name):
        category = CategoryModel.find_by_name(name)

        if category:
            try:
                category.delete_from_db()
            except IntegrityError as e:
                return {"database_exception": str(e)}, 400
            except:
                return {"message": "Internal error occurred during deletion."}, 500
        return {"message": "Category deleted from database."}, 200


class CategoryList(Resource):
    @classmethod
    def get(cls):
        return {"categories": [category.json() for category in CategoryModel.find_all()]}, 200
