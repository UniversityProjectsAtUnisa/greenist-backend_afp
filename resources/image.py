from flask_restful import Resource
from models.image import ImageModel

from sqlalchemy.exc import IntegrityError


class Image(Resource):

    @classmethod
    def get(cls, name):
        image = ImageModel.find_by_name(name)
        if not image:
            return {"message": "Image not found."}, 404
        return image.json(), 200

    @classmethod
    def post(cls, name):
        image = ImageModel.find_by_name(name)
        if image:
            return {"message": "An image with name '{}' already exists.".format(name)}, 400

        image = ImageModel(name)
        try:
            image.save_to_db()
        except IntegrityError as e:
            return {"database_exception": str(e)}, 400
        except:
            return {"message": "Internal error occurred during insertion."}, 500

        return image.json(), 201

    @classmethod
    def put(cls, name):
        image = ImageModel.find_by_name(name)
        if not image:
            image = ImageModel(name)
        else:
            image.name = name

        try:
            image.save_to_db()
        except IntegrityError as e:
            return {"database_exception": str(e)}, 400
        except:
            return {"message": "Internal error occurred during the update."}, 500

        return image.json(), 201

    @classmethod
    def delete(cls, name):
        image = ImageModel.find_by_name(name)

        if image:
            try:
                image.delete_from_db()
            except IntegrityError as e:
                return {"database_exception": str(e)}, 400
            except Exception as e:
                return {"message": "Internal error occurred during deletion."+str(e)}, 500
        return {"message": "Image deleted from database."}, 200


class ImageList(Resource):
    @classmethod
    def get(cls):
        return {"images": [image.json() for image in ImageModel.find_all()]}, 200
