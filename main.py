from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

app.secret_key = 'quickredSECR3Tfox'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(220))
   
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        
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

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    email_err = ''
    password_err = ''
    verify_err = ''

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(email=email).first()

        if email != '':

            if '@' not in email or '.' not in email:
                email_err = "Invalid email"

        if password == '' or password == " " or len(password) < 3 or len(password) > 20 or ' ' in password:
            password_err = "Invalid password"

        if verify != password:
            verify_err = "Your passwords do not match"

        if existing_user:
            flash('User already exists', 'Error')

        if not existing_user and not email_err and not password_err and not verify_err:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email

            return redirect('/new_entry')

    return render_template('signup.html', title="Become a member of our Blog!", email_err=email_err, password_err=password_err, verify_err=verify_err)

@app.route('/blog', methods = ['POST', 'GET'])
def blog():
    if request.args.get("id"):
        blog_id = request.args.get('id')
        blog = Blog.query.get(blog_id)

        return render_template("view_entry.html", blog=blog)

    elif request.args.get("user"):
        user_id = request.args.get('user')
        user = User.query.get(user_id)
        posts = Blog.query.filter_by(owner=user).all()

        return render_template("singleUser.html", user=user, posts=posts)

    else:
        posts = Blog.query.all()

        return render_template('blog_home.html', title="Build Your Blog", posts=posts)

@app.route('/new_entry', methods=['GET', 'POST'])
def new_entry():
    if request.method == 'GET':

        return render_template('new_entry.html', title="Write a new blog entry")

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        owner = User.query.filter_by(email=session['email']).first()
        title_err = ''
        body_err = ''

        if len(title) < 1:
            title_err = "Your post needs a title."
        
        if len(body) < 1:
            body_err = "Type something here."

    if not title_err and not body_err:
        blog = Blog(title, body, owner)
        db.session.add(blog)
        db.session.commit()

        id = blog.id
        id_str = str(id)

        return redirect('/blog?id=' + id_str)

    else:
        return render_template("new_entry.html", title="Create a new blog entry", title_err=title_err, body_err=body_err)

@app.route('/logout')
def logout():
    del session['email']
    flash("You are logged out")
    
    return redirect('/blog')


if __name__ == "__main__":
    app.run(debug=True)