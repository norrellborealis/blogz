from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:pizza1229@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'ToUcEt101031'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(220))

    def __init__(self, title, body):
        self.title = title
        self.body = body

blogs = Blog.query.all()

def is_empty(n):
    if n == "":
        return True

@app.route('/')
def index():
    return redirect('blog')

@app.route('/blog', methods = ['POST', 'GET'])
def blog():
    blog_id=request.args.get('id')
    blog = Blog.query.filter_by(id = blog_id).first()

    if request.args:
        return render_template('view_entry.html', title=blog.title, body=blog.body)

    blogs = Blog.query.all()
    return render_template('blog_home.html', title="New Entry", blogs=blogs)

@app.route('/new_entry')
def new_entry():
    return render_template('new_entry.html')

@app.route('/new_entry', methods = ['POST'])
def new_post():
    title = request.form['title']
    title_error = ''

    body = request.form['body']
    body_error = ''

    if is_empty(title):
        title_error = 'You must choose a title'

    if is_empty(body):
        body_error = 'Your post needs some content!'

        return render_template('new_entry.html', title = "New Entry", title_error=title_error, body_error=body_error)

    else:
        new_blog = Blog(title, body)
        db.session.add(new_blog)
        db.session.commit()

    return redirect('/blog?id='+str(new_blog.id))


if __name__ == "__main__":
    app.run(debug=True)