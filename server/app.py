from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from config import create_app, db, api
from models import User, Recipe, Plant

app = create_app()

@app.before_request
def check_if_logged_in():
    open_access_list = [
        'signup',
        'login',
        'check_session'
    ]

    if (request.endpoint) not in open_access_list and (not session.get('user_id')):
        return {'error': '401 Unauthorized'}, 401

class Signup(Resource):
    def post(self):
        request_json = request.get_json()
        username = request_json.get('username')
        password = request_json.get('password')
        image_url = request_json.get('image_url')
        bio = request_json.get('bio')

        user = User(
            username=username,
            image_url=image_url,
            bio=bio
        )

        user.password_hash = password

        try:
            db.session.add(user)
            db.session.commit()
            session['user_id'] = user.id
            return user.to_dict(), 201
        except IntegrityError:
            return {'error': '422 Unprocessable Entity'}, 422

class CheckSession(Resource):
    def get(self):
        user_id = session['user_id']
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            return user.to_dict(), 200
        return {}, 401

class Login(Resource):
    def post(self):
        request_json = request.get_json()
        username = request_json.get('username')
        password = request_json.get('password')

        user = User.query.filter(User.username == username).first()
        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200
        return {'error': '401 Unauthorized'}, 401

class Logout(Resource):
    def delete(self):
        session['user_id'] = None
        return {}, 204

class RecipeIndex(Resource):
    def get(self):
        user = User.query.filter(User.id == session['user_id']).first()
        return [recipe.to_dict() for recipe in user.recipes], 200

    def post(self):
        request_json = request.get_json()
        title = request_json['title']
        instructions = request_json['instructions']
        minutes_to_complete = request_json['minutes_to_complete']

        try:
            recipe = Recipe(
                title=title,
                instructions=instructions,
                minutes_to_complete=minutes_to_complete,
                user_id=session['user_id'],
            )
            db.session.add(recipe)
            db.session.commit()
            return recipe.to_dict(), 201
        except IntegrityError:
            return {'error': '422 Unprocessable Entity'}, 422

class PlantResource(Resource):
    def get(self, id):
        try:
            plant = Plant.query.get(id)
            if plant:
                return plant.to_dict(), 200
            return {'error': 'Plant not found'}, 404
        except Exception as e:
            logger.error(f"Error fetching plant with id {id}: {e}")
            return {'error': 'Internal Server Error'}, 500

    def patch(self, id):
        try:
            plant = Plant.query.get(id)
            if not plant:
                return {'error': 'Plant not found'}, 404

            request_json = request.get_json()
            if 'is_in_stock' in request_json:
                plant.is_in_stock = request_json['is_in_stock']

            db.session.commit()
            return plant.to_dict(), 200
        except IntegrityError:
            db.session.rollback()
            return {'error': '422 Unprocessable Entity'}, 422
        except Exception as e:
            logger.error(f"Error updating plant with id {id}: {e}")
            return {'error': 'Internal Server Error'}, 500

    def delete(self, id):
        try:
            plant = Plant.query.get(id)
            if not plant:
                return {'error': 'Plant not found'}, 404

            db.session.delete(plant)
            db.session.commit()
            return {}, 204
        except Exception as e:
            logger.error(f"Error deleting plant with id {id}: {e}")
            return {'error': 'Internal Server Error'}, 500



api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')
api.add_resource(PlantResource, '/plants/<int:id>', endpoint='plant')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
