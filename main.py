from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:pizza1229@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'Bear11TkFox9WtNeRdS225'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(220))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, date, owner):
        self.title = title
        self.body = body
        self.date = date
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def get_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/')
def index():
    users = User.query.all()

    return render_template('index.html', title="Blog Members", users=users)


@app.route('/blog', methods = ['POST', 'GET'])
def blog_list():
    owner = User.query.filter_by(email=session['email']).first()

    if request.args.get("id"):
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)
        blog_date = request.args.get('date')
        return render_template("view_entry.html", blog=blog, blog_date=blog_date)

    elif request.args.get("user"):
        user_id = request.args.get('user')
        user = User.query.get(user_id)
        posts = Blog.query.filter_by(owner=user).order_by(Blog.date.desc()).all()
        return render_template("singleUser.html", user=user, posts=posts)

    else:
        posts = Blog.query.order_by(Blog.date.desc()).all()
        return render_template('blog_home.html', title="Build Your Blog", posts=posts, owner=owner)

@app.route('/new_entry', methods=['GET', 'POST'])
def new_entry():
    if request.method == 'GET':
        return render_template('new_entry.html', title="Write a new blog entry")

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        date = request.args.get('date')
        owner = User.query.filter_by(email=session['email']).first()
        title_err = ''
        body_err = ''

        if len(title) < 1:
            title_err = "You forgot a title."
        
        if len(body) < 1:
            body_err = "Add some post content."

        if not title_err and not body_err:
            new_post = Blog(title, body, date, owner)
            db.session.add(new_entry)
            db.session.commit()
            blog_url = "/blog?id=" + str(new_entry.id)
            return redirect(blog_url)

        return render_template("new_entry.html", title="Create a new blog entry", title_err=title_err, body_err=body_err)


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    email_err = ''
    password_err = ''
    verify_err = ''

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        if email != '':
            if '@' not in email or '.' not in email:
                email_err = "Invalid email"

        if password == '' or password == " " or len(password) < 3 or len(password) > 20 or ' ' in password:
            password_err = "Invalid password"

        if verify != password:
            verify_err = "Your passwords do not match"

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash('User already exists', 'Error')

        if not existing_user and not email_err and not password_err and not verify_err:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/new_entry')

    return render_template('signup.html', title="Become a member of our Blog!", email_err=email_err, password_err=password_err, verify_err=verify_err)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Login successful")
            print(session)
            return redirect('/new_entry')
        else:
            flash('Password incorrect or user does not exist', 'Error')

    return render_template('login.html', title="Log in to contribute.")


@app.route('/logout')
def logout():
    del session['email']
    flash("You are logged out")
    return redirect('/blog')


if __name__ == "__main__":
    app.run(debug=True)