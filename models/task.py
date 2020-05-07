from db import db
from datetime import datetime
from models.category import CategoryModel

from config import DEBUG


class TaskModel(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(128), nullable=False)
    ecoPoints = db.Column(db.Integer, nullable=False)
    savings = db.Column(db.DECIMAL(2), nullable=False)
    weekly = db.Column(db.Boolean, nullable=False)

    created = db.Column(db.DateTime, server_default=db.func.now())
    updated = db.Column(db.DateTime, server_default=db.func.now())
    deleted = db.Column(db.DateTime, server_default=None)

    category_id = db.Column(db.Integer,
                            db.ForeignKey("categories.id"),
                            nullable=False)
    category = db.relationship("CategoryModel")

    def __init__(self, desc, ecoPoints, savings, weekly, category):
        self.desc = desc
        self.ecoPoints = ecoPoints
        self.savings = savings
        self.weekly = weekly
        self.category_id = getattr(CategoryModel.find_existing_by_name(category), "id", None)

    def json(self):
        if DEBUG:
            return {
                "id": self.id,
                "desc": self.desc,
                "ecoPoints": self.ecoPoints,
                "savings": format(float(self.savings), ".2f"),
                "weekly": self.weekly,
                "category":  CategoryModel.find_existing_by_id(self.category_id).name,
                "created": self.created.timestamp(),
                "updated": self.updated.timestamp(),
                "deleted": None if self.deleted is None else self.deleted.timestamp()
            }
        return {
            "id": self.id,
            "desc": self.desc,
            "ecoPoints": self.ecoPoints,
            "savings": format(float(self.savings), ".2f"),
            "weekly": self.weekly,
            "category":  CategoryModel.find_existing_by_id(self.category_id).name
        }

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_existing_by_id(cls, id):
        return cls.query.filter_by(id=id).filter_by(deleted=None).first()

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
