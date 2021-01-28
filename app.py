from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
from flask_sqlalchemy import SQLAlchemy
from flask_json import FlaskJSON, JsonError, json_response, as_json
from sqlalchemy.exc import IntegrityError
from flask_migrate import Migrate
from datetime import datetime
import os

app = Flask(__name__)
FlaskJSON(app)
api = Api(app)

parser = reqparse.RequestParser()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost:8889/Projet_izberg'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#Création des models pour la DB.
#python -m flask db init || migrate || upgrade

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    gamer = db.relationship('Gamer', backref='user')
    comment = db.relationship('Comment', backref='user')
    like = db.relationship('Like', backref='user', uselist=False)
    dislike = db.relationship('Dislike', backref='user', uselist=False)

    def serialize(self):
        return {
            'username': self.username,
            'email': self.email,
            'password': self.password
        }

    parser.add_argument('username')
    parser.add_argument('email')    
    parser.add_argument('password')


class Game(db.Model):
    __tablename__ = 'game'
    id = db.Column(db.Integer, primary_key=True)
    picture_game = db.Column(db.Text, nullable=True)
    number_joueur = db.Column(db.Integer, nullable=True)
    name = db.Column(db.Text, unique=True, nullable=False)
    one_game = db.relationship('One_game', backref='game')
    comment = db.relationship('Comment', backref='game')
    like = db.relationship('Like', backref='game')
    dislike = db.relationship('Dislike', backref='game')

    def serialize(self):
        return {
            'id': self.id,
            'picture_game': self.picture_game,
            'number_joueur': self.number_joueur,
            'name': self.name
        }
    parser.add_argument('picture_game')
    parser.add_argument('number_joueur')    
    parser.add_argument('name')


class One_game(db.Model):
    __tablename__ = 'one_game'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))
    gamer = db.relationship('Gamer', backref='one_game')
    group = db.relationship('Group', backref='one_game')

    def serialize(self):
        return {
            'id': self.id,
            'date': self.date,
            'game_id': self.game_id,
        }
    parser.add_argument('date')
    parser.add_argument('game_id')    


class Gamer(db.Model):
    __tablename__ = 'gamer'
    id = db.Column(db.Integer, primary_key=True)
    score = db.Column(db.Integer, nullable=True, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    one_game_id = db.Column(db.Integer, db.ForeignKey('one_game.id'))


class Group(db.Model):
    __tablename__ = 'group'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    score = db.Column(db.Integer, nullable=True, default=0)
    one_game_id = db.Column(db.Integer, db.ForeignKey('one_game.id'))


class Gamer_group(db.Model):
    __tablename__ = 'gamer_group'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))


class Like(db.Model):
    __tablename__ = 'like'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))


class Dislike(db.Model):
    __tablename__ = 'dislike'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))


class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    content_com = db.Column(db.Text, nullable=False)
    date_com = db.Column(db.Date, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))


#Création des routes pour l'API Rest.

#Classe User.
class AddUser(Resource):
    def post(self):
        args = parser.parse_args()
        username = str(args['username'])
        email = str(args['email'])
        password = str(args['password'])
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return User.serialize(new_user)

class getAllUsers(Resource):
    def get(self):
        my_list = []
        all_users = User.query.all()
        for item in all_users:
            my_list.append(User.serialize(item))
        return my_list

class getOneUser(Resource):
    def get(self, id):
        my_user = User.query.get(id)
        if my_user:
            return User.serialize(my_user)
        else:
            response = {
                "Error": "Aucun utilisateur n'est trouvé avec cette id."
                }
            return response

class editUser(Resource):
    def put(self, id):
        args = parser.parse_args()
        username = str(args['username'])
        email = str(args['email'])
        password = str(args['password'])
        my_user = User.query.get(id)
        if my_user:
            my_user.username = username
            my_user.email = email
            my_user.password = password
            db.session.commit()
        else:
            response = {
                "Error": "Aucun utilisateur n'est trouvé avec cette id."
                }
            return response
        return User.serialize(my_user)

class DeleteUser(Resource):
    def delete(self, id):
        user = User.query.get(id)
        db.session.delete(user)
        db.session.commit()
        response = {
                "success": "L'utilisateur {} a bien été supprimé.".format(user.username)
                }
        return response

#Classe Game.
class AddGame(Resource):
    def post(self):
        args = parser.parse_args()
        picture_game = str(args['picture_game'])
        number_joueur = str(args['number_joueur'])
        name = str(args['name'])
        new_game = Game(picture_game=picture_game, number_joueur=number_joueur, name=name)
        db.session.add(new_game)
        db.session.commit()
        return Game.serialize(new_game)

class getAllGames(Resource):
    def get(self):
        my_list = []
        all_games = Game.query.all()
        for item in all_games:
            my_list.append(Game.serialize(item))
        return my_list

class getOneGame(Resource):
    def get(self, id):
        my_game = Game.query.get(id)
        if my_game:
            return Game.serialize(my_game)
        else:
            response = {
                "Error": "Aucun jeu n'est trouvé avec cette id."
                }
            return response

class editGame(Resource):
    def put(self, id):
        args = parser.parse_args()
        picture_game = str(args['picture_game'])
        number_joueur = str(args['number_joueur'])
        name = str(args['name'])
        my_game = Game.query.get(id)
        if my_game:
            my_game.picture_game = picture_game
            my_game.number_joueur = number_joueur
            my_game.name = name
            db.session.commit()
        else:
            response = {
                "Error": "Aucun jeu n'est trouvé avec cette id."
                }
            return response
        return Game.serialize(my_game)

class DeleteGame(Resource):
    def delete(self, id):
        game = Game.query.get(id)
        db.session.delete(game)
        db.session.commit()
        response = {
                "success": "Le jeu {} a bien été supprimé.".format(game.name)
                }
        return response

#Classe One_game.
class AddOneGame(Resource):
    def post(self):
        args = parser.parse_args()
        date = str(args['date'])
        game_id = str(args['game_id'])
        new_game = Game(date=date, game_id=game_id)
        db.session.add(new_game)
        db.session.commit()
        return One_game.serialize(new_game)


class getAllOneGames(Resource):
    def get(self):
        my_list = []
        all_one_games = One_game.query.all()
        for item in all_one_games:
            my_list.append(One_game.serialize(item))
        return my_list
                     

class getOneOneGame(Resource):
    def get(self, id):
        my_game = One_game.query.get(id)
        if my_game:
            return One_game.serialize(my_game)
        else:
            response = {
                "Error": "Aucun jeu n'est trouvé avec cette id."
                }
            return response


class editOneGame(Resource):
    def put(self, id):
        args = parser.parse_args()
        date = str(args['date'])
        game_id = str(args['game_id'])
        my_game = One_game.query.get(id)
        if my_game:
            my_game.date = date
            my_game.game_id = game_id
            db.session.commit()
        else:
            response = {
                "Error": "Aucun jeu n'est trouvé avec cette id."
                }
            return response
        return One_game.serialize(my_game)


class DeleteOneGame(Resource):
    def delete(self, id):
        game = Game.query.get(id)
        db.session.delete(game)
        db.session.commit()
        response = {
                "success": "Le jeu {} a bien été supprimé.".format(game.name)
                }
        return response
#Routes User.
api.add_resource(AddUser, "/user")
api.add_resource(getAllUsers, "/user")
api.add_resource(getOneUser, "/user/<int:id>")
api.add_resource(editUser, "/user/<int:id>")
api.add_resource(DeleteUser, "/user/<int:id>")

#Routes Game.
api.add_resource(AddGame, "/game")
api.add_resource(getAllGames, "/game")
api.add_resource(getOneGame, "/game/<int:id>")
api.add_resource(editGame, "/game/<int:id>")
api.add_resource(DeleteGame, "/game/<int:id>")

if __name__ == "__main__":
    app.run(debug=True)
