from flask import Flask, render_template, flash, session, request, make_response, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms.fields import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(16)
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///let_me_note.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    password = db.Column(db.Integer, nullable=False)
    tasks = db.relationship('Tasks', backref="users", lazy=True)

    def __repre__(self):
        return '<Name %r>' % self.user_id

class Tasks(db.Model):
    task_id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    def __repre__(self):
        return '<Status %r>' % self.tasks_id

class Form(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Start!")

class TaskForm(FlaskForm):
    description = StringField("Description", validators=[DataRequired()])
    submit = SubmitField("Add")

@app.route("/", methods=["GET", "POST"])
def index():

    title = "Login"
    login_form = Form()

    context = {
        "title": title,
        "login_form": login_form
    }

    if login_form.validate_on_submit():
        username = login_form.username.data
        password = login_form.password.data
        user_db = Users.query.filter_by(username=username).first()

        if user_db is not None:
            if check_password_hash(user_db.password, password):
                session["user_id"] = user_db.user_id
                session["name"] = user_db.name
                return redirect(url_for("notes"))
            else: 
                flash("Wrong Username or Password", "danger")
        else:
            flash("Wrong Username or Password", "danger")

    return render_template("login.html", **context)


@app.route("/notes/", defaults={"task_id":0, "task_status":0}, methods=["GET", "POST"])
@app.route("/notes/<task_id>/<task_status>", methods=["GET", "POST"])
def notes(task_id, task_status):
    title = "My Notes"
    task_form = TaskForm()
    user_id = session.get("user_id")
    name = session.get("name")
    tasks = Tasks.query.filter_by(user_id=user_id).all()

    context = {
        "title": title,
        "name": name, 
        "tasks": tasks,
        "task_form": task_form
    }

    if request.method == "POST":
        print(task_status)
        if task_form.validate_on_submit(): #ADD A TASK
            desp = task_form.description.data
            new_task = Tasks(description=desp, status="2", user_id=user_id)
            print(new_task.description)
            try:
                db.session.add(new_task)
                db.session.commit()
                flash("Task added!", "success")

                return redirect(url_for("notes"))
            except:
                flash("Something was wrong. Please try again!", "danger")
                return redirect(url_for("notes"))
        elif int(task_status) == 0: #DELETE A TASK  
            task_del = Tasks.query.filter_by(task_id=task_id).first()
            try:
                db.session.delete(task_del)
                db.session.commit()
                flash("A task was deleted!", "success")

                return redirect(url_for("notes"))
            except:
                flash("Something was wrong. Please try again!", "danger")
                return redirect(url_for("notes"))
        else:  #STATUS CHANGE OF A TASK
            new_task_status = Tasks.query.filter_by(task_id=task_id).first()
            if new_task_status.status == 2:
                new_task_status.status = 1
                try:
                    db.session.commit()
                    flash("Status changed", "success")

                    return redirect(url_for("notes"))
                except:
                    flash("Something was wrong. Please try again!", "danger")
                    return redirect(url_for("notes"))
            else:
                new_task_status.status = 2
                try:
                    db.session.commit()
                    flash("Status changed", "success")

                    return redirect(url_for("notes"))
                except:
                    flash("Something was wrong. Please try again!", "danger")
                    return redirect(url_for("notes"))     
            
    return render_template("notes.html", **context)


if __name__ == "__main__":
    app.run()