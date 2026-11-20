from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash
from authorize import role_required
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, User, Game, Team, Expense, Transaction, BankAccount
from datetime import date, datetime
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


# Flask-Login configuration
login_manager = LoginManager()
login_manager.login_view = 'log_in'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
# GENERAL ROUTES

@app.route('/')
def home_page():
    games = Game.query.order_by(Game.game_date).all()
    return render_template('home-page.html', games=games)


@app.route('/log-in', methods=['GET', 'POST'])
def log_in():

    if request.method == 'POST':

        email = request.form.get('umd_email')
        password = request.form.get('password')

        # TEMPORARY: Skip authentication during development
        return redirect(url_for('member_page'))

        # AUTHENTICATION CODE - Enable when ready

        # user = User.query.filter_by(email=email).first()

        # if user and check_password_hash(user.password, password):

            # login_user(user)

            # if current_user.user_persona == 'MEMBER':
                # return redirect(url_for('member_page'))

            # elif current_user.user_persona == 'EXECUTIVE':
                # return redirect(url_for('executive_page'))

            # elif current_user.user_persona == 'TREASURER':
                # return redirect(url_for('treasurer_page'))

            # elif current_user.user_persona == 'ADVISOR':
                # return redirect(url_for('advisor_page'))

        # flash('Your login information was not correct. Please try again.', 'error')

        # return redirect(url_for('log_in'))

    return render_template('log-in.html')

@app.errorhandler(404)
def page_not_found(e):
    flash(f'Sorry! You are trying to access a page that does not exist. Please contact support if this problem persists.', 'error')
    return render_template('404.html'), 404

@app.route('/logout')
# @login_required
def logout():
    # logout_user()  # Enable when authentication is active
    flash('You have been logged out.', 'success')
    return redirect(url_for('home_page'))

@app.route('/create-account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        email = request.form['umd_email']
        password = request.form['password']
        return redirect('/advisor-dashboard')
    return render_template('create-account.html')

# PERSONA OVERVIEW ROUTES

## Function to get and return next game
def get_next_game():
    today = date.today()

    games = Game.query.order_by(Game.game_date.asc()).all()

    for game in games:
        game_date = game.game_date

        #Using isinstance so each game can be stored seperately and the function can return the next game
        if isinstance(game_date, datetime):
            game_date = game_date.date()

        if game_date >= today:
            return game

    return None

@app.route('/member-dashboard')
# @login_required
# @role_required(['MEMBER'])
def member_page():
    return render_template('member-dashboard.html')

@app.route('/treasurer-dashboard')
# @login_required
# @role_required(['TREASURER'])
def treasurer_page():
    next_game = get_next_game()
    return render_template('treasurer-dashboard.html', next_game=next_game)


@app.route('/executive-dashboard')
# @login_required
# @role_required(['EXECUTIVE'])
def executive_page():
    next_game = get_next_game()
    return render_template('executive-dashboard.html', next_game=next_game)

@app.route('/advisor-dashboard')
# @login_required
# @role_required(['ADVISOR'])
def advisor_page():
    next_game = get_next_game()
    return render_template('advisor-dashboard.html', next_game=next_game)

# REIMBURSEMENT ROUTES

@app.route('/reimbursement-request', methods=['GET', 'POST'])
# @login_required
# @role_required(['EXECUTIVE', 'TREASURER', 'ADVISOR'])
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
# @login_required
# @role_required(['EXECUTIVE', 'TREASURER', 'ADVISOR'])
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
# @login_required
# @role_required(['TREASURER', 'ADVISOR'])
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

        flash('Reimbursement updated successfully!', 'success')

        return redirect(url_for('reimbursement_review'))

    return render_template(
            'reimbursement-review-update.html',
             expense=expense
             )
# DELETE: Remove a reimbursement from the database
@app.route('/reimbursement-delete/<int:expense_id>', methods=['POST'])
# @login_required
# @role_required(['TREASURER', 'ADVISOR'])
def reimbursement_delete(expense_id):

    # Find the reimbursement
    expense = db.get_or_404(Expense, expense_id)

    # Delete the reimbursement
    db.session.delete(expense)
    db.session.commit()

    flash('Reimbursement deleted successfully!', 'success')

    return redirect(url_for('reimbursement_review'))

# MY INFORMATION & DUES ROUTES

# MY INFORMATION ROUTES

@app.route('/my-information')
# @login_required
def my_information():
    # Fetch the logged-in user (temporarily using ID 1 for testing)
    user = User.query.get(1)
    return render_template('my-information.html', user=user)


@app.route('/my-information-update', methods=['GET', 'POST'])
# @login_required
def my_information_update():
    # Fetch the logged-in user (temporarily using ID 1 for testing)
    user = User.query.get(1)

    if request.method == 'POST':
        # Update only the personal fields (not role, team, or dues)
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.email = request.form.get('email')
        user.exp = request.form.get('exp')

        # If they submit a new expected graduation date, update it
        grad_date = request.form.get('expected_graduation_date')
        if grad_date:
            from datetime import datetime
            user.expected_graduation_date = datetime.strptime(grad_date, '%Y-%m-%d').date()

        db.session.commit()
        flash('Your information has been successfully updated.', 'success')
        return redirect('/my-information')

    return render_template('my-information-update.html', user=user)

@app.route('/pay-dues')
# @login_required
# @role_required(['MEMBER', 'EXECUTIVE', 'TREASURER'])
def pay_dues():
    return render_template('pay-dues.html')

# TEAM ROSTER ROUTE

@app.route('/team-roster')
# @login_required
# @role_required(['EXECUTIVE', 'TREASURER', 'ADVISOR'])
def team_roster():
    # Fetch all users who are players (filtering out the Advisor)
    roster = User.query.filter(User.user_persona != 'ADVISOR').all()
    return render_template('team-roster.html', roster=roster)


@app.route('/team-roster-update', methods=['GET', 'POST'])
# @login_required
# @role_required(['EXECUTIVE', 'TREASURER', 'ADVISOR'])
def team_roster_update():
    roster = User.query.filter(User.user_persona != 'ADVISOR').all()

    if request.method == 'POST':
        # Loop through every player on the roster
        for member in roster:
            # Grab the specific dropdown values for this exact member using their unique ID
            new_status = request.form.get(f'status_{member.member_id}')
            new_team = request.form.get(f'team_{member.member_id}')

            # Update the database object if data was submitted
            if new_status:
                # Convert the string "True"/"False" from HTML back into a Python Boolean
                member.active_status = (new_status == 'True')
            if new_team:
                member.team = new_team

        db.session.commit()
        flash('Team roster has been successfully updated.', 'success')
        return redirect('/team-roster')

    return render_template('team-roster-update.html', roster=roster)

# FINANCIAL LEDGER ROUTES
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'csv', 'xls', 'xlsx', 'ofx', 'qfx', 'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to generate the next sequential Transaction ID (e.g., R112501, E102510)
def generate_next_transaction_id(resolved_category, t_date):
    prefix = 'R' if resolved_category == 'Revenue' else 'E'
    base_pattern = f"{prefix}{t_date.strftime('%m%y')}"

    existing_matches = [
        t.transaction_id for t in Transaction.query.filter(
            Transaction.transaction_id.like(f"{base_pattern}%")
        ).all()
    ]
    seq_numbers = []
    for tid in existing_matches:
        suffix = tid[len(base_pattern):]
        if suffix.isdigit():
            seq_numbers.append(int(suffix))

    next_seq = max(seq_numbers) + 1 if seq_numbers else 1
    return f"{base_pattern}{next_seq:02d}"

# READ: Financial Ledger
@app.route('/financial-ledger')
# @login_required
# @role_required(['EXECUTIVE', 'TREASURER', 'ADVISOR'])
def financial_ledger():
    transactions = Transaction.query.order_by(Transaction.transaction_date.desc()).all()
    return render_template('financial-ledger.html', transactions=transactions)

# UPDATE: Edit Existing Transaction
@app.route('/financial-ledger-update/<transaction_id>', methods=['GET', 'POST'])
# @login_required
# @role_required(['TREASURER', 'ADVISOR'])
def financial_ledger_update(transaction_id):
    transaction = Transaction.query.filter_by(transaction_id=transaction_id).first_or_404()

    # Block editing if the transaction has already been voided
    if transaction.status == 'Voided':
        flash(f'Transaction {transaction_id} is voided and cannot be modified.', 'danger')
        return redirect('/financial-ledger')

    if request.method == 'POST':
        # Store submitted values in new_* variables (do NOT overwrite transaction yet)
        new_date = date.fromisoformat(request.form.get('transactionDate'))
        new_account = request.form.get('accountID')
        teams = request.form.getlist('teamID')
        new_team = "Both" if len(teams) > 1 else (teams[0] if teams else "NCSA")

        t_type = request.form.get('transactionType')
        revenue_types = {'Fundraising', 'Dues', 'Donation', 'Other Revenue'}
        new_category = 'Revenue' if t_type in revenue_types else 'Expense'

        raw_amount = request.form.get('amount', '0.00').strip()
        new_amount = Decimal(raw_amount).quantize(Decimal('0.01')) if raw_amount else Decimal('0.00')

        new_game_id = request.form.get('gameID', '').strip() or None
        new_location = request.form.get('location', '').strip() or None
        new_description = request.form.get('description', '').strip()

        # Check if any core financial field was changed
        existing_amount = Decimal(str(transaction.amount)).quantize(Decimal('0.01'))
        financial_fields_changed = (
            transaction.transaction_date != new_date or
            transaction.account_id != new_account or
            transaction.team_id != new_team or
            transaction.transaction_type != new_category or
            existing_amount != new_amount
        )
        receipt = request.files.get('expenseReceipt')

        # PATH A: Only non-financial data changed -> Update existing row in place
        if not financial_fields_changed:
            transaction.game_id = new_game_id
            transaction.location = new_location
            transaction.description = new_description

            if receipt and receipt.filename and allowed_file(receipt.filename):
                receipt_name = secure_filename(f"{transaction_id}_{receipt.filename}")
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                receipt.save(os.path.join(app.config['UPLOAD_FOLDER'], receipt_name))
                transaction.receipt_filename = receipt_name

            db.session.commit()
            flash(f'Transaction {transaction_id} details updated.', 'success')
            return redirect('/financial-ledger')

        # PATH B: Financial field(s) changed -> Void original & create replacement transaction
        else:
            new_t_id = generate_next_transaction_id(new_category, new_date)

            # Carry over existing receipt unless a replacement receipt was uploaded
            final_receipt = transaction.receipt_filename
            if receipt and receipt.filename and allowed_file(receipt.filename):
                receipt_name = secure_filename(f"{new_t_id}_{receipt.filename}")
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                receipt.save(os.path.join(app.config['UPLOAD_FOLDER'], receipt_name))
                final_receipt = receipt_name

            # Void the original transaction without altering its original financial numbers
            transaction.status = 'Voided'
            if f"Replaced by {new_t_id}" not in transaction.description:
                transaction.description = f"{transaction.description} [Voided — Replaced by {new_t_id}]"

            # Create the new replacement transaction with the updated financial numbers
            replacement_desc = f"{new_description} [Replaces {transaction.transaction_id}]"
            replacement_trans = Transaction(
                transaction_id=new_t_id, transaction_date=new_date, game_id=new_game_id,
                account_id=new_account, team_id=new_team, description=replacement_desc,
                transaction_type=new_category, location=new_location, amount=new_amount,
                receipt_filename=final_receipt, status='Active'
            )
            db.session.add(replacement_trans)
            db.session.commit()
            flash(
                f'Financial change detected: Original entry {transaction.transaction_id} was voided '
                f'and reissued as {new_t_id}.',
                'success')
            return redirect('/financial-ledger')
    return render_template('financial-ledger-update.html', transaction=transaction)

# CREATE: Manual Entry
@app.route('/record-transaction', methods=['GET', 'POST'])
# @login_required
# @role_required(['TREASURER', 'ADVISOR'])
def record_transaction():
    if request.method == 'POST':
        t_type = request.form.get('transactionType')

        # Transaction ID prefix R for Revenue or E for Expense
        revenue_types = {'Fundraising', 'Dues', 'Donation', 'Other Revenue'}
        resolved_category = 'Revenue' if t_type in revenue_types else 'Expense'

        # Transaction Date or default to user's current date
        raw_date = request.form.get('transactionDate')
        t_date = date.fromisoformat(raw_date) if raw_date else date.today()

        # Generate sequential Transaction ID (e.g., R112501)
        t_id = generate_next_transaction_id(resolved_category, t_date)
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
            receipt_filename=receipt_filename, status='Active')

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

# VOID: Void Transaction Without Replacement
@app.route('/financial-ledger-void/<transaction_id>', methods=['POST'])
#@login_required
#@role_required(['TREASURER', 'ADVISOR'])
def financial_ledger_void(transaction_id):
    transaction = Transaction.query.filter_by(transaction_id=transaction_id).first_or_404()
    if transaction.status != 'Voided':
        transaction.status = 'Voided'
        if "[Voided]" not in transaction.description and "[Voided —" not in transaction.description:
            transaction.description = f"{transaction.description} [Voided]"
    db.session.commit()
    flash(f'Transaction {transaction_id} has been voided.', 'success')
    return redirect('/financial-ledger')

# OTHER FINANCIAL ROUTES

@app.route('/financial-report')
# @login_required
# @role_required(['EXECUTIVE', 'TREASURER', 'ADVISOR'])
def financial_report():
    return render_template('financial-report.html')

@app.route('/bank-accounts')
# @login_required
# @role_required(['TREASURER', 'ADVISOR'])
def bank_accounts():
    # Initialize all four account balances at zero
    account_balances = {
        'SGA': Decimal('0.00'),
        'RecWell': Decimal('0.00'),
        'Foundation': Decimal('0.00'),
        'SECU': Decimal('0.00')
    }

    # Retrieve all active transactions associated with these accounts
    transactions = Transaction.query.filter(
        Transaction.status == 'Active',
        Transaction.account_id.in_(account_balances.keys())
    ).all()

    # Calculate each account's balance
    for transaction in transactions:

        if transaction.transaction_type == 'Revenue':
            account_balances[transaction.account_id] += transaction.amount

        elif transaction.transaction_type == 'Expense':
            account_balances[transaction.account_id] -= transaction.amount

    return render_template(
        'bank-accounts.html',
        account_balances=account_balances
    )

# EDIT TEAM DUES ROUTE

@app.route('/edit-team-dues', methods=['GET', 'POST'])
# @login_required
# @role_required(['TREASURER', 'ADVISOR'])
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
# Allowed permission values
VALID_PERSONAS = {
    "MEMBER",
    "TREASURER",
    "EXECUTIVE",
    "ADVISOR"
}
@app.route('/user-permissions')
# @login_required
# @role_required(['ADVISOR'])
def user_permissions():
    # Retrieve users who have not been deleted
    users = User.query.filter(
        User.user_persona != "VOID"
    ).order_by(User.last_name, User.first_name).all()

    return render_template('user-permissions.html',
                           users=users)
@app.route('/update-user-permissions', methods=['POST'])
def update_user_permissions():

    try:
        # Retrieve all active users
        users = User.query.filter(
            User.user_persona != "VOID"
        ).all()

        for user in users:

            # Each dropdown has a unique name based on member_id
            form_field = f"role_{user.member_id}"

            if form_field in request.form:

                new_persona = request.form.get(form_field)

                # Validate submitted role
                if new_persona not in VALID_PERSONAS:
                    raise ValueError("Invalid permission selected.")

                # Update only if the role changed
                if user.user_persona != new_persona:
                    user.user_persona = new_persona

        db.session.commit()

    except Exception:
        db.session.rollback()
        raise

    return redirect(url_for('user_permissions'))


@app.route('/delete-user/<int:member_id>', methods=['POST'])
def delete_user(member_id):

    user = db.session.get(User, member_id)

    if user is None:
        return "User not found.", 404

    if user.user_persona == "VOID":
        return "User is already inactive.", 400

    # Soft delete: preserve the database record
    user.user_persona = "VOID"
    user.active_status = False

    db.session.commit()

    return redirect(url_for('user_permissions'))


# GAME SCHEDULE ROUTES

@app.route('/record-game')
# @login_required
# @role_required(['EXECUTIVE', 'TREASURER', 'ADVISOR'])
def record_game():
    return render_template('record-game.html')

@app.route('/game-schedule-after-login')
# @login_required
# @role_required(['EXECUTIVE', 'TREASURER', 'ADVISOR'])
def game_schedule_after_login():
    games = Game.query.order_by(Game.game_date).all()
    return render_template('game-schedule-after-login.html', games=games)

@app.route('/game-schedule-create', methods=['GET', 'POST'])
# @login_required
# @role_required(['EXECUTIVE', 'TREASURER', 'ADVISOR'])
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

        flash('Game created successfully!', 'success')

        return redirect('/game-schedule-after-login')

    return render_template('game-schedule-create.html')

@app.route('/game-schedule-update/<int:game_id>', methods=['GET', 'POST'])
# @login_required
# @role_required(['EXECUTIVE', 'TREASURER', 'ADVISOR'])
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
# @login_required
# @role_required(['EXECUTIVE', 'TREASURER', 'ADVISOR'])
def game_schedule_delete(game_id):
    game = db.get_or_404(Game, game_id)
    db.session.delete(game)
    db.session.commit()
    flash('Game deleted successfully!', 'success')
    return redirect(url_for('game_schedule_after_login'))


if __name__ == '__main__':
    app.run(port=5001, debug=True)
