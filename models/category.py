from db import db
from datetime import datetime
from sqlalchemy.exc import IntegrityError

from config import DEBUG


class CategoryModel(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)

    created = db.Column(db.DateTime, server_default=db.func.now())
    updated = db.Column(db.DateTime, server_default=db.func.now())
    deleted = db.Column(db.DateTime, server_default=None)

    image_name = db.Column(db.String(20),
                           db.ForeignKey("images.name"))
    image = db.relationship("ImageModel")

    tasks = db.relationship("TaskModel", lazy="dynamic")
    achievements = db.relationship("AchievementModel", lazy="dynamic")

    def __init__(self, name, image):
        self.name = name
        self.image_name = image

    def json(self):
        if DEBUG:
            return {
                "id": self.id,
                "name": self.name,
                "image": self.image_name,
                "created": self.created.timestamp(),
                "updated": self.updated.timestamp(),
                "deleted": None if self.deleted is None else self.deleted.timestamp()
            }
        return {
            "name": self.name,
            "image": self.image_name
        }

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_existing_by_id(cls, id):
        return cls.query.filter_by(id=id).filter_by(deleted=None).first()

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_existing_by_name(cls, name):
        return cls.query.filter_by(name=name).filter_by(deleted=None).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_new(cls, last_fetch):
        return cls.query.filter(
            cls.created > datetime.fromtimestamp(last_fetch),
            cls.deleted == None
        )

    @classmethod
    def find_deleted(cls, last_fetch):
        return cls.query.filter(
            cls.created <= datetime.fromtimestamp(last_fetch),
            cls.deleted > datetime.fromtimestamp(last_fetch)
        )

    @classmethod
    def find_updated(cls, last_fetch):
        return cls.query.filter(
            cls.created <= datetime.fromtimestamp(last_fetch),
            cls.deleted == None,
            cls.updated > datetime.fromtimestamp(last_fetch)
        )

    def update(self, data):
        for k in data:
            if k == "image":
                setattr(self, "image_name", data[k])
            else:
                setattr(self, k, data[k])
        setattr(self, "updated", datetime.now())

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        if self.achievements.filter_by(deleted=None).count() or self.tasks.filter_by(deleted=None).count():
            raise IntegrityError(
                "Cannot delete a category if it's associated with tasks or achievements", params=None, orig=None)
        self.deleted = datetime.now()
        db.session.add(self)
        db.session.commit()
