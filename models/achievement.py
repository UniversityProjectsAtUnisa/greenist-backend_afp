from db import db
from datetime import datetime
from models.category import CategoryModel

from config import DEBUG


class AchievementModel(db.Model):
    __tablename__ = "achievements"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    desc = db.Column(db.String(128), nullable=False)
    goal = db.Column(db.Integer, nullable=False)
    below = db.Column(db.Boolean, nullable=False)

    created = db.Column(db.DateTime, server_default=db.func.now())
    updated = db.Column(db.DateTime, server_default=db.func.now())
    deleted = db.Column(db.DateTime, server_default=None)

    category_id = db.Column(db.Integer,
                            db.ForeignKey("categories.id"),
                            nullable=False)
    category = db.relationship("CategoryModel")

    __table_args__ = (db.CheckConstraint(goal > 0, name="positive_goal"),)

    def __init__(self, name, desc, goal, below, category):
        self.name = name
        self.desc = desc
        self.goal = goal
        self.below = below
        self.category_id = getattr(
            CategoryModel.find_existing_by_name(category), "id", None)

    def json(self):
        if DEBUG:
            return {
                "id": self.id,
                "name": self.name,
                "desc": self.desc,
                "goal": self.goal,
                "below": self.below,
                "category": CategoryModel.find_existing_by_id(self.category_id).name,
                "image": CategoryModel.find_existing_by_id(self.category_id).image,
                "created": self.created.timestamp(),
                "updated": self.updated.timestamp(),
                "deleted": None if self.deleted is None else self.deleted.timestamp()
            }
        return {
            "name": self.name,
            "desc": self.desc,
            "goal": self.goal,
            "below": self.below,
            "category": CategoryModel.find_existing_by_id(self.category_id).name,
            "image": CategoryModel.find_existing_by_id(self.category_id).name
        }

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
            cls.created < datetime.fromtimestamp(last_fetch),
            cls.deleted > datetime.fromtimestamp(last_fetch)
        )

    @classmethod
    def find_updated(cls, last_fetch):
        return cls.query.filter(
            cls.created < datetime.fromtimestamp(last_fetch),
            cls.deleted == None,
            cls.updated > datetime.fromtimestamp(last_fetch)
        )

    def update(self, data):
        for k in data:
            if k == "category":
                setattr(self, "category_id",
                        getattr(CategoryModel.find_existing_by_name(data[k]), "id", None))
            else:
                setattr(self, k, data[k])
        setattr(self, "updated", datetime.now())

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        self.deleted = datetime.now()
        db.session.add(self)
        db.session.commit()
