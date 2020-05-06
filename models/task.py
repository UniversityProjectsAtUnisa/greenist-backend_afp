from db import db


class TaskModel(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(128), nullable=False)
    ecoPoints = db.Column(db.Integer, nullable=False)
    savings = db.Column(db.DECIMAL(2), nullable=False)
    weekly = db.Column(db.Boolean, nullable=False)

    category_name = db.Column(db.String(20),
                              db.ForeignKey("categories.name"),
                              nullable=False)
    category = db.relationship("CategoryModel")

    def __init__(self, desc, ecoPoints, savings, weekly, category):
        self.desc = desc
        self.ecoPoints = ecoPoints
        self.savings = savings
        self.weekly = weekly
        self.category_name = category

    def json(self):
        return {
            "id": self.id,
            "desc": self.desc,
            "ecoPoints": self.ecoPoints,
            "savings": format(float(self.savings), ".2f"),
            "weekly": self.weekly,
            "category": self.category_name
        }

    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def find_all(cls):
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
