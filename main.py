from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, User, Game, Team, Expense, Transaction
from datetime import date
from decimal import Decimal, InvalidOperation
from werkzeug.utils import secure_filename
import os
import uuid
import pandas as pd
app = Flask(__name__)
# Secret key for reimbursement flash messages
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY', 'local-development-only-key'
)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///softball.db'

# Folder for reimbursement receipt uploads
app.config['UPLOAD_FOLDER'] = os.path.join(
    app.root_path, 'static', 'uploads'
)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
db.init_app(app)

with app.app_context():
    db.create_all()
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

@app.route('/reimbursement-request', methods=['GET', 'POST'])
def reimbursement_request():
    if request.method == 'POST':

        # Retrieve submitted form information
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        venmo = request.form.get('venmo', '').strip()
        expense_date = request.form.get('expense_date', '')
        game = request.form.get('game', '').strip()
        amount = request.form.get('amount', '')
        description = request.form.get('description', '').strip()

        receipt = request.files.get('receipt')

        # Validate receipt
        allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png'}

        if not receipt or not receipt.filename:
            flash('Please upload a receipt.', 'danger')
            return redirect(url_for('reimbursement_request'))

        extension = receipt.filename.rsplit('.', 1)[-1].lower()

        if '.' not in receipt.filename or extension not in allowed_extensions:
            flash('Invalid receipt file type.', 'danger')
            return redirect(url_for('reimbursement_request'))

        try:
            # Validate date and amount
            parsed_date = date.fromisoformat(expense_date)
            parsed_amount = Decimal(amount)

            if not parsed_amount.is_finite() or parsed_amount <= 0:
                raise ValueError('Amount must be greater than zero.')

            # Generate a unique receipt filename
            filename = secure_filename(receipt.filename)
            filename = f'{uuid.uuid4().hex}_{filename}'

            receipt_path = os.path.join(
                app.config['UPLOAD_FOLDER'],
                filename
            )

            receipt.save(receipt_path)

            # CREATE: Save reimbursement to database
            new_expense = Expense(
                first_name=first_name,
                last_name=last_name,
                venmo=venmo,
                expense_date=parsed_date,
                game=game,
                amount=parsed_amount,
                description=description,
                receipt_filename=filename,
                approval_status='Pending',
                repayment_status=False
            )

            db.session.add(new_expense)
            db.session.commit()

            flash('Reimbursement submitted successfully!', 'success')

            return redirect(url_for('reimbursement_request'))

        except (ValueError, InvalidOperation):
            flash('Please enter a valid date and amount.', 'danger')

        except Exception:
            db.session.rollback()
            flash('Unable to save reimbursement.', 'danger')

    return render_template('reimbursement-request.html')

@app.route('/reimbursement-review')
def reimbursement_review():
    # READ: Retrieve reimbursements from the database
    expenses = Expense.query.order_by(
        Expense.expense_id.desc()
    ).all()
    return render_template('reimbursement-review.html',
        expenses=expenses
    )
# Reimbursement Review Update
@app.route('/reimbursement-review-update/<int:expense_id>',
           methods=['GET','POST'])
def reimbursement_review_update(expense_id):
    # Find the reimbursement being edited
    expense = db.get_or_404(Expense, expense_id)
    if request.method == 'POST':

        # Get updated information from the form
        approval_status = request.form.get('approval_status')
        repayment_status = request.form.get('repayment_status')
        treasurer_comment = request.form.get(
            'treasurer_comment', ''
        ).strip()

        # Validate submitted information
        if approval_status not in ['Pending', 'Approved', 'Denied']:
            flash('Please select a valid approval status.', 'danger')
            return redirect(url_for(
                'reimbursement_review_update',
                expense_id=expense_id
            ))

        if repayment_status not in ['Yes', 'No']:
            flash('Please select a repayment status.', 'danger')
            return redirect(url_for(
                'reimbursement_review_update',
                expense_id=expense_id
            ))

        if approval_status == 'Denied' and not treasurer_comment:
            flash('Please provide a reason for denial.', 'danger')
            return redirect(url_for(
                'reimbursement_review_update',
                expense_id=expense_id
            ))

        # UPDATE: Change the existing database record
        expense.approval_status = approval_status
        expense.repayment_status = (repayment_status == 'Yes')
        expense.treasurer_comment = treasurer_comment

        db.session.commit()

        db.session.commit()

        flash('Reimbursement updated successfully!', 'success')

        return redirect(url_for('reimbursement_review'))

    return render_template(
            'reimbursement-review-update.html',
             expense=expense
             )
# DELETE: Remove a reimbursement from the database
@app.route('/reimbursement-delete/<int:expense_id>', methods=['POST'])
def reimbursement_delete(expense_id):

    # Find the reimbursement
    expense = db.get_or_404(Expense, expense_id)

    # Delete the reimbursement
    db.session.delete(expense)
    db.session.commit()

    flash('Reimbursement deleted successfully!', 'success')

    return redirect(url_for('reimbursement_review'))

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
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx', 'ofx', 'qfx', 'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# READ: Financial Ledger
@app.route('/financial-ledger')
def financial_ledger():
    transactions = Transaction.query.order_by(Transaction.transaction_date.desc()).all()
    return render_template('financial-ledger.html', transactions=transactions)

# UPDATE: Edit Existing Transaction
@app.route('/financial-ledger-update/<transaction_id>', methods=['GET', 'POST'])
def financial_ledger_update(transaction_id):
    transaction = Transaction.query.filter_by(transaction_id=transaction_id).first_or_404()
    if request.method == 'POST':
        transaction.transaction_date = date.fromisoformat(request.form.get('transactionDate'))
        transaction.account_id = request.form.get('accountID')
        teams = request.form.getlist('teamID')
        transaction.team_id = "Both" if len(teams) > 1 else (teams[0] if teams else "NCSA")

        t_type = request.form.get('transactionType')
        revenue_types = {'Fundraising', 'Dues', 'Donation', 'Other Revenue'}
        transaction.transaction_type = 'Revenue' if t_type in revenue_types else 'Expense'

        transaction.amount = Decimal(request.form.get('amount', '0.00'))
        transaction.game_id = request.form.get('gameID') or None
        transaction.location = request.form.get('location')
        transaction.description = request.form.get('description')

        receipt = request.files.get('expenseReceipt')
        if receipt and receipt.filename and allowed_file(receipt.filename):
            receipt_name = secure_filename(f"{transaction_id}_{receipt.filename}")
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            receipt.save(os.path.join(app.config['UPLOAD_FOLDER'], receipt_name))
            transaction.receipt_filename = receipt_name
        db.session.commit()
        return redirect('/financial-ledger')
    return render_template('financial-ledger-update.html', transaction=transaction)

# CREATE: Manual Entry
@app.route('/record-transaction', methods=['GET', 'POST'])
def record_transaction():
    if request.method == 'POST':
        t_type = request.form.get('transactionType')

        # Transaction ID prefix R for Revenue or E for Expense
        revenue_types = {'Fundraising', 'Dues', 'Donation', 'Other Revenue'}
        resolved_category = 'Revenue' if t_type in revenue_types else 'Expense'
        prefix = 'R' if resolved_category == 'Revenue' else 'E'

        # Transaction Date or default to user's current date
        raw_date = request.form.get('transactionDate')
        t_date = date.fromisoformat(raw_date) if raw_date else date.today()

        # 3. Date format as month (MM) + year (YY) -> e.g., '1126' -> November 2026
        month_str = t_date.strftime("%m")
        year_str = t_date.strftime("%y")
        base_pattern = f"{prefix}{month_str}{year_str}"

        # Read previously created Transaction IDs to create new Transaction ID number (e.g., 'R1126%')
        existing_matches = [
            t.transaction_id for t in Transaction.query.filter(
                Transaction.transaction_id.like(f"{base_pattern}%")
            ).all()
        ]

        # Find the next available counter for  Transaction ID
        seq_numbers = []
        for tid in existing_matches:
            suffix = tid[len(base_pattern):]
            if suffix.isdigit():
                seq_numbers.append(int(suffix))

        next_seq = max(seq_numbers) + 1 if seq_numbers else 1
        t_id = f"{base_pattern}{next_seq:02d}"  # 01, 02, 03...

        acc_id = request.form.get('accountID')

        teams = request.form.getlist('teamID')
        if len(teams) > 1:
            team_id = "Both"
        elif len(teams) == 1:
            team_id = teams[0]
        else:
            team_id = "Both"

        amount_raw = request.form.get('amount', '0.00').strip()
        amount = Decimal(amount_raw) if amount_raw else Decimal('0.00')

        game_id = request.form.get('gameID', '').strip() or None
        location = request.form.get('location', '').strip() or None
        description = request.form.get('description', '').strip()

        receipt_filename = None
        receipt = request.files.get('expenseReceipt')
        if receipt and receipt.filename and allowed_file(receipt.filename):
            receipt_name = secure_filename(f"{t_id}_{receipt.filename}")
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            receipt.save(os.path.join(app.config['UPLOAD_FOLDER'], receipt_name))
            receipt_filename = receipt_name

        new_trans = Transaction(
            transaction_id=t_id, transaction_date=t_date, game_id=game_id,
            account_id=acc_id, team_id=team_id, description=description,
            transaction_type=resolved_category, location=location, amount=amount,
            receipt_filename=receipt_filename)

        db.session.add(new_trans)
        db.session.commit()
        return redirect('/financial-ledger')
    return render_template('record-transaction.html')


@app.route('/upload-transactions', methods=['GET', 'POST'])
# @login_required
# @role_required(['TREASURER', 'ADVISOR'])
def upload_transactions():
    if request.method == 'POST':
        file = request.files.get('statement_file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                # 1. Read the Excel file into a pandas DataFrame
                df = pd.read_excel(filepath)

                # Basic validation to ensure they used the template
                required_cols = ['Date', 'Account', 'Team', 'Type', 'Amount', 'Description']
                if not all(col in df.columns for col in required_cols):
                    flash('Upload failed: File is missing required template columns.', 'error')
                    return redirect('/upload-transactions')

                sequence_tracker = {}
                success_count = 0

                # 2. Loop through each row in the Excel sheet
                for index, row in df.iterrows():

                    # Parse the date and resolve the transaction type
                    t_date = pd.to_datetime(row['Date']).date()
                    t_type = str(row['Type']).strip()
                    revenue_types = ['Fundraising', 'Dues', 'Donation', 'Other Revenue']
                    resolved_category = 'Revenue' if t_type in revenue_types else 'Expense'

                    # 3. Generate the dynamic Transaction ID (e.g., R112601)
                    prefix = 'R' if resolved_category == 'Revenue' else 'E'
                    base_pattern = f"{prefix}{t_date.strftime('%m%y')}"

                    # Check our local tracker to prevent duplicates within the same batch upload
                    if base_pattern not in sequence_tracker:
                        existing_matches = Transaction.query.filter(
                            Transaction.transaction_id.like(f"{base_pattern}%")).all()
                        seq_numbers = [int(t.transaction_id[len(base_pattern):]) for t in existing_matches if
                                       t.transaction_id[len(base_pattern):].isdigit()]
                        sequence_tracker[base_pattern] = max(seq_numbers) + 1 if seq_numbers else 1

                    t_id = f"{base_pattern}{sequence_tracker[base_pattern]:02d}"
                    sequence_tracker[base_pattern] += 1  # Increment for the next row

                    # 4. Handle optional fields cleanly
                    game_id_val = str(row['Game ID']).strip() if pd.notna(row.get('Game ID')) else None
                    location_val = str(row['Location']).strip() if pd.notna(row.get('Location')) else None

                    # 5. Create the database object and stage it
                    new_trans = Transaction(
                        transaction_id=t_id,
                        transaction_date=t_date,
                        account_id=str(row['Account']).strip(),
                        team_id=str(row['Team']).strip(),
                        description=str(row['Description']).strip(),
                        transaction_type=resolved_category,
                        amount=Decimal(str(row['Amount']).strip()),
                        location=location_val,
                        game_id=game_id_val,
                        receipt_filename=None
                    )
                    db.session.add(new_trans)
                    success_count += 1

                # 6. Commit the entire batch to the database at once
                db.session.commit()
                flash(f'Success! Processed {success_count} transactions from the template.', 'success')
                return redirect('/financial-ledger')

            except Exception as e:
                db.session.rollback()
                flash(f'Error processing file. Ensure you used the provided template. Details: {str(e)}', 'error')
                return redirect('/upload-transactions')

        else:
            flash('Invalid file type. Please upload a valid CSV or Excel file.', 'error')
            return redirect('/upload-transactions')

    return render_template('upload-transactions.html')

# DELETE: Delete Transaction
@app.route('/financial-ledger-void/<transaction_id>', methods=['POST'])
#@login_required
#@role_required(['TREASURER', 'ADVISOR'])
def financial_ledger_void(transaction_id):
    transaction = Transaction.query.filter_by(transaction_id=transaction_id).first_or_404()
    transaction.status = 'Voided'
    db.session.commit()
    flash(f'Transaction {transaction_id} has been voided.', 'success')
    return redirect('/financial-ledger')

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
    return render_template('reimbursement-request.html')

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

@app.route('/game-schedule-update/<int:game_id>', methods=['GET', 'POST'])
def game_schedule_update(game_id):

    game = db.get_or_404(Game, game_id)

    if request.method == 'POST':

        game.team_id = request.form['team_id']
        game.opponent = request.form['opponent']
        game.game_date = date.fromisoformat(request.form['game_date'])
        game.game_times = request.form['game_times']
        game.game_location = request.form['game_location']

        db.session.commit()

        flash('Game updated successfully!', 'success')

        return redirect(url_for('game_schedule_after_login'))

    return render_template('game-schedule-update.html', game=game)


@app.route('/game-schedule-delete/<int:game_id>', methods=['POST'])
def game_schedule_delete(game_id):
    game = db.get_or_404(Game, game_id)
    db.session.delete(game)
    db.session.commit()
    flash('Game deleted successfully!', 'success')
    return redirect(url_for('game_schedule_after_login'))


if __name__ == '__main__':
    app.run(port=5001)
