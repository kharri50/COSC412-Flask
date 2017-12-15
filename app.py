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
    Tasks = db.relationship('Task',
                            backref=db.backref('Tasks'),
                            lazy='dynamic')

    # backref for the user image. Makes it easier to query, but
    # it's certainly not necessary
    image = db.relationship("UserImage", backref=db.backref('UserImage'), lazy='dynamic')


class Group(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, nullable=False)
    name = db.Column(db.VARCHAR(55), nullable=False)
    description = db.Column(db.TEXT, nullable=True)
    admin_id = db.Column(db.INTEGER)

    # creating a second multi-relationship so two way queries can be ran
    g_users = db.relationship('User',
                              secondary=subs,
                              backref=db.backref('members'),
                              lazy='dynamic')

    project_id = db.Column(db.INTEGER, nullable=False)

    # project_id = db.Column(db.INTEGER, db.ForeignKey('project.id'))
    project = db.relationship("Project", backref=db.backref('Project'), lazy='dynamic')

    posts = db.relationship('Post',
                        backref=db.backref('post'),
                        lazy='dynamic')


# the following is a definition for a project, which belongs to a group.
# technically, this mirrors the structure of the group, but it's not an atomic.
class Project(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, nullable=False)
    name = db.Column(db.VARCHAR(55), nullable=False)
    description = db.Column(db.TEXT, nullable=True)
    admin_id = db.Column(db.INTEGER)
    # the following makes a lazy backref to the tasks

    tasks = db.relationship('Task',
                            backref=db.backref('project'),
                            lazy='dynamic')
    group_id = db.Column(db.INTEGER, db.ForeignKey('group.id'))


# the following is the definition for the tasks which are in a project.
# it's a one to many model. There will be many tasks per one group.
#
# Each task must have the following:
#   task_id
#   project_id BACKREF
#   user_id    BACKREF
#   name
#   description
#   time estimate
#   status (ENUM STRING)
#   file(not needed for prototype implementation) SKIP
#   revisions (not needed for prototype implementation) SKIP


class Task(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, nullable=False)
    name = db.Column(db.VARCHAR(255), nullable=False)
    description = db.Column(db.TEXT, nullable=True)
    time_estimate = db.Column(db.FLOAT, nullable=False)
    status = db.Column(db.VARCHAR(25), nullable=False)
    project_id = db.Column(db.INTEGER, db.ForeignKey('project.id'))
    user_id = db.Column(db.INTEGER, db.ForeignKey('user.id'))
    # backref to get the user assigned to the task
    user = db.relationship("User", backref=db.backref('User', lazy='dynamic'))


# add the model for user images here
class UserImage(db.Model):
    imgId = db.Column(db.INTEGER, primary_key=True, nullable=False)
    uid = db.Column(db.INTEGER, db.ForeignKey('user.id'))
    imagePath = db.Column(db.VARCHAR(255), nullable=False)
    # you can add a back ref here in the user table for the image

# creating a model to contain group posts..
class Post(db.Model):
    post_id = db.Column(db.INTEGER, primary_key=True, nullable=False)
    user_id = db.Column(db.INTEGER, db.ForeignKey('user.id'))
    text = db.Column(db.TEXT, nullable=False)
    posted_date = db.Column(db.VARCHAR(25), nullable=False)
    posted_time = db.Column(db.FLOAT, nullable=False)

    # db backref in the common situation that we're lazy
    puser = db.relationship("User", backref=db.backref('puser', lazy='dynamic'))
    group_id = db.Column(db.INTEGER, db.ForeignKey('group.id'))





@app.route('/')
def index():
    return render_template("index.html")


@app.route('/user_profile/')
def user_profile():
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
        has_group = "TRUE"
        numGroups = 0
        for group in groups:
            numGroups += 1
        if numGroups == 0:
            has_group = "FALSE"
    else:
        user = "NOT_SET"
    return render_template("user_profile.html", user=user_obj)


@app.route('/signup/')
def signup():
    return render_template("signup.html")


# test code to show task block
@app.route('/task_view/')
def taskblock():
    return render_template("task_block.html")


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
                        l_name=ln,
                        username=un,
                        email=em,
                        password=passw)

        # get the orphan group
        orphan_group = Group.query.filter_by(name='orphan group').first()
        # append the subscriber to the orphan group initially
        orphan_group.subscribers.append(new_user)

        db.session.add(new_user)
        db.session.commit()

        return redirect("/login/")


@app.route('/process_create_group/', methods=['POST'])
def process_create_group():
    if request.method == "POST":
        print ("method equal to post")
        form_data = request.form
        group_name = form_data['input_groupname']
        desc = form_data['input_desc']
        admin_username = form_data['input_admin_un']
        print("Group name : {} ".format(group_name))
        print("Group description: {} ".format(desc))
        print("Group admin: {}".format(admin_username))
        # get the admin id from the inputted username
        admin = User.query.filter_by(username=admin_username).first()
        if admin is not None:
            admin_id = admin.id
            print("Admin name from query : {}".format(admin.f_name))
            g = Group(name=group_name, description=desc, admin_id=admin_id, project_id=-1)
            db.session.add(g)
            db.session.commit()
            return redirect('/edit_group/{}'.format(g.id))
        else:
            return """"<script type="text/javascript"> alert("Invalid admin username ");\
            window.location.href='/create_group/'; </script>"""
    else:
        return redirect('/create_group/')


@app.route('/edit_group/<int:group_id>')
def edit_group(group_id):
    # get the currently logged in user from the session
    current_user = session['username']
    # get the group object from the group id
    group = Group.query.filter_by(id=group_id).first()
    print("Group name from query : {}".format(group.name))
    if group is not None:
        # get the admin from the group admin_id
        print("Group admin id : {}".format(group.admin_id))
        user = User.query.filter_by(id=group.admin_id).first()
        # check if the user.username is equal to the currently logged in user
        print("Username from query : {}".format(user.username))
        admin = User.query.filter_by(id=group.admin_id).first()
        user = User.query.filter_by(username=current_user).first()
        isAdmin = admin.id = user.id
        if current_user == user.username:
            isAdmin = True
        return render_template('edit_group.html', group=group, isAdmin=isAdmin)


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

        has_group = "TRUE"
        numGroups = 0
        for group in groups:
            numGroups += 1
        if numGroups == 0:
            has_group = "FALSE"

    else:
        user = "NOT_SET"
    return render_template('dashboard.html', user=user_obj, hasgroup=has_group)


@app.route('/process_group_edit/<int:action>', methods=['POST'])
def process_group_edit(action):
    # print("Data from AJAX/FLASK: {}".format(request.form['user_name']))
    # print("DATA FROM AJAX GROUP ID: {}".format(request.form['group_num']))

    # get the user that we have from the id
    user = User.query.filter_by(username=request.form['user_name']).first()
    if user is not None:
        # add a user to the group
        if action == 1:
            # theres no model to use, so we have to run raw sql
            query = "INSERT INTO subs VALUES({},{});".format(user.id, request.form['group_num'])
            # now get all of the user data and specifiy it to be returned in jsonify obj
            db.engine.execute(query)
            return jsonify(
                {'f_name': user.f_name, 'l_name': user.l_name, 'user_name': user.username, 'email': user.email}
            )
        elif action == 2:
            query = "DELETE FROM subs WHERE user_id = {} AND group_id = {};".format(user.id, request.form['group_num'])
        db.engine.execute(query)
        return jsonify({'success': 'operation sucessful.'})

    else:
        return jsonify({'error': 'unspecified exception'})


@app.route('/group_edit_desc/', methods=['POST'])
def edit_group_desc():
    group_desc = request.form['group_desc']
    group_id = request.form['group_id']
    print("group desc from post data : {}".format(group_desc))
    print("group id from post data : {}".format(group_id))
    # run the raw sql
    sql = "UPDATE  `group` SET description = '{}' WHERE id = {};".format(group_desc, group_id)
    db.engine.execute(sql)
    return jsonify({'sucess': 'operation sucessful'})


@app.route('/create_group/')
def create_group():
    return render_template('create_group.html', username=session['username'])


@app.route('/group_detail/<int:g_id>')
def group_detail(g_id):
    # check if the current user is the admin of the group for the detail page
    is_admin = False
    user = session['username']
    # print("username from detail url : {}".format(user))
    # get the username from the group admin
    group_obj = Group.query.filter_by(id=g_id).first()
    user_obj = User.query.filter_by(username=user).first()
    if group_obj.admin_id == user_obj.id:
        is_admin = True

    print("Group name from group detail : {}".format(group_obj.name))
    # now I'm going to get the project *if there is one, and then pass it with the url *
    project_obj = Project.query.filter_by(group_id=group_obj.id).first()
    # just need this line so the world doesn't end
    adminObj = User.query.filter_by(id=group_obj.admin_id).first()

    return render_template("group_detail.html", group=group_obj, admin_status=is_admin, project=project_obj, admin = adminObj)


@app.route('/process_project_create/', methods=['POST'])
def create_project():
    group_name = request.form['gn']
    project_name = request.form['project_name']
    project_desc = request.form['project_desc']
    admin = request.form['admin_id']

    print("GROUP NAME FROM PROCESS : {}".format(group_name))
    group = Group.query.filter_by(name=group_name).first()

    # print("Group ID from python : {}" .format(group.id)) # this causes issues BIG ISSUES
    # print("Group name from python: {}".format(group_name)) # this is not right
    print("Project name from python: {}".format(project_name))
    print("Project desc from python: {}".format(project_desc))
    print("ADMIN ID from python: {}".format(admin))

    groupObj  = Group.query.filter_by(name=group_name).first()

    proj = Project(name=project_name, description=project_desc, admin_id=admin, group_id=groupObj.id)
    db.session.add(proj)
    db.session.commit()

    # make a new query that will update the group id with the project id
    # get the project id that was just created
    project_obj = Project.query.filter_by(group_id = group.id).first()

    updateQuery = "update `group` set project_id = {} WHERE id  = {};".format(project_obj.id, groupObj.id)

    db.engine.execute(updateQuery)

    # return where you think its appropriate
    return redirect('group_detail/{}'.format(groupObj.id))


@app.route('/process_task_create/', methods=['POST'])
def create_task():
    task_name = request.form['task_name']
    task_description = request.form['task_desc']
    assigned_member = request.form['member']
    print("Assigned mem from py : {}".format(assigned_member))
    time_est = request.form['time_est']
    project_id = request.form['fuck_2']

    group_id = request.form['gid']
    names = assigned_member.split()

    print("first name from python :{}space".format(names[0]))
    print("last name from python :{}space".format(names[1]))

    userObj = User.query.filter_by(f_name=names[0],l_name=names[1]).first()

    print("PRINTING FROM USER OBJ : {}".format(userObj.f_name))

    print("task ID from python : {}".format(task_name))
    print("Task DESC from py : {}".format(task_description))
    print("Assigned mem from py : {}".format(assigned_member))

#      initially the status will be "TO DO"
#      create a new task obj

    tsk = Task(name=task_name,
                description = task_description,
                time_estimate=time_est,
                status="TODO",
                project_id=project_id,
                user_id=userObj.id)

    db.session.add(tsk)
    db.session.commit()

    return redirect('group_detail/{}'.format(group_id))


@app.route('/process_task_edit/', methods=['POST'])
def editTask():
    group_id = request.form['group_id']
    task_id = request.form['task_id']
    task_name = request.form['edit_task_name']
    task_desc = request.form['edit_task_desc']
    time_est = request.form['edit_time_est']

    # need to get name of person to change id
    assigned_member = request.form['selected_member']
    print("Assigned member : {}".format(assigned_member))
    names = assigned_member.split()
    userObj = User.query.filter_by(f_name=names[0],l_name=names[1]).first()
    status = request.form["selected_status"]
    print("Status from python : {}".format(status))
    print ("Task id from edit : {}".format(task_id))

    # now run an update query
    sql = "UPDATE task SET name = '{}'," \
           " description = '{}' ," \
           " time_estimate = {} , " \
           "status='{}', " \
           "user_id={}" \
           " WHERE id = {};".format(task_name, task_desc, time_est,status,userObj.id, task_id)

    # the query is correct, now run it
    db.engine.execute(sql)

    # now that it's done, redirect them to the same page they were just on
    return redirect('group_detail/{}'.format(group_id))
    print("SQL Query from python : {}".format(sql))


@app.route('/group_feed/<int:gro_id>')
def group_feed(gro_id):
    group_obj = Group.query.filter_by(id=gro_id).first()


@app.route('/project_create/<int:gro_id>')
def project_create(gro_id):
    group_obj = Group.query.filter_by(id=gro_id).first()
    adminObj = User.query.filter_by(id=group_obj.admin_id).first()
    return render_template('create_project.html', admin=adminObj)

if __name__ == '__main__':
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(debug=True)
