#!/usr/bin/env python3

import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'instance/app.db')}")

from flask import Flask, make_response, jsonify, request
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Activity, Camper, Signup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

@app.route('/')
def home():
    return ''


class Campers (Resource):

    def get(self):
        get_campers = [c.to_dict( only=('id','name','age') ) for c in Camper.query.all()]
        return get_campers, 200
    
    def post(self):
        try:
            new_camper = Camper(name=request.json['name'], age=request.json['age'])
            db.session.add(new_camper)
            db.session.commit()
            return new_camper.to_dict(), 201
        except:
            return {'error': 'Camper not created'}, 400
        
    
api.add_resource(Campers, '/campers')

class CamperById (Resource):
    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if not camper:
            return {'error': 'Camper not found'}, 404
        return camper.to_dict(rules=('-activity.camper',)), 200
    
api.add_resource(CamperById, '/campers/<int:id>')


class Activities (Resource):
    def get(self):
        get_activities = [a.to_dict( only=('id','name','difficulty') ) for a in Activity.query.all()]
        return get_activities, 200
api.add_resource(Activities, '/activities')

class ActivityById (Resource):
    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()
        if not activity:
            return {'error': 'Activity not found'}, 404
        db.session.delete(activity)
        db.session.commit()
        return make_response('', 204)
    
api.add_resource(ActivityById, '/activities/<int:id>')

class Signups(Resource):
    def post(self):
        try:
            new_signup = Signup(time=request.json['time'],camper_id=request.json['camper_id'], activity_id=request.json['activity_id'])
            db.session.add(new_signup)
            db.session.commit()
            return new_signup.to_dict(), 201
        except:
            return {'error': 'Signup not created'}, 400
api.add_resource(Signups, '/signups')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
