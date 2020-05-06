from db import db
from models.category import CategoryModel


class AchievementModel(db.Model):
    __tablename__ = "achievements"

    name = db.Column(db.String(20), primary_key=True)
    desc = db.Column(db.String(128), nullable=False)
    goal = db.Column(db.Integer, nullable=False)
    below = db.Column(db.Boolean, nullable=False)

    category_name = db.Column(db.String(20), db.ForeignKey("categories.name"))
    category = db.relationship(CategoryModel)

    __table_args__ = (db.CheckConstraint(goal > 0, name="positive_goal"),)

    def __init__(self, name, desc, goal, below, category):
        self.name = name
        self.desc = desc
        self.goal = goal
        self.below = below
        self.category_name = category

    def json(self):
        return {
            "name": self.name,
            "desc": self.desc,
            "goal": self.goal,
            "below": self.below,
            "category": self.category_name
        }

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
