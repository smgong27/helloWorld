from main import app
from models import db, User, Transaction, Team
from sqlalchemy import inspect
from werkzeug.security import generate_password_hash
from datetime import datetime, date
from decimal import Decimal

with app.app_context():
    db.drop_all()
    db.create_all()

    inspector = inspect(db.engine)
    print("Created tables:", inspector.get_table_names())

    # Initial loading of users
    users = [
        {'username': 'member', 'email': 'member@umd.edu', 'first_name': 'Mandy', 'last_name': 'McDonald',
         'password': generate_password_hash('Member123456789', method='pbkdf2:sha256'), 'user_persona': 'MEMBER'},
        {'username': 'executive', 'email': 'executive@umd.edu', 'first_name': 'Ellen', 'last_name': 'Embrose',
         'password': generate_password_hash('Executive123456789', method='pbkdf2:sha256'), 'user_persona': 'EXECUTIVE'},
        {'username': 'treasurer', 'email': 'treasurer@umd.edu', 'first_name': 'Tara', 'last_name': 'Taylor',
         'password': generate_password_hash('Treasurer123456789', method='pbkdf2:sha256'), 'user_persona': 'TREASURER'},
        {'username': 'advisor', 'email': 'advisor@umd.edu', 'first_name': 'Arthur', 'last_name': 'Anderson',
         'password': generate_password_hash('Advisor123456789', method='pbkdf2:sha256'), 'user_persona': 'ADVISOR'}
    ]

    for each_user in users:
        print(f'{each_user["first_name"]} {each_user["last_name"]} inserted into User')
        a_user = User(
            username=each_user['username'],
            email=each_user['email'],
            first_name=each_user['first_name'],
            last_name=each_user['last_name'],
            password=each_user['password'],
            user_persona=each_user['user_persona']
        )
        db.session.add(a_user)
        db.session.commit()

    # Initial loading of ledger transactions
    transactions = [
        Transaction(
            transaction_id="E102601", transaction_date=datetime(2026, 10, 8), account_id="SGA",
            team_id="NCSA", transaction_type="Travel", amount=245.50, game_id="G201",
            description="Van rental gas for Delaware away double-header", receipt_filename=None),
        Transaction(
            transaction_id="R102601", transaction_date=datetime(2026, 10, 15), account_id="SECU",
            team_id="Active", transaction_type="Dues", amount=150.00, game_id=None,
            description="Fall player dues payment", receipt_filename=None),
        Transaction(
            transaction_id="R092602", transaction_date=date(2026, 9, 15), game_id="G201",
            account_id="RecWell", team_id="NCSA", description="Concessions revenue",
            transaction_type="Revenue", location="College Park, MD", amount=Decimal("800.00"),
            receipt_filename=None),
        Transaction(
            transaction_id="E092602", transaction_date=date(2026, 9, 2), game_id=None,
            account_id="SGA", team_id="Active", description="Team jerseys & gear",
            transaction_type="Expense", location="Baltimore, MD", amount=Decimal("680.00"),
            receipt_filename=None)
    ]

    for each_trans in transactions:
        print(f'Transaction {each_trans.transaction_id} inserted into Transaction')
        db.session.add(each_trans)
        db.session.commit()

    # Initial loading of team dues by semester

    teams = [
        Team(
            teamName='NCSA Team',
            teamSemesterYear='Fall 2026',
            teamDuesAmount=Decimal('100.00')
        ),
        Team(
            teamName='Active Team',
            teamSemesterYear='Fall 2026',
            teamDuesAmount=Decimal('100.00')
        ),
        Team(
            teamName='NCSA Team',
            teamSemesterYear='Spring 2027',
            teamDuesAmount=Decimal('100.00')
        ),
        Team(
            teamName='Active Team',
            teamSemesterYear='Spring 2027',
            teamDuesAmount=Decimal('100.00')
        ),
        Team(
            teamName='NCSA Team',
            teamSemesterYear='Fall 2027',
            teamDuesAmount=Decimal('100.00')
        ),
        Team(
            teamName='Active Team',
            teamSemesterYear='Fall 2027',
            teamDuesAmount=Decimal('100.00')
        )
    ]

    for each_team in teams:
        print(
            f'{each_team.teamName} - '
            f'{each_team.teamSemesterYear} inserted into Team'
        )
        db.session.add(each_team)

    db.session.commit()