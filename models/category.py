from db import db


class CategoryModel(db.Model):
    __tablename__ = "categories"

    name = db.Column(db.String(20), primary_key=True)

    image_name = db.Column(db.String(20), db.ForeignKey("images.name"), nullable=False)
    images = db.relationship("ImageModel")
    
    tasks = db.relationship("TaskModel", lazy="dynamic")
    achievements = db.relationship("AchievementModel", lazy="dynamic")

    def __init__(self, name, image):
        self.name = name
        self.image_name = image

    def json(self):
        return {
            "name": self.name,
            "image": self.image_name
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
