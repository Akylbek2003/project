from flask import Flask, redirect, url_for, request, flash 
from config import Configuration 
from flask_sqlalchemy import SQLAlchemy  # Импорт SQLAlchemy для работы с базой данных
from flask_migrate import Migrate  # Импорт Migrate для работы с миграциями

from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView 
from flask_admin.form import ImageUploadField
from werkzeug.utils import secure_filename
from uuid import uuid4
import os

from flask_security import SQLAlchemyUserDatastore
from flask_security import Security
from flask_security import current_user

from markupsafe import Markup #Использование Markup из MarkupSafe помогает пометить строки как безопасные для вывода.

from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()


# Инициализация приложения Flask
app = Flask(__name__)
app.config.from_object(Configuration)  # Загрузка конфигурации из файла config.py

# Инициализация базы данных SQLAlchemy и миграций
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Путь для сохранения изображений
file_path = os.path.normpath(os.path.join(os.path.dirname(__file__), 'static/uploads/'))
app.config['UPLOAD_FOLDER'] = os.path.normpath(os.path.join(os.getcwd(), 'static/uploads/'))


# Генерация уникальных имен файлов
def namegen(obj, file_data):
    ext = file_data.filename.split('.')[-1]
    return secure_filename(f"{uuid4()}.{ext}")

# Импорт моделей базы данных
from models import Post, Article, Tag, User, Role, post_tags, articles_tags, roles_users


class AdminMixin:
    def is_accessible(self):
        return 1
    
    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('security.login', next=request.url ))

class BaseModelView(ModelView):
    def on_model_change(self, form, model, is_created):
        model.generate_slug()
        return super(BaseModelView, self).on_model_change(form, model, is_created)

class AdminView(ModelView):
    pass

class HomeAdminView(AdminIndexView):
    pass

class PostAdminView(AdminMixin, BaseModelView):
    form_columns = ['title', 'body', 'tags', 'image']

    form_extra_fields = {
        'image': ImageUploadField('Image',
                                  base_path='static/',  
                                  relative_path='uploads/', 
                                  thumbnail_size=(100, 100, True), 
                                  namegen=namegen,
                                  allowed_extensions=['jpg', 'jpeg', 'png', 'gif'])
    }

    # Отображение миниатюры в списке постов
    def _list_thumbnail(view, context, model, name):
        if not model.image:
            return ''
        # Убедитесь, что здесь правильно используется каталог 'uploads'
        url = url_for('static', filename=f'{model.image}')
        return Markup(f'<img src="{url}" width="200">')

    column_formatters = {
        'image': _list_thumbnail
    }

    form_overrides = {
        'image': ImageUploadField
    }



class TagAdminView(AdminMixin, BaseModelView):
    form_columns = ['name', 'posts']


admin = Admin(app, 'FlaskApp', url='/', index_view=HomeAdminView(name='Home'))
admin.add_view(PostAdminView(Post, db.session))
admin.add_view(AdminView(Tag, db.session))
admin.add_view(AdminView(Article, db.session))

### Flask-security ###
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)
