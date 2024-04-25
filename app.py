from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import os

app = Flask(__name__, static_url_path='/static')
app.config["MONGO_URI"] = "mongodb://username:password@mongodb.default.svc.cluster.local:27017/mydatabase"
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this to a secure secret key
app.config["TEMPLATE_DIR"] = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
mongo = PyMongo(app)
jwt = JWTManager(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        password = data.get('password')

        # Check if username already exists
        if mongo.db.users.find_one({"username": username}):
            return jsonify({"message": "Username already exists"}), 400

        # Insert new user into the database
        mongo.db.users.insert_one({
            "username": username,
            "password": password,
            "role": "user"
        })

        return jsonify({'message': 'Signup successful'})
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        password = data.get('password')

        user = mongo.db.users.find_one({"username": username, "password": password})

        if not user:
            return jsonify({"message": "Invalid username or password"}), 401

        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token)
    return render_template('login.html')

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return render_template('protected.html', current_user=current_user)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
