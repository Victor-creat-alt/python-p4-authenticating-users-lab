#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource
from sqlalchemy.orm import Session

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)
api = Api(app)


# Login Resource
class Login(Resource):
    def post(self):
        # Get username from request JSON
        data = request.get_json()
        username = data.get('username')

        # Find the user by username
        user = User.query.filter_by(username=username).first()
        if not user:
            return {'message': "User not found"}, 404
        
        # Set user_id in session
        session['user_id'] = user.id

        # Return user as JSON
        user_data = {
            'id': user.id,
            'username': user.username
        }
        return jsonify(user_data)

# Logout Resource
class Logout(Resource):
    def delete(self):
        # Remove user_id from session
        session.pop('user_id', None)
        return '', 204

# Check Session Resource
class CheckSession(Resource):
    def get(self):
        # Check if user_id exists in session
        user_id = session.get('user_id')
        if not user_id:
            return {}, 401

        # Retrieve user using Session.get() for compatibility with SQLAlchemy 2.0
        with db.session() as db_session:
            user = db_session.get(User, user_id)
        if not user:
            return {'message': 'User not found'}, 404

        # Return user as JSON
        user_data = {
            'id': user.id,
            'username': user.username
        }
        return jsonify(user_data)

# Clear Session Resource
class ClearSession(Resource):
    def delete(self):
        # Clear session data
        session['page_views'] = None
        session['user_id'] = None
        return {}, 204

# Index Article Resource
class IndexArticle(Resource):
    def get(self):
        # Retrieve all articles and return as JSON
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

# Show Article Resource
class ShowArticle(Resource):
    def get(self, id):
        # Initialize or increment page views
        session['page_views'] = session.get('page_views', 0)
        session['page_views'] += 1

        if session['page_views'] <= 3:
            # Fetch the article by ID
            article = Article.query.filter(Article.id == id).first()
            if not article:
                return {'message': 'Article not found'}, 404

            # Return article data as JSON
            return make_response(jsonify(article.to_dict()), 200)

        # Return error if page view limit is exceeded
        return {'message': 'Maximum pageview limit reached'}, 401


# Add Resources to API
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(CheckSession, '/check_session')
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(ShowArticle, '/articles/<int:id>')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
