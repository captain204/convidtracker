from marshmallow import Schema, fields, pre_load
from marshmallow import validate
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from passlib.apps import custom_app_context as password_context
import re


db = SQLAlchemy()
ma = Marshmallow()


class ResourceAddUpdateDelete():   
    def add(self, resource):
        db.session.add(resource)
        return db.session.commit()

    def update(self):
        return db.session.commit()

    def delete(self, resource):
        db.session.delete(resource)
        return db.session.commit()



class User(db.Model, ResourceAddUpdateDelete):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    creation_date = db.Column(db.TIMESTAMP,server_default=db.func.current_timestamp(), nullable=False)

    def verify_password(self, password):
        return password_context.verify(password, self.password_hash)

    def check_password_strength_and_hash_if_ok(self, password):
        if len(password) < 8:
            return 'The password is too short. Please, specify a password with at least 8 characters.', False
        if len(password) > 32:
            return 'The password is too long. Please, specify a password with no more than 32 characters.', False

        if re.search(r'[A-Z]', password) is None:
            return 'The password must include at least one uppercase letter.', False

        if re.search(r'[a-z]', password) is None:
            return 'The password must include at least one lowercase letter.', False

        if re.search(r'\d', password) is None:
            return 'The password must include at least one number.', False

        if re.search(r"[ !#$%&'()*+,-./[\\\]^_`{|}~"+r'"]',password) is None:
            return 'The password must include at least one symbol.', False

        self.password_hash = password_context.hash(password)
        return '', True

    def __init__(self, username):
        self.username = username




class UserSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(required=True,validate=validate.Length(3))
    password = fields.String(required=True,validate=validate.Length(6))
    url = ma.URLFor('tracker.userresource',id='<id>',_external=True)


class Intervention(db.Model,ResourceAddUpdateDelete):
    id = db.Column(db.Integer, primary_key=True)
    figures = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), unique=True, nullable=False)
    donor = db.Column(db.String(250), nullable=False)
    state = db.Column(db.String(250), nullable=False)
    lat = db.Column(db.String(100), nullable=False)
    longitiude = db.Column(db.String(100), nullable=False)
    intervention_category_id = db.Column(db.Integer, db.ForeignKey('intervention_category.id', ondelete='CASCADE'), nullable=False)
    intervention_category = db.relationship('InterventionCategory', backref=db.backref('interventions', lazy='dynamic' , order_by='Intervention.description'))
    creation_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)

    def __init__(self, figures, description, donor,state,lat,longitiude,intervention_category):
        self.figures = figures
        self.description = description
        self.donor = donor
        self.state = state
        self.lat = lat
        self.longitiude = longitiude
        self.intervention_category = intervention_category


    @classmethod
    def is_description_unique(cls, id, description):
        existing_intervention_category = cls.query.filter_by(description=description).first()
        if existing_intervention_category is None:
            return True
        else:
            if existing_intervention_category.id == id:
                return True
            else:
                return False





class InterventionCategory(db.Model,ResourceAddUpdateDelete):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    @classmethod
    def is_name_unique(cls, id, name):
        existing_intervention_category = cls.query.filter_by(name=name).first()
        if existing_intervention_category is None:
            return True
        else:
            if existing_intervention_category.id == id:
                return True
            else:
                return False




class InterventionCategorySchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    # Minimum length = 3 characters
    name = fields.String(required=True, 
        validate=validate.Length(3))
    url = ma.URLFor('tracker.interventionresource', 
        id='<id>', 
        _external=True)
    interventions = fields.Nested('InterventionSchema', 
        many=True, 
        exclude=('intervention_category',))



class InterventionSchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    figures = fields.Integer()
    description= fields.String(required=True, 
        validate=validate.Length(3))
    donor= fields.String(required=True, 
        validate=validate.Length(3))
    state= fields.String(required=True, 
        validate=validate.Length(3))
    lat = fields.String(required=True, 
        validate=validate.Length(1))
    longitiude = fields.String(required=True, 
        validate=validate.Length(1))
    intervention_category = fields.Nested(InterventionCategorySchema, 
        only=['id', 'url', 'name'], 
        required=True)
    url = ma.URLFor('tracker.interventionresource', 
        id='<id>', 
        _external=True)




    @pre_load
    def process_intervention_category(self, data,**kwargs):
        intervention_category = data.get('intervention_category')
        if intervention_category:
            if isinstance(intervention_category, dict):
                intervention_category_name = intervention_category.get('name')
            else:
                intervention_category_name = intervention_category 
            intervention_category_dict = dict(name=intervention_category_name)
        else:
            intervention_category_dict = {}
        data['intervention_category'] =  intervention_category_dict
        return data


class Beneficiary(db.Model,ResourceAddUpdateDelete):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    phone = db.Column(db.String(250), unique=True, nullable=False)
    states = db.Column(db.String(250), nullable=False)
    lga = db.Column(db.String(250), nullable=False)
    ward = db.Column(db.String(250), nullable=False)
    intervention_type = db.Column(db.String(250), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    education = db.Column(db.String(250), nullable=False)
    gender = db.Column(db.String(250), nullable=False)
    creation_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)


    def __init__(self, name, phone, state, lga, ward, intervention_type, age, education, gender):
        self.name = name
        self.phone = phone
        self.state = state
        self.lga = lga
        self.ward = ward
        self.intervention_type = intervention_type
        self.age = age
        self.education = education
        self.gender = gender


    @classmethod
    def is_phone_unique(cls, id, phone):
        existing_phone = cls.query.filter_by(phone=phone).first()
        if existing_phone is None:
            return True
        else:
            if existing_phone.id == id:
                return True
            else:
                return False


class BeneficiarySchema(ma.Schema):
    id = fields.Integer(dump_only=True)
    # Minimum length = 3 characters
    name = fields.String(required=True, 
        validate=validate.Length(3))
    phone = fields.String(required=True, 
        validate=validate.Length(11))
    state = fields.String(required=True, 
        validate=validate.Length(3))
    lga = fields.String(required=True, 
        validate=validate.Length(3))
    ward = fields.String(required=True, 
        validate=validate.Length(3))
    intervention_type = fields.String(required=True, 
        validate=validate.Length(3))
    age = fields.Integer()
    education = fields.String(required=True, 
        validate=validate.Length(3))
    gender = fields.String(required=True, 
        validate=validate.Length(3))
    creation_date = fields.DateTime()
    url = ma.URLFor('tracker.beneficiaryresource', 
        id='<id>', 
        _external=True)
    





    