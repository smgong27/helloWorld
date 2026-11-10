from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Game, Team
from datetime import date
from decimal import Decimal, InvalidOperation
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///softball.db'

db.init_app(app)
# GENERAL ROUTES

@app.route('/')
def home_page():
    return render_template('home-page.html')

@app.route('/log-in', methods=['GET', 'POST'])
def log_in():
    if request.method =="POST":
        email = request.form['umd_email']
        password = request.form['password']
        return redirect('/advisor-dashboard')
    return render_template('log-in.html')

@app.route('/create-account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        email = request.form['umd_email']
        password = request.form['password']
        return redirect('/advisor-dashboard')
    return render_template('create-account.html')

# PERSONA OVERVIEW ROUTES

@app.route('/member-dashboard')
def member_page():
    return render_template('member-dashboard.html')

@app.route('/treasurer-dashboard')
def treasurer_page():
    return render_template('treasurer-dashboard.html')

@app.route('/executive-dashboard')
def executive_page():
    return render_template('executive-dashboard.html')

@app.route('/advisor-dashboard')
def advisor_page():
    return render_template('advisor-dashboard.html')

# REIMBURSEMENT ROUTES

@app.route('/reimbursement-request')
def reimbursement_request():
    return render_template('reimbursement-request.html')

@app.route('/reimbursement-review')
def reimbursement_review():
    return render_template('reimbursement-review.html')
# Reimbursement Review Update
@app.route('/reimbursement-review-update', methods=['GET','POST'])
def reimbursement_review_update():
    if request.method == 'POST':
        return redirect('/reimbursement-review')
    return render_template('reimbursement-review-update.html')

# MY INFORMATION & DUES ROUTES

@app.route('/my-information')
def my_information():
    return render_template('my-information.html')

@app.route('/pay-dues')
def pay_dues():
    return render_template('pay-dues.html')

# TEAM ROSTER ROUTE

@app.route('/team-roster')
def team_roster():
    return render_template('team-roster.html')

@app.route('/team-roster-update', methods=['GET', 'POST'])
def team_roster_update():
    if request.method == 'POST':
        # Add database save logic here later
        return redirect('team_roster')
    return render_template('team-roster-update.html')

# FINANCIAL LEDGER ROUTES

@app.route('/financial-ledger')
def financial_ledger():
    return render_template('financial-ledger.html')

@app.route('/financial-ledger-update/<transaction_id>', methods=['GET', 'POST'])
def financial_ledger_update(transaction_id):
    if request.method == 'POST':
        transaction_date = request.form.get('transactionDate')
        account_id = request.form.get('accountID')
        team_id = request.form.getlist('teamID')
        transaction_type = request.form.get('transactionType')
        amount = request.form.get('amount')
        game_id = request.form.get('gameID')
        location = request.form.get('location')
        description = request.form.get('description')
        receipt = request.files.get('expenseReceipt')
        return redirect('/financial-ledger')
    return render_template('financial-ledger-update.html')

@app.route('/record-transaction')
def record_transaction():
    return render_template('record-transaction.html')

@app.route('/upload-transactions')
def upload_transactions():
    return render_template('upload-transactions.html')

# OTHER FINANCIAL ROUTES

@app.route('/financial-report')
def financial_report():
    return render_template('financial-report.html')

@app.route('/bank-accounts')
def bank_accounts():
    return render_template('bank-accounts.html')

# EDIT TEAM DUES ROUTE

@app.route('/edit-team-dues', methods=['GET', 'POST'])
def edit_team_dues():
    semesters = [
        semester[0]
        for semester in db.session.query(
            Team.teamSemesterYear
        ).distinct().order_by(Team.teamSemesterYear).all()
    ]

    # Handle Save Changes
    if request.method == 'POST':

        semester = request.form.get('semester', '').strip()

        try:
            # Retrieve dues amounts from the form
            ncsa_dues = Decimal(request.form.get('ncsa_dues', '').strip())
            active_dues = Decimal(request.form.get('active_dues', '').strip())

            # Validate that amounts are valid numbers
            if not ncsa_dues.is_finite() or not active_dues.is_finite():
                raise ValueError("Please enter valid dues amounts.")

            # Dues cannot be negative
            if ncsa_dues < 0 or active_dues < 0:
                raise ValueError("Dues amounts cannot be negative.")

            # Allow no more than two decimal places
            if (ncsa_dues != ncsa_dues.quantize(Decimal('0.01'))
                    or active_dues != active_dues.quantize(Decimal('0.01'))):
                raise ValueError("Dues amounts can have at most two decimal places.")

            # Verify that the selected semester is valid
            if semester not in semesters:
                raise ValueError("Please select a valid semester.")

            # Find the existing team records
            ncsa_team = Team.query.filter_by(
                teamName='NCSA Team',
                teamSemesterYear=semester
            ).first()

            active_team = Team.query.filter_by(
                teamName='Active Team',
                teamSemesterYear=semester
            ).first()

            if not ncsa_team or not active_team:
                raise ValueError("Team records could not be found.")

            # Update the existing records
            ncsa_team.teamDuesAmount = ncsa_dues
            active_team.teamDuesAmount = active_dues

            # Save changes to the database
            db.session.commit()

            return redirect(url_for(
                'edit_team_dues',
                semester=semester
            ))

        except (InvalidOperation, ValueError) as error:
            db.session.rollback()

        except Exception:
            db.session.rollback()

    # Determine which semester to display
    if request.method == 'POST':
        selected_semester = request.form.get('semester', '')
    else:
        selected_semester = request.args.get('semester', '')

    if not semesters:
        selected_semester = None
    elif selected_semester not in semesters:
        selected_semester = semesters[0]

    # Retrieve the selected semester's records
    ncsa_team = None
    active_team = None

    if selected_semester:
        ncsa_team = Team.query.filter_by(
            teamName='NCSA Team',
            teamSemesterYear=selected_semester
        ).first()

        active_team = Team.query.filter_by(
            teamName='Active Team',
            teamSemesterYear=selected_semester
        ).first()

    # Display the page
    return render_template(
        'edit-team-dues.html',
        semesters=semesters,
        selected_semester=selected_semester,
        ncsa_dues=ncsa_team.teamDuesAmount if ncsa_team else '',
        active_dues=active_team.teamDuesAmount if active_team else ''
    )

# USER PERMISSION ROUTES

@app.route('/user-permissions')
def user_permissions():
    return render_template('user-permissions.html')


# GAME SCHEDULE ROUTES

@app.route('/record-game')
def record_game():
    return render_template('record-game.html')

@app.route('/game-schedule-after-login')
def game_schedule_after_login():
    games = Game.query.order_by(Game.game_date).all()
    return render_template('game-schedule-after-login.html', games=games)

@app.route('/game-schedule-create', methods=['GET', 'POST'])
def game_schedule_create():
    if request.method == 'POST':

        team_id = request.form['team_id']
        opponent = request.form['opponent']
        game_date = date.fromisoformat(request.form['game_date'])
        game_times = request.form['game_times']
        game_location = request.form['game_location']

        new_game = Game(
            team_id=team_id,
            opponent=opponent,
            game_date=game_date,
            game_times=game_times,
            game_location=game_location
        )

        db.session.add(new_game)
        db.session.commit()

        return redirect('/game-schedule-after-login')

    return render_template('game-schedule-create.html')

@app.route('/game-schedule-update')
def game_schedule_update():
    return render_template('game-schedule-update.html')


if __name__ == '__main__':
    app.run(port=5001)
