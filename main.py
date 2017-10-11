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

    def __init__(self, title, textbody):
        self.title = title
        self.body = body

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        title = request.form['title']
        blog = request.form['blog']
        if not title or not blog:
            flash('Invalid title or entry', 'error')
            return render_template('new_post.html')

        else:
            new_entry = Blog(title,blog)
            db.session.add(new_entry)
            db.session.commit()
            return render_template('view_entry.html', title=title, body=blog)
    
    blogs = Blog.query.all()

    return render_template('blog_home.html', blogs=blogs)

@app.route('/blog')
def blog():
    id=request.args.get('id')
    blog = Blog.query.get(id)
    title = blog.title
    body = blog.body

    return render_template('view_entry.html', title=title, body=body)

@app.route('/new_entry', methods=['GET', 'POST'])
def new_entry():
    return render_template('new_entry.html')


if __name__ == "__main__":
    app.run(debug=True)