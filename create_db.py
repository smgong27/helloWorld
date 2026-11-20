from main import app
from models import db, User, Transaction, Team, BankAccount
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
            username=each_user['username'],  # <-- This line was missing!
            email=each_user['email'],
            first_name=each_user['first_name'],
            last_name=each_user['last_name'],
            password=each_user['password'],
            user_persona=each_user['user_persona']
        )
        db.session.add(a_user)
        db.session.commit()
        # Create bank accounts

    bank_accounts = [
            BankAccount(
                account_id='SGA',
                account_name='SGA',
                account_description='Umpires & Equipment'
            ),
            BankAccount(
                account_id='RecWell',
                account_name='RecWell',
                account_description='Hotels & Equipment'
            ),
            BankAccount(
                account_id='Foundation',
                account_name='Foundation',
                account_description='Donations & Grants'
            ),
            BankAccount(
                account_id='SECU',
                account_name='SECU',
                account_description='Food & Transportation'
            )
        ]

    db.session.add_all(bank_accounts)
    db.session.commit()

        # Initial loading of ledger transactions
    transactions = [
            Transaction(
                transaction_id="R122501", transaction_date=date(2025, 12, 2), game_id=None,
                account_id="SGA", team_id="Both", description="UMD Concessions MBB v Wagner",
                transaction_type="Revenue", location="UMD", amount=Decimal("1110.48"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="R122502", transaction_date=date(2025, 12, 2), game_id=None,
                account_id="RecWell", team_id="Both", description="RecWell Points",
                transaction_type="Revenue", location="UMD", amount=Decimal("300.00"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E112501", transaction_date=date(2025, 11, 20), game_id=None,
                account_id="SECU", team_id="NCSA", description="Formal (NCSA Other)",
                transaction_type="Expense", location=None, amount=Decimal("283.00"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E112502", transaction_date=date(2025, 11, 20), game_id=None,
                account_id="SECU", team_id="Active", description="Formal (Active Other)",
                transaction_type="Expense", location=None, amount=Decimal("283.00"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E112503", transaction_date=date(2025, 11, 16), game_id=None,
                account_id="SECU", team_id="NCSA", description="Gear Order (NCSA Other)",
                transaction_type="Expense", location=None, amount=Decimal("3656.52"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="R112501", transaction_date=date(2025, 11, 11), game_id=None,
                account_id="SGA", team_id="Both", description="UMD Concessions MBB v Alcorn",
                transaction_type="Revenue", location="UMD", amount=Decimal("1300.49"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E112504", transaction_date=date(2025, 11, 9), game_id="G8",
                account_id="SECU", team_id="NCSA", description="Snack - Target (NCSA Food)",
                transaction_type="Expense", location="Millersville", amount=Decimal("35.30"),
                receipt_filename=None, status="Voided"),
            Transaction(
                transaction_id="E112505", transaction_date=date(2025, 11, 9), game_id="G8",
                account_id="SECU", team_id="NCSA", description="Gas (NCSA Transportation)",
                transaction_type="Expense", location="Millersville", amount=Decimal("102.80"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E112506", transaction_date=date(2025, 11, 8), game_id="G9",
                account_id="SGA", team_id="Active", description="Umpires (Active Games vs Loyola)",
                transaction_type="Expense", location="UMD", amount=Decimal("200.00"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E112507", transaction_date=date(2025, 11, 8), game_id="G9",
                account_id="SECU", team_id="Active", description="Lunch - Wawa (Active Food)",
                transaction_type="Expense", location="UMD", amount=Decimal("136.00"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E112508", transaction_date=date(2025, 11, 8), game_id="G9",
                account_id="SECU", team_id="Active", description="Snack - Target (Active Food)",
                transaction_type="Expense", location="UMD", amount=Decimal("34.20"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="R112502", transaction_date=date(2025, 11, 7), game_id=None,
                account_id="SGA", team_id="Both", description="UMD Concessions MBB v Georgetown",
                transaction_type="Revenue", location="UMD", amount=Decimal("649.36"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="R102501", transaction_date=date(2025, 10, 27), game_id=None,
                account_id="SGA", team_id="Both", description="UMD Concessions MBB v UMBC",
                transaction_type="Revenue", location="UMD", amount=Decimal("704.87"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E102501", transaction_date=date(2025, 10, 26), game_id="G7",
                account_id="SECU", team_id="NCSA", description="Snack - Target (NCSA Food)",
                transaction_type="Expense", location="UVA", amount=Decimal("37.01"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E102502", transaction_date=date(2025, 10, 25), game_id="G6",
                account_id="SECU", team_id="NCSA", description="Dinner - Texas Roadhouse (NCSA Food)",
                transaction_type="Expense", location="UVA", amount=Decimal("535.30"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E102503", transaction_date=date(2025, 10, 25), game_id="G7",
                account_id="RecWell", team_id="NCSA", description="Hotel (NCSA Hotel - UVA Tourney)",
                transaction_type="Expense", location="UVA", amount=Decimal("900.42"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E102504", transaction_date=date(2025, 10, 24), game_id="G6",
                account_id="SECU", team_id="NCSA", description="Gas (NCSA Transportation)",
                transaction_type="Expense", location="UVA", amount=Decimal("153.38"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E102505", transaction_date=date(2025, 10, 24), game_id="G6",
                account_id="RecWell", team_id="NCSA", description="Hotel (NCSA Hotel - UVA Tourney)",
                transaction_type="Expense", location="UVA", amount=Decimal("770.12"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E102506", transaction_date=date(2025, 10, 19), game_id="G5",
                account_id="SECU", team_id="NCSA", description="Snack - Target (NCSA Food)",
                transaction_type="Expense", location="Delaware", amount=Decimal("36.50"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E102507", transaction_date=date(2025, 10, 19), game_id="G5",
                account_id="SECU", team_id="NCSA", description="Gas (NCSA Transportation)",
                transaction_type="Expense", location="Delaware", amount=Decimal("129.60"),
                receipt_filename=None, status="Voided"),
            Transaction(
                transaction_id="R102502", transaction_date=date(2025, 10, 15), game_id=None,
                account_id="SECU", team_id="NCSA", description="NCSA Fall Membership Dues",
                transaction_type="Revenue", location=None, amount=Decimal("1400.00"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="R102503", transaction_date=date(2025, 10, 15), game_id=None,
                account_id="SECU", team_id="Active", description="Active Fall Membership Dues",
                transaction_type="Revenue", location=None, amount=Decimal("1520.00"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E102508", transaction_date=date(2025, 10, 14), game_id=None,
                account_id="SECU", team_id="NCSA", description="UVA Tourney Fee (NCSA Other)",
                transaction_type="Expense", location="UVA", amount=Decimal("450.00"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E102509", transaction_date=date(2025, 10, 14), game_id=None,
                account_id="SECU", team_id="Active", description="Senior Gifts (Active Other)",
                transaction_type="Expense", location=None, amount=Decimal("98.33"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E092501", transaction_date=date(2025, 9, 28), game_id="G4",
                account_id="SGA", team_id="Active", description="Umpires (Active Games vs ODU)",
                transaction_type="Expense", location="UMD", amount=Decimal("200.00"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E092502", transaction_date=date(2025, 9, 27), game_id="G3",
                account_id="SGA", team_id="NCSA", description="Umpires (NCSA Games vs TCNJ)",
                transaction_type="Expense", location="UMD", amount=Decimal("600.00"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E092503", transaction_date=date(2025, 9, 27), game_id="G3",
                account_id="SECU", team_id="NCSA", description="Lunch - Wawa (NCSA Food)",
                transaction_type="Expense", location="UMD", amount=Decimal("135.50"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E092504", transaction_date=date(2025, 9, 20), game_id="G2",
                account_id="SGA", team_id="Active", description="Umpires (Active Games vs Georgetown)",
                transaction_type="Expense", location="UMD", amount=Decimal("200.00"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E092505", transaction_date=date(2025, 9, 20), game_id="G2",
                account_id="SECU", team_id="Active", description="Snack - Target (Active Food)",
                transaction_type="Expense", location="UMD", amount=Decimal("32.30"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E092506", transaction_date=date(2025, 9, 13), game_id="G1",
                account_id="SECU", team_id="NCSA", description="Snack - Target (NCSA Food)",
                transaction_type="Expense", location="Navy", amount=Decimal("34.43"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E092507", transaction_date=date(2025, 9, 13), game_id="G1",
                account_id="SECU", team_id="NCSA", description="Gas (NCSA Transportation)",
                transaction_type="Expense", location="Navy", amount=Decimal("63.50"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E092508", transaction_date=date(2025, 9, 1), game_id=None,
                account_id="SGA", team_id="NCSA", description="NCSA Dues",
                transaction_type="Expense", location=None, amount=Decimal("1381.00"),
                receipt_filename=None, status="Active"),
            Transaction(
                transaction_id="E092509", transaction_date=date(2025, 9, 1), game_id=None,
                account_id="SECU", team_id="NCSA", description="Exec Meeting Pizza (NCSA Other)",
                transaction_type="Expense", location="UMD", amount=Decimal("70.00"),
                receipt_filename=None, status="Active")
        ]

    for each_trans in transactions:
        print(f'Transaction {each_trans.transaction_id} inserted into Transaction')
        db.session.add(each_trans)
        db.session.commit()

    # Initial loading of team dues by semester

    teams = [
        Team(
            teamName='NCSA',
            teamSemesterYear='Fall 2026',
            teamDuesAmount=Decimal('100.00'),
            teamSemesterStatus='Current'
        ),
        Team(
            teamName='Active',
            teamSemesterYear='Fall 2026',
            teamDuesAmount=Decimal('100.00'),
            teamSemesterStatus='Current'
        ),
        Team(
            teamName='NCSA',
            teamSemesterYear='Spring 2027',
            teamDuesAmount=Decimal('100.00'),
            teamSemesterStatus='Upcoming'
        ),
        Team(
            teamName='Active',
            teamSemesterYear='Spring 2027',
            teamDuesAmount=Decimal('100.00'),
            teamSemesterStatus = 'Upcoming'
        ),
        Team(
            teamName='NCSA',
            teamSemesterYear='Fall 2027',
            teamDuesAmount=Decimal('100.00'),
            teamSemesterStatus = 'Upcoming'
        ),
        Team(
            teamName='Active',
            teamSemesterYear='Fall 2027',
            teamDuesAmount=Decimal('100.00'),
            teamSemesterStatus='Upcoming'
        )
    ]

    for each_team in teams:
        print(
            f'{each_team.teamName} - '
            f'{each_team.teamSemesterYear} - '
            f'{each_team.teamSemesterStatus} inserted into Team'
        )
        db.session.add(each_team)

    db.session.commit()