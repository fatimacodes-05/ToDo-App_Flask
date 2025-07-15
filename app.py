from flask import Flask,render_template,request,redirect,session,flash,url_for
from models import db, User, Todo
from flask_sqlalchemy import SQLAlchemy
#from datetime import datetime

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///todo.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= False
app.secret_key = "supersecretkey"
db.init_app(app)

#db=SQLAlchemy(app)

# class Todo(db.Model):
#     sno=db.Column(db.Integer,primary_key=True)
#     title=db.Column(db.String(200),nullable=False)
#     desc=db.Column(db.String(200),nullable=False)
#     date_created=db.Column(db.DateTime,default=datetime.utcnow)

#     def __repr__(self) -> str:
#         return f"{self.sno} - {self.title}"


@app.route("/", methods=["GET", "POST"])
def hello_world():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        desc = request.form["desc"]
        todo = Todo(title=title, desc=desc, user_id=session["user_id"])
        db.session.add(todo)
        db.session.commit()
        return redirect("/")  

    
    search_query = request.args.get("q", "")

   
    page = request.args.get("page", 1, type=int)
    per_page = 5

    
    query = Todo.query.filter_by(user_id=session["user_id"])
    if search_query:
        query = query.filter(
            Todo.title.ilike(f"%{search_query}%") | Todo.desc.ilike(f"%{search_query}%")
        )

    pagination = query.order_by(Todo.date_created.desc()).paginate(page=page, per_page=per_page)
    todos = pagination.items

    return render_template("index.html", allTodo=todos, pagination=pagination, search_query=search_query)


@app.route("/show")
def products():
    allTodo= Todo.query.all()
    print(allTodo)
    return "<p>This is the products page!</p>"

@app.route("/update/<int:sno>", methods=["GET", "POST"])
def update(sno):
    todo = Todo.query.filter_by(sno=sno).first()

    if todo.user_id != session["user_id"]:
        flash("Unauthorized access")
        return redirect("/")

    if request.method == "POST":
        todo.title = request.form['title']
        todo.desc = request.form['desc']
        db.session.commit()
        return redirect("/")

    return render_template('update.html', todo=todo)
  

@app.route("/delete/<int:sno>")
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first()

    if todo.user_id != session["user_id"]:
        flash("Unauthorized access")
        return redirect("/")

    db.session.delete(todo)
    db.session.commit()
    return redirect('/')

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        # Check if email exists
        if User.query.filter_by(email=email).first():
            flash("Email already exists!")
            return redirect("/register")

        user = User(username=username, email=email)
        user.set_password(password)  # 🔐 Hash password
        db.session.add(user)
        db.session.commit()

        flash("Registered successfully. Please log in.")
        return redirect("/login")

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Login successful!")
            return redirect("/")

        flash("Invalid credentials!")
        return redirect("/login")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully")
    return redirect("/login")



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=8000)

