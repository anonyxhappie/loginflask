from flask import Flask, session, request, logging, jsonify
from flask_mysqldb import MySQL
from flask_restful import Resource, Api
from flask_httpauth import HTTPBasicAuth
import requests

app = Flask(__name__)
api = Api(app, prefix="/loginflask/api/v1")
auth = HTTPBasicAuth()

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'loginflask'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

class Users(Resource):
    def get(self):
        cur = mysql.connection.cursor()
        query = cur.execute("SELECT * FROM users")
        mysql.connection.commit()
        result = {"error": "No Users"}
        if query > 0:
            result = cur.fetchall()
        return jsonify(result)

    def post(self):
        print('one__')
        name = request.json.get('name')
        email = request.json.get('email')
        password = request.json.get('password')
        print('two__')
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO users(name, email, password) VALUES (%s, %s, %s)", (name, email, password))
        mysql.connection.commit()
        return {'status': 'success'}


class User(Resource):
    def get(self, email):
        print('__pp__')
        cur = mysql.connection.cursor()
        query = cur.execute("SELECT * FROM users WHERE email = %s", [email])
        mysql.connection.commit()
        result = {"email": False}
        if query > 0:
            result = cur.fetchone()
        return jsonify(result)


api.add_resource(Users, '/users')
api.add_resource(User, '/user/<email>')

if __name__ == '__main__':
    app.secret_key = 'secret101'
    app.run(debug=True)
