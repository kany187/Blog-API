import datetime

from argon2 import PasswordHasher
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                            BadSignature, SignatureExpired)
from peewee import *

import config

# set a database using Python and Peewee

DATABASE = SqliteDatabase('blog.db')
HASHER = PasswordHasher()


class Post(Model):
    id = CharField(unique=True)
    title = CharField()
    content = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DATABASE

class User(Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField()
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE

    @classmethod
    def create_user(cls, username, email, password, **kwargs):
        email = email.lower()
        try:
            cls.select().where(
                (cls.email == email) | (cls.username ** username)
            ).get()
        except cls.DoesNotExist:
            user = cls(username = username, email = email)
            user.password = user.set_password(password)
            user.save()
            return user
        else:
            raise Exception('user with that email or username already exist')

    @staticmethod
    def verify_auth_token(token):
        serializer = Serializer(config.SECRET_KEY)
        try:
            data = serializer.loads(token)
        except (SignatureExpired, BadSignature):
            return None
        else:
            user = User.get(User.id == data['id'])
            return user

    @staticmethod
    def set_password(password):
        return HASHER.hash(password)

    def verify_password(self, password):
        return HASHER.verify(self.password, password)

    #expire in one hour
    def generate_auth_token(self, expires=3600):
        serializer = Serializer(config.SECRET_KEY, expires_in=expires)
        return serializer.dumps({'id':self.id})

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User,Post])
    DATABASE.close()


