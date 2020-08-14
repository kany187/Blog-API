from flask import jsonify, Blueprint, abort

from flask_restful import (Resource, Api, reqparse, fields,
marshal, marshal_with, url_for)

from auth import auth
import models


posts_fields = {
    'content' : fields.String,
    'id': fields.Integer,
    'title': fields.String
}

def post_or_404(post_id):
    try:
        post = models.Post.get(models.Post.id == post_id)

    except models.Post.DoesNotExist:
        abort(404)
    
    else:
        return post


class PostList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'content',
            required = True,
            help = 'No content provided',
            location = ['form','json']
        )
        self.reqparse.add_argument(
            'id',
            required = True,
            help = 'No id provided',
            location = ['form','json']
        )
        self.reqparse.add_argument(
            'title',
            required = True,
            help = 'No content provided',
            location = ['form','json']
        )
        super().__init__()

    def get(self):
        posts = [marshal(posts, posts_fields) 
                for posts in models.Post.select()]
        return {'posts': posts}

    @marshal_with(posts_fields)
    @auth.login_required
    def post(self):
        args = self.reqparse.parse_args()
        post = models.Post.create(**args)
        return (post, 201, {
            'Location': url_for('resources.posts.post', id = post.id)
        })



class Post(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'content',
            required = True,
            help = 'No content provided',
            location = ['form', 'json']
        )

    @marshal_with(posts_fields)
    def get(self, id):
        return post_or_404(id)
    
    def put(self, id):
        return jsonify({'content': ''})

    @auth.login_required
    def delete(self, id):
        query = models.Post.delete().where(models.Post.id==id)
        query.execute()
        return ('', 204, {'Location': url_for('resources.posts.posts')})


#treat this file as another app or proxy
posts_api = Blueprint('resources.posts', __name__)
api = Api(posts_api)
api.add_resource(
    PostList,
    '/api/v1/posts',
    endpoint = 'posts'
)

api.add_resource(
    Post,
    '/api/v1/posts/<int:id>',
    endpoint = 'post'
)