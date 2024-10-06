from flask import Blueprint, render_template, request, redirect, url_for, current_app
from werkzeug.utils import secure_filename  # Для работы с безопасным именем файла
import os  # Для работы с файловой системой
from flask_security import login_required  # Защита маршрута
from models import Post, Tag
from app import db
from .forms import PostForm
import uuid


# Определяем Blueprint для маршрутов постов
posts = Blueprint('posts', __name__, template_folder='templates')
ALLOWED_EXTENSIONS={'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@posts.route('/create', methods=['POST', 'GET'])
@login_required
def create_post():
    if request.method == 'POST':
        title = request.form['title']  # Получаем заголовок поста из формы
        body = request.form['body']  # Получаем содержимое поста из формы

        # Проверка наличия файла в запросе
        if 'file' not in request.files:
            return 'No file part'

        file = request.files['file']  # Получаем файл из формы

        # Если файл есть и он разрешенного типа
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)  # Защищаем имя файла
            
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))  # Сохраняем файл
            # Генерируем относительный путь к изображению с правильным слэшем
            image_url = f'uploads/{filename}'  # Используем прямой слэш
            # Создаем пост с изображением
            post = Post(title=title, body=body, image=image_url)
        else:
            # Если файла нет или тип не разрешен, создаем пост без изображения
            post = Post(title=title, body=body)

        try:
            db.session.add(post)  # Добавляем пост в сессию базы данных
            db.session.commit()  # Подтверждаем изменения
        except Exception as e:
            print(f'Something went wrong: {e}')  # Логируем ошибку в консоль
            return 'Error while creating post'

        return redirect(url_for('posts.index'))  # Перенаправляем на главную страницу после создания поста

    form = PostForm()  # Форма для создания поста
    return render_template('posts/create_post.html', form=form)



@posts.route('/<slug>/edit/', methods=['POST', 'GET'])
@login_required
def edit_post(slug):
    post = Post.query.filter(Post.slug==slug).first_or_404()

    if request.method == 'POST':
        form = PostForm(formdata=request.form, obj=post)
        form.populate_obj(post)

        # Проверка наличия файла в запросе
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                # Генерация уникального имени файла с использованием UUID
                filename = f"{uuid.uuid4()}.{file.filename.rsplit('.', 1)[1].lower()}"
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Удаление старого изображения
                if post.image:
                    old_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], post.image)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)

                # Обновляем запись в базе данных новым изображением
                post.image = filename

        db.session.commit()
        return redirect(url_for('posts.post_detail', slug=post.slug))

    form = PostForm(obj=post)
    return render_template('posts/edit_post.html', post=post, form=form)


@posts.route('/')
def index():
    q = request.args.get('q')
    page = request.args.get('page')
    if page and page.isdigit():
        page = int(page)
    else:
        page = 1
    if q:
        posts = Post.query.filter(Post.title.contains(q) | Post.body.contains(q)) #.all()
    else:
        posts = Post.query.order_by(Post.created.desc())
    pages = posts.paginate(page=page, per_page=5)
    return render_template('posts/index.html', pages=pages)


# http://localhost/blog/first-post
@posts.route('/<slug>')
def post_detail(slug):
    post = Post.query.filter(Post.slug==slug).first_or_404()
    tags = post.tags
    return render_template('posts/post_detail.html', post=post, tags=tags)


# http://localhost/blog/blog/python
@posts.route('/tag/<slug>')
def tag_detail(slug):
    tag = Tag.query.filter(Tag.slug==slug).first_or_404()
    posts = tag.posts.all()
    return render_template('posts/tag_detail.html', tag=tag, posts=posts)

