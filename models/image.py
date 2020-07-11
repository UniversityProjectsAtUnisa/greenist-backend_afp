from db import db
from models.category import CategoryModel
from sqlalchemy.exc import IntegrityError

class ImageModel(db.Model):
    __tablename__ = "images"
    
    name = db.Column(db.String(20), primary_key=True)
    
    categories = db.relationship("CategoryModel")
    
    def __init__(self, name):
        self.name = name
        
    def json(self):
        return {"name": self.name}
    
    def is_taken(self):
        return len(categories) > 0
    
    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()
        
    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_all_existing(cls):
        return cls.query.filter_by(deleted=None).all()
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
        
    def delete_from_db(self):
        for category in self.categories:
            if not category.deleted:
                raise IntegrityError("Cannot delete an image if it's associated with existing categories", params=None, orig=None)
        for category in self.categories:
            category.image = None
        db.session.delete(self)
        db.session.commit()