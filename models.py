from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

class Group(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, nullable=False)
    name = db.Column(db.VARCHAR(55), nullable=False)
    admin_id = db.Column(db.INTEGER)
    users = db.relationship('User', backref='proj_group', lazy='dynamic')


class User(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, nullable=False)
    f_name = db.Column(db.String(25))
    l_name = db.Column(db.String(25))
    username = db.Column(db.VARCHAR(50))
    email = db.Column(db.VARCHAR(50))
    password = db.Column(db.VARCHAR(50))
    group_id = db.Column(db.INTEGER, db.ForeignKey('group.id'))