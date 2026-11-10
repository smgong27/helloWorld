from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    years_of_experience = db.Column(db.Integer)
    expected_graduation_date = db.Column(db.Date)
    active_status = db.Column(db.Boolean)
    dues_paid_status = db.Column(db.Boolean)
    user_persona = db.Column(db.String(30))

class Game(db.Model):
    __tablename__ = 'game'

    game_id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.String(20), nullable=False)
    opponent = db.Column(db.String(100), nullable=False)
    game_date = db.Column(db.Date, nullable=False)
    game_times = db.Column(db.String(100), nullable=False)
    game_location = db.Column(db.String(20), nullable=False)

class Team(db.Model):
    __tablename__ = 'Team'

    teamID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    teamName = db.Column(db.String(100), nullable=False)
    teamSemesterYear = db.Column(db.String(50), nullable=False)
    teamDuesAmount = db.Column(db.Numeric(10, 2), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            'teamName',
            'teamSemesterYear',
            name='unique_team_semester'
        ),
    )

