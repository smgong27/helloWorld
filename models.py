from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
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
    teamSemesterStatus = db.Column(db.String(20), nullable=False, default='Upcoming', server_default='Upcoming')

    #Makes sure semester and team combinations are unique.
    __table_args__ = (
        UniqueConstraint(
            'teamName',
            'teamSemesterYear',
            name='unique_team_semester'
        ),
    )
class Expense(db.Model):
    __tablename__ = 'expense'

    expense_id = db.Column(db.Integer, primary_key=True)

    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    venmo = db.Column(db.String(100), nullable=False)

    expense_date = db.Column(db.Date, nullable=False)
    game = db.Column(db.String(100))

    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.Text, nullable=False)
    receipt_filename = db.Column(db.String(255), nullable=False)

    approval_status = db.Column(
        db.String(20), nullable=False, default='Pending'
    )

    repayment_status = db.Column(
        db.Boolean, nullable=False, default=False
    )

    treasurer_comment = db.Column(db.Text)

class Transaction(db.Model):
    __tablename__ = 'transaction'

    transaction_id = db.Column(db.String(20), primary_key=True)
    transaction_date = db.Column(db.Date, nullable=False)
    game_id = db.Column(db.String(20), nullable=True)
    account_id = db.Column(db.String(30), nullable=False)
    team_id = db.Column(db.String(30), nullable=False)
    description = db.Column(db.Text, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(100), nullable=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    receipt_filename = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='Active', nullable=False)

    def __repr__(self):
        return f"<Transaction {self.transaction_id}: {self.description} (${self.amount})>"