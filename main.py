from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:pizza1229@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    textbody = db.Column(db.String(220))

    def __init__(self, title, textbody):
        self.title = title
        self.textbody = textbody

@app.route("/", methods=["GET", "POST"])
def index():
    return render_tempalte("index.html")

@app.route("/blog", methods["POST", "GET"])
def blog():
    id = request.args.get("id")
    focus = False
    if id:
        focus = Blog.query.filter_by(id = id)[0]

    blogs = Blog.query.all()
    return render_tempalte("blog.html", blogs=blogs, focus=focus)

@app.route("/new_post", methods=["GET", "POST"])
def new_post():
    if request.method == "POST":
        if request.form["title"] == "" or request.form["body"] == "":
            return redirect("/new_post?error=" + str(True))
        title = request.form["title"]
        textbody = request.form["textbody"]
        db.session.add(Blog(title,body))
        db.session.commit()
        id = db.engine.execute("SELECT MAX(id) from blog;").fetchone()[0]
        return redirect("/blog?id=" + str(id))
    return render_template("new_post.html", error=request.args.get('error'))

if __name__ == "__main__":
    app.run(debug=True)