from app import db
from datetime import datetime
import re
from flask_security import UserMixin, RoleMixin
from flask_wtf import FlaskForm
from wtforms import FileField

# Утилита для генерации безопасных имен файлов
from werkzeug.utils import secure_filename


# Функция для генерации безопасных имен файлов при загрузке
def prefix_name(obj, file_data):
    parts = os.path.splitext(file_data.filename)
    return secure_filename(f'file-{parts[0]}{parts[1]}')


# Функция для создания slug из строки
def slugify(s):
    pattern = r'[^\w+]'
    return re.sub(pattern, '-', s)


# Модель для загрузки файлов через форму
class MyForm(FlaskForm):
    upload = FileField('File')


# Таблица связи многие-ко-многим между постами и тегами
post_tags = db.Table('post_tags',
                     db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
                     db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                     )


# Таблица связи многие-ко-многим между статьями и тегами
articles_tags = db.Table('articles_tags',
                         db.Column('article_id', db.Integer, db.ForeignKey('article.id')),
                         db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
                         )


# Модель Post
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    slug = db.Column(db.String(140), unique=True)
    body = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.now())
    image = db.Column(db.String(120), nullable=True)  # Поле для хранения пути к изображению
    tags = db.relationship('Tag', secondary=post_tags, backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        self.generate_slug()

    # Метод для генерации slug из заголовка
    def generate_slug(self):
        if self.title:
            self.slug = slugify(self.title)

    def __repr__(self):
        return f'<Post id: {self.id}, title: {self.title}>'


# Модель Article
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    slug = db.Column(db.String(140), unique=True)
    body = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.now())
    tags = db.relationship('Tag', secondary=articles_tags, backref=db.backref('articles', lazy='dynamic'))

    def __init__(self, *args, **kwargs):
        super(Article, self).__init__(*args, **kwargs)
        self.generate_slug()

    def generate_slug(self):
        if self.title:
            self.slug = slugify(self.title)

    def __repr__(self):
        return f'<Article id: {self.id}, title: {self.title}>'


# Модель Tag
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    slug = db.Column(db.String(100))

    def __init__(self, *args, **kwargs):
        super(Tag, self).__init__(*args, **kwargs)
        self.slug = slugify(self.name)

    def __repr__(self):
        return f'{self.name}'


# Таблица связи многие-ко-многим между пользователями и ролями
roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
                       )


# Модель User с поддержкой Flask-Security
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))


# Модель Role с поддержкой Flask-Security
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(255))
