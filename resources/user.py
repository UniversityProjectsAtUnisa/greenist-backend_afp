from config import MASTER_PASSWORD
from models.user import UserModel
from flask_restful import Resource, reqparse
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    jwt_refresh_token_required,
    get_jwt_identity,
    get_raw_jwt
)
from blacklist import BLACKLIST


class User(Resource):
    @classmethod
    @jwt_required
    def get(cls, id):
        user = UserModel.find_by_id(id)
        if not user:
            return {"message": "User not found"}, 404
        return user.json(), 201

    @classmethod
    @jwt_required
    def delete(cls, id):
        user = UserModel.find_by_id(id)
        if not user:
            return {"message": "User not found"}, 404

        user.delete_from_db()
        return {"message": "User deleted"}, 200


_user_parser = reqparse.RequestParser()
_user_parser.add_argument("username",
                          type=str, required=True,
                          help="Username should be non-empty string"
                          )
_user_parser.add_argument("password",
                          type=str,
                          required=True,
                          help="Password should be non-empty string"
                          )
_user_parser.add_argument("master_password",
                          type=str,
                          required=False,
                          help="This field must be a string")


class UserList(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        return [user.json() for user in UserModel.find_all()]


class UserRegister(Resource):

    @classmethod
    def post(cls):
        data = _user_parser.parse_args()

        if UserModel.find_by_username(data["username"]):
            return {"message": "User with username '{}' already exists".format(data["username"])}, 400

        if not check_password_hash(MASTER_PASSWORD, data["master_password"]):
            return {"message": "Wrong master_password, please try again or contact your administrator"}

        user = UserModel(
            data["username"],
            generate_password_hash(data["password"], "sha256")
        )
        user.save_to_db()

        return {"message": "User created successfully"}, 201


class UserLogin(Resource):
    @classmethod
    def post(cls):
        data = _user_parser.parse_args()

        user = UserModel.find_by_username(data['username'])

        if not user:
            return {"message": "User not found"}, 404

        if not check_password_hash(user.password, data["password"]):
            return {"message": "Incorrect password"}, 401  # Not authorized

        access_token = create_access_token(identity=user.id, fresh=True)
        refresh_token = create_refresh_token(identity=user.id)
        return {"access_token": access_token, "refresh_token": refresh_token}


class UserLogout(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        # jti is "JWT ID", a unique identifier for JWT
        jti = get_raw_jwt()['jti']
        BLACKLIST.add(jti)
        return {"message": "Successfully logged out"}


class TokenRefresh(Resource):
    @classmethod
    @jwt_refresh_token_required
    def post(cls):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}
