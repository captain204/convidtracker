from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource
from tracker.http_status import HttpStatus
from tracker.models import db,Intervention,InterventionCategory,InterventionSchema,InterventionCategorySchema,Beneficiary,BeneficiarySchema
from sqlalchemy.exc import SQLAlchemyError
from tracker.helpers import PaginationHelper
from flask_httpauth import HTTPBasicAuth
from flask import g
from tracker.models import User, UserSchema

auth = HTTPBasicAuth()



tracker_blueprint = Blueprint('tracker', __name__)
user_schema = UserSchema()
intervention_schema = InterventionSchema()
intervention_category_schema = InterventionCategorySchema()
beneficiary_schema = BeneficiarySchema()

tracker = Api(tracker_blueprint)

@auth.verify_password
def verify_user_password(username, password):
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        return False
    g.user = user
    return True

    

class AuthenticationRequiredResource(Resource):
    method_decorators = [auth.login_required]
    user_schema = UserSchema()



class UserResource(AuthenticationRequiredResource):
    def get(self, id):
        user = User.query.get_or_404(id)
        result = user_schema.dump(user)
        return result




class UserListResource(Resource):
    @auth.login_required
    def get(self):
        pagination_helper = PaginationHelper(
            request,
            query=User.query,
            resource_for_url='tracker.userlistresource',
            key_name='results',
            schema=user_schema)
        result = pagination_helper.paginate_query()
        return result

    def post(self):
        user_dict = request.get_json()
        if not user_dict:
            response = {'user': 'No input data provided'}
            return response, HttpStatus.bad_request_400.value
        errors = user_schema.validate(user_dict)
        if errors:
            return errors, HttpStatus.bad_request_400.value
        user_name = user_dict['username']
        existing_user = User.query.filter_by(username=user_name).first()
        if existing_user is not None:
            response = {'user': 'A user with the name {} already exists'.format(user_name)}
            return response, HttpStatus.bad_request_400.value
        try:
            user = User(username=user_name)
            error_message, password_ok = \
                user.check_password_strength_and_hash_if_ok(user_dict['password'])
            if password_ok:
                user.add(user)
                query = User.query.get(user.id)
                dump_result = user_schema.dump(query)
                return dump_result, HttpStatus.created_201.value
            else:
                return {"error": error_message}, HttpStatus.bad_request_400.value
        except SQLAlchemyError as e:
            db.session.rollback()
            response = {"error": str(e)}
            return response, HttpStatus.bad_request_400.value


#Single intervention Collection
class InterventionResource(AuthenticationRequiredResource):
    def get(self,id):
        intervention = Intervention.query.get_or_404(id)
        dumped_intervention = intervention_schema.dump(intervention)
        return dumped_intervention

    def patch(self,id):
        intervention = Intervention.query.get_or_404(id)
        intervention_dict = request.get_json(force=True)
        if 'description' in intervention_dict  and intervention_dict['description'] is not None:
            intervention_description = intervention_dict['description']
            #Check if intervention with same description already exist in database
            """if not Intervention.is_description_unique(id = 0, description = intervention_description):
                response = {'error':'An intervention with this description{} already exist'.format(intervention_description)}
                return response, HttpStatus.bad_request_400.value
            intervention.description = intervention_description"""

        try:
            intervention.update()
            response = {'message':'Intervention Updated successfully'}
            return response, HttpStatus.ok_200.value
        except SQLAlchemyError as e:
            db.session.rollback()
            response = {"error":str(e)}
            return response, HttpStatus.bad_request_400.value

    
    def delete(self,id):
        intervention = Intervention.query.get_or_404(id)
        try:
            delete = intervention.delete(intervention)
            response = make_response()
            return response, HttpStatus.no_content_204.value
        except SQLAlchemyError as e:
            db.session.rollback()
            response ={"error":str(e)}
            return response, HttpStatus.unauthorized_401.value




#Collection  of intervntions
class InterventionListResource(AuthenticationRequiredResource):
    def get(self):
        pagination_helper = PaginationHelper(
            request,
            query=Intervention.query,
            resource_for_url='tracker.interventionlistresource',
            key_name='results',
            schema=intervention_schema)
        result = pagination_helper.paginate_query()
        return result

    def post(self):
        intervention_collection = request.get_json()
        if not intervention_collection:        
            response = {'message':'No input data provided'}
            return response, HttpStatus.bad_request_400.value
        errors = intervention_schema.validate(intervention_collection)
        if errors:
            return errors, HttpStatus.bad_request_400.value
        intervention_description = intervention_collection['description']
        if not Intervention.is_description_unique(id=0,description=intervention_description):
            response = {'error':'Intervention already exist'.format(intervention_description)}
            return response, HttpStatus.bad_request_400.value
        try:
            intervention_category_name = intervention_collection['intervention_category']['name'] 
            category = InterventionCategory.query.filter_by(name=intervention_category_name).first()
            if category is None:
                category = InterventionCategory(name=intervention_category_name)
                db.session.add(category)
            # Add new photo
            intervention=Intervention(
                    figures = intervention_collection['figures'],
                    description = intervention_collection['description'],
                    donor = intervention_collection['donor'],
                    intervention_category = category
                )
            intervention.add(intervention)
            query = Intervention.query.get(intervention.id)
            dump_result = intervention_schema.dump(query)
            return dump_result, HttpStatus.created_201.value
        except SQLAlchemyError as e:
            db.session.rollback()
            response = {"error":str(e)}
            return response, HttpStatus.bad_request_400.value




#Single Beneficiary Collection
class BeneficiaryResource(AuthenticationRequiredResource):
    def get(self,id):
        beneficiary = Beneficiary.query.get_or_404(id)
        dumped_beneficiary = beneficiary_schema.dump(beneficiary)
        return dumped_beneficiary

    def patch(self,id):
        beneficiary = Beneficiary.query.get_or_404(id)
        beneficiary_dict = request.get_json(force=True)
        if 'phone' in beneficiary_dict  and beneficiary_dict['phone'] is not None:
            beneficiary_phone = beneficiary_dict['phone']
            #Check if beneficiary with same phone number already exist in database
            """if not Beneficiary.is_phone_unique(id = 0, phone = beneficiary_phone ):
                response = {'error':'A beneficiary with this details{} already exist'.format(beneficiary_phone)}
                return response, HttpStatus.bad_request_400.value
            beneficiary.phone =  beneficiary_phone"""

        try:
            beneficiary.update()
            response = {'message':'Beneficiary Update successfull'}
            return response, HttpStatus.ok_200.value
        except SQLAlchemyError as e:
            db.session.rollback()
            response = {"error":str(e)}
            return response, HttpStatus.bad_request_400.value

    
    def delete(self,id):
        beneficiary = Beneficiary.query.get_or_404(id)
        try:
            delete = beneficiary.delete(beneficiary)
            response = make_response()
            return response, HttpStatus.no_content_204.value
        except SQLAlchemyError as e:
            db.session.rollback()
            response ={"error":str(e)}
            return response, HttpStatus.unauthorized_401.value




#Collection  of Beneficiary
class BeneficiaryListResource(AuthenticationRequiredResource):
    def get(self):
        pagination_helper = PaginationHelper(
            request,
            query=Beneficiary.query,
            resource_for_url='tracker.beneficiarylistresource',
            key_name='results',
            schema=beneficiary_schema)
        result = pagination_helper.paginate_query()
        return result

    def post(self):
        beneficiary_collection = request.get_json()
        if not beneficiary_collection:        
            response = {'message':'No input data provided'}
            return response, HttpStatus.bad_request_400.value
        errors = beneficiary_schema.validate(beneficiary_collection)
        if errors:
            return errors, HttpStatus.bad_request_400.value
        beneficiary_phone = beneficiary_collection['phone']
        if not Beneficiary.is_phone_unique(id=0,phone=beneficiary_phone):
            response = {'error':'Beneficiary already exist'.format(beneficiary_phone)}
            return response, HttpStatus.bad_request_400.value
        try:
            # Add new photo
            beneficiary=Beneficiary(
                    name = beneficiary_collection['name'],
                    phone = beneficiary_collection['phone'],
                    state = beneficiary_collection['state'],
                    lga = beneficiary_collection['lga'],
                    ward = beneficiary_collection['ward'],
                    intervention_type = beneficiary_collection['intervention_type'],
                    age  = beneficiary_collection['age'],
                    education = beneficiary_collection['education'],
                    gender = beneficiary_collection['gender'],
                )
            beneficiary.add(beneficiary)
            query = Beneficiary.query.get(beneficiary.id)
            dump_result = beneficiary_schema.dump(query)
            return dump_result, HttpStatus.created_201.value
        except SQLAlchemyError as e:
            db.session.rollback()
            response = {"error":str(e)}
            return response, HttpStatus.bad_request_400.value






tracker.add_resource(UserListResource, '/users/')
tracker.add_resource(UserResource, '/users/<int:id>')
tracker.add_resource(InterventionListResource,'/intervention/')
tracker.add_resource(InterventionResource,'/intervention/<int:id>')
tracker.add_resource(BeneficiaryListResource,'/beneficiary/')
tracker.add_resource(BeneficiaryResource,'/beneficiary/<int:id>')
