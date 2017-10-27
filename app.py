from flask import Flask, render_template, request, redirect, jsonify, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# this connects flask to connect to the database
app.config.from_pyfile('config.cfg')

# make a database object and register it to the application
db = SQLAlchemy(app)
# create a new table to handle group subscriptions

subs = db.Table('subs',
                db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
                )


class User(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, nullable=False)
    f_name = db.Column(db.String(25))
    l_name = db.Column(db.String(25))
    username = db.Column(db.VARCHAR(50))
    email = db.Column(db.VARCHAR(50))
    password = db.Column(db.VARCHAR(50))

    subscriptions = db.relationship('Group',
                                    secondary=subs,
                                    backref=db.backref('subscribers'),
                                    lazy='dynamic')


class Group(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, nullable=False)
    name = db.Column(db.VARCHAR(55), nullable=False)
    admin_id = db.Column(db.INTEGER)

    # creating a second multi-relationship so two way queries can be ran
    g_users = db.relationship('User',
                              secondary=subs,
                              backref=db.backref('members'),
                              lazy='dynamic')


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/signup/')
def signup():
    return render_template("signup.html")


@app.route('/process_signup/', methods=['POST'])
def process_signup():
    if request.method == 'POST':
        print ("method equal to post")
        form_data = request.form
        fn = form_data['input_fname']
        ln = form_data['input_lname']
        un = form_data['input_uname']
        em = form_data['input_email']
        passw = form_data['input_password']

        # create a new user
        # group id of zero means they don't yet have a group
        new_user = User(f_name=fn,
                        l_name=ln ,
                        username=un,
                        email=em,
                        password=passw)

        # get the orphan group
        orphanGroup = Group.query.filter_by(id=0).first()
        # append the subscriber to the orphan group initially
        orphanGroup.subscribers.append(new_user)


        db.session.add(new_user)
        db.session.commit()

        return redirect("/login/")


@app.route('/group/<int:group_id>')
def show_group(group_id):
    group = Group.query.filter_by(id=group_id).first()
    users = User.query.filter_by(group_id=1)
    return render_template("group.html", group=group, users=users)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("method is post, process the form. ")
        form_data = request.form
        uname = form_data['input_uname']
        passw = form_data['input_password']
        # print ("Username {}\n".format(uname))
        # print ("Password {}".format(passw))
        # select the user where the username and password are in the db
        user = User.query.filter_by(username=uname, password=passw).first()
        # if the user query is not none, meaning it exists..
        if user is not None:
           # print("First name from db : {}".format(user.f_name))
           # print("Last name from db : {}".format(user.l_name))
           # print("Username from db : {}".format(user.username))
           # print("email from db : {}".format(user.email))
           # print("group id from db : {}".format(user.group_id))
           session['username'] = uname
           return redirect("/dashboard/")
        else:
            return render_template('login.html', sucessval="FALSE")
    else:
        return render_template('login.html')


@app.route('/dashboard/')
def dashboard():
    if 'username' in session:
        user = session['username']
        print("user from session: {}".format(user))
        # get the group that they're in
        # first get the user
        user_obj = User.query.filter_by(username=user).first()
        print("Username from db query : {}".format(user_obj.f_name))
        # now find the group based on the association
        # groups = user_obj.subscriptions()
        groups = user_obj.members

        hasGroup = "TRUE";
        for group in groups:
            if group.id == 0:
                hasGroup = "False"

    else:
        user = "NOT_SET"
    return render_template('dashboard.html', user=user_obj, hasgroup=hasGroup)


if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(debug=True)
