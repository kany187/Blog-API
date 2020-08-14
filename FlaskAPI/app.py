from flask import Flask, g, jsonify

from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr
from flask_cors import CORS

from auth import auth
import config

import models
from resources.posts import posts_api
from resources.users import users_api


app = Flask(__name__)
cors = CORS(app)

#register the api with app.py
app.register_blueprint(posts_api)
app.register_blueprint(users_api)

limiter = Limiter(app, global_limits=[config.DEFAULT_RATE], key_func=get_ipaddr)
limiter.limit("40/day")(users_api)
limiter.limit(config.DEFAULT_RATE, per_method=True,
            methods=["post","delete"])(posts_api)
#limiter.exempt(posts_api)


@app.route('/')
def hello_world():
    return 'Hello world'

@app.route('/api/v1/users/token', methods=['GET'])
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})

if __name__ == '__main__':
    models.initialize()
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
