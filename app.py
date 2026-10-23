from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# ==============================================================================
# ----------------------------- FAKE DATA START --------------------------------
# ==============================================================================
# The datasets below simulate the database tables shown on your ERD:
# - GAME: gameID, gameOpponent, gameDate, gameLocation, teamID
# - BANK_ACCOUNT: accountID, accountName
# - EXPENSE / REVENUE: combined for display in the financial ledger
# ==============================================================================

# Fake Game Schedule Data (simulating the GAME table)
MOCK_GAMES = [
    {"game_id": "G-201", "opponent": "Towson University", "date": "09/13/2026", "location": "Home"},
    {"game_id": "G-202", "opponent": "Delaware Blue Hens", "date": "09/19/2026", "location": "Away"},
    {"game_id": "G-203", "opponent": "Navy Club Softball", "date": "09/20/2026", "location": "Home"},
    {"game_id": "G-204", "opponent": "Penn State Club", "date": "09/27/2026", "location": "Away"},
    {"game_id": "G-205", "opponent": "Georgetown Hoyas", "date": "10/03/2026", "location": "Home"},
    {"game_id": "G-206", "opponent": "Virginia Cavaliers", "date": "10/10/2026", "location": "Away"},
    {"game_id": "G-207", "opponent": "Rutgers Scarlet Knights", "date": "10/17/2026", "location": "Away"},
    {"game_id": "G-208", "opponent": "UMBC Retrievers", "date": "10/24/2026", "location": "Home"}
]

# 20 Fake Transactions (simulating the EXPENSE and REVENUE tables)
TRANSACTIONS = [
    {
        "id": "E105",
        "date": "2026-09-24",
        "display_date": "09/24/2026",
        "game_id": "G-204",
        "account": "SGA",
        "team": "NCSA",
        "description": "Mid-Atlantic Fall Tournament entry fee",
        "type": "Game/Tournament Fees",
        "category": "Expense",
        "location": "College Park, MD",
        "amount": 450.00,
        "receipt": "View"
    },
    {
        "id": "R104",
        "date": "2026-09-20",
        "display_date": "09/20/2026",
        "game_id": "—",
        "account": "SECU",
        "team": "Active",
        "description": "Active Team Fall Member dues deposit",
        "type": "Dues",
        "category": "Revenue",
        "location": "Online",
        "amount": 1200.00,
        "receipt": None
    },
    {
        "id": "R103",
        "date": "2026-09-15",
        "display_date": "09/15/2026",
        "game_id": "G-201",
        "account": "RecWell",
        "team": "NCSA",
        "description": "Home doubleheader concessions revenue",
        "type": "Fundraising",
        "category": "Revenue",
        "location": "College Park, MD",
        "amount": 800.00,
        "receipt": "View"
    },
    {
        "id": "E100",
        "date": "2026-09-02",
        "display_date": "09/02/2026",
        "game_id": "—",
        "account": "SGA",
        "team": "Active",
        "description": "Under Armour team jerseys and custom gear",
        "type": "Equipment",
        "category": "Expense",
        "location": "Baltimore, MD",
        "amount": 680.00,
        "receipt": "View"
    },
    {
        "id": "E106",
        "date": "2026-09-18",
        "display_date": "09/18/2026",
        "game_id": "G-202",
        "account": "SECU",
        "team": "NCSA",
        "description": "Delaware travel van fuel & tolls",
        "type": "Gas",
        "category": "Expense",
        "location": "Newark, DE",
        "amount": 114.50,
        "receipt": "View"
    },
    {
        "id": "E107",
        "date": "2026-09-19",
        "display_date": "09/19/2026",
        "game_id": "G-202",
        "account": "RecWell",
        "team": "NCSA",
        "description": "Post-game team meal at Panera",
        "type": "Food",
        "category": "Expense",
        "location": "Wilmington, DE",
        "amount": 195.40,
        "receipt": "View"
    },
    {
        "id": "R108",
        "date": "2026-09-22",
        "display_date": "09/22/2026",
        "game_id": "—",
        "account": "Foundation",
        "team": "NCSA",
        "description": "Alumni booster club tax-deductible gift",
        "type": "Donation",
        "category": "Revenue",
        "location": "College Park, MD",
        "amount": 1500.00,
        "receipt": "View"
    },
    {
        "id": "E109",
        "date": "2026-09-26",
        "display_date": "09/26/2026",
        "game_id": "G-204",
        "account": "SECU",
        "team": "NCSA",
        "description": "Penn State trip Hampton Inn (4 rooms)",
        "type": "Hotel",
        "category": "Expense",
        "location": "State College, PA",
        "amount": 780.00,
        "receipt": "View"
    },
    {
        "id": "E110",
        "date": "2026-09-27",
        "display_date": "09/27/2026",
        "game_id": "G-204",
        "account": "SECU",
        "team": "NCSA",
        "description": "Charter passenger van rental balance",
        "type": "Travel",
        "category": "Expense",
        "location": "State College, PA",
        "amount": 340.00,
        "receipt": "View"
    },
    {
        "id": "R111",
        "date": "2026-10-01",
        "display_date": "10/01/2026",
        "game_id": "—",
        "account": "SECU",
        "team": "NCSA",
        "description": "Fall season roster dues batch #2",
        "type": "Dues",
        "category": "Revenue",
        "location": "Online",
        "amount": 950.00,
        "receipt": None
    },
    {
        "id": "E112",
        "date": "2026-10-02",
        "display_date": "10/02/2026",
        "game_id": "G-205",
        "account": "SGA",
        "team": "NCSA",
        "description": "Umpires and field line prep fees",
        "type": "Game/Tournament Fees",
        "category": "Expense",
        "location": "College Park, MD",
        "amount": 220.00,
        "receipt": "View"
    },
    {
        "id": "R113",
        "date": "2026-10-05",
        "display_date": "10/05/2026",
        "game_id": "—",
        "account": "SECU",
        "team": "Active",
        "description": "Chipotle community fundraiser night check",
        "type": "Fundraising",
        "category": "Revenue",
        "location": "Route 1 Chipotle",
        "amount": 420.75,
        "receipt": "View"
    },
    {
        "id": "E114",
        "date": "2026-10-08",
        "display_date": "10/08/2026",
        "game_id": "—",
        "account": "RecWell",
        "team": "Active",
        "description": "Dudley Thunder optic yellow softballs (3 doz)",
        "type": "Equipment",
        "category": "Expense",
        "location": "College Park, MD",
        "amount": 185.00,
        "receipt": "View"
    },
    {
        "id": "E115",
        "date": "2026-10-09",
        "display_date": "10/09/2026",
        "game_id": "G-206",
        "account": "SECU",
        "team": "NCSA",
        "description": "Charlottesville team gas fill-up",
        "type": "Gas",
        "category": "Expense",
        "location": "Charlottesville, VA",
        "amount": 88.60,
        "receipt": "View"
    },
    {
        "id": "E116",
        "date": "2026-10-10",
        "display_date": "10/10/2026",
        "game_id": "G-206",
        "account": "SECU",
        "team": "NCSA",
        "description": "Pre-game subway subs & energy drinks",
        "type": "Food",
        "category": "Expense",
        "location": "Charlottesville, VA",
        "amount": 142.30,
        "receipt": "View"
    },
    {
        "id": "R117",
        "date": "2026-10-12",
        "display_date": "10/12/2026",
        "game_id": "—",
        "account": "Foundation",
        "team": "Active",
        "description": "Softball parent association fall contribution",
        "type": "Donation",
        "category": "Revenue",
        "location": "College Park, MD",
        "amount": 600.00,
        "receipt": "View"
    },
    {
        "id": "E118",
        "date": "2026-10-14",
        "display_date": "10/14/2026",
        "game_id": "—",
        "account": "SGA",
        "team": "NCSA",
        "description": "Emergency field medical kit & ice packs",
        "type": "Other",
        "category": "Expense",
        "location": "Silver Spring, MD",
        "amount": 65.00,
        "receipt": "View"
    },
    {
        "id": "E119",
        "date": "2026-10-16",
        "display_date": "10/16/2026",
        "game_id": "G-207",
        "account": "SECU",
        "team": "NCSA",
        "description": "New Jersey turnpike tolls & turnpike fuel",
        "type": "Gas",
        "category": "Expense",
        "location": "New Brunswick, NJ",
        "amount": 128.90,
        "receipt": "View"
    },
    {
        "id": "R120",
        "date": "2026-10-18",
        "display_date": "10/18/2026",
        "game_id": "—",
        "account": "SECU",
        "team": "Active",
        "description": "Club apparel snap store order profit margin",
        "type": "Fundraising",
        "category": "Revenue",
        "location": "Online",
        "amount": 510.00,
        "receipt": "View"
    },
    {
        "id": "E121",
        "date": "2026-10-21",
        "display_date": "10/21/2026",
        "game_id": "G-208",
        "account": "SGA",
        "team": "NCSA",
        "description": "Softball umpire association officiating invoice",
        "type": "Game/Tournament Fees",
        "category": "Expense",
        "location": "College Park, MD",
        "amount": 210.00,
        "receipt": "View"
    }
]

# Supported granular transaction classifications
TRANSACTION_TYPES = [
    "Travel",
    "Hotel",
    "Food",
    "Fundraising",
    "Dues",
    "Other",
    "Game/Tournament Fees",
    "Gas",
    "Equipment",
    "Donation"
]


# ==============================================================================
# ------------------------------ FAKE DATA END ---------------------------------
# ==============================================================================


@app.route('/')
def home():
    return redirect(url_for('login'))


# 1. Log-in Route
@app.route('/log-in', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('financial_ledger'))
    return render_template('login.html')


# 2. Financial Ledger Route
@app.route('/financial-ledger', methods=['GET'])
def financial_ledger():
    filter_type = request.args.get('filter', 'all').lower()

    if filter_type == 'revenue':
        filtered = [t for t in TRANSACTIONS if t['category'].lower() == 'revenue']
    elif filter_type == 'expense':
        filtered = [t for t in TRANSACTIONS if t['category'].lower() == 'expense']
    elif filter_type != 'all':
        filtered = [t for t in TRANSACTIONS if t['type'].lower() == filter_type]
    else:
        filtered = TRANSACTIONS

    return render_template(
        'financial-ledger.html',
        transactions=filtered,
        current_filter=filter_type,
        transaction_types=TRANSACTION_TYPES
    )


# 3. Record Transaction Route (Create & Edit)
@app.route('/record-transaction', methods=['GET', 'POST'])
def record_transaction():
    trans_id = request.args.get('id')
    existing_txn = next((t for t in TRANSACTIONS if t['id'] == trans_id), None)

    if request.method == 'POST':
        action = request.form.get('action')

        # Handle Deletion
        if action == 'delete' and trans_id:
            global TRANSACTIONS
            TRANSACTIONS = [t for t in TRANSACTIONS if t['id'] != trans_id]
            return redirect(url_for('financial_ledger'))

        # Read form inputs
        t_date = request.form.get('transaction_date', '')
        bank_acc = request.form.get('bank_account', 'SGA')
        team_alloc = request.form.get('team_allocation', 'Active')
        txn_type = request.form.get('transaction_type', 'Other')
        amount_val = float(request.form.get('amount', 0.0) or 0.0)
        game_id_val = request.form.get('game_id', '').strip() or '—'
        desc_val = request.form.get('description', '')

        # Classify as Revenue or Expense according to ERD table structure
        if txn_type in ["Dues", "Fundraising", "Donation"]:
            category_tag = "Revenue"
        else:
            category_tag = "Expense"

        # Format display date MM/DD/YYYY
        display_d = t_date
        if t_date and '-' in t_date:
            parts = t_date.split('-')
            display_d = f"{parts[1]}/{parts[2]}/{parts[0]}"

        if existing_txn:
            existing_txn.update({
                "date": t_date,
                "display_date": display_d,
                "game_id": game_id_val,
                "account": bank_acc,
                "team": team_alloc,
                "description": desc_val,
                "type": txn_type,
                "category": category_tag,
                "amount": amount_val
            })
        else:
            prefix = "R" if category_tag == "Revenue" else "E"
            new_id = f"{prefix}{len(TRANSACTIONS) + 105}"
            TRANSACTIONS.insert(0, {
                "id": new_id,
                "date": t_date,
                "display_date": display_d,
                "game_id": game_id_val,
                "account": bank_acc,
                "team": team_alloc,
                "description": desc_val,
                "type": txn_type,
                "category": category_tag,
                "location": "College Park, MD",
                "amount": amount_val,
                "receipt": "View" if category_tag == "Expense" else None
            })
        return redirect(url_for('financial_ledger'))

    return render_template(
        'record-transaction.html',
        txn=existing_txn,
        games=MOCK_GAMES,
        transaction_types=TRANSACTION_TYPES
    )


# 4. Upload Transactions Route
@app.route('/upload-transactions', methods=['GET', 'POST'])
def upload_transactions():
    if request.method == 'POST':
        # Simulates statement scraping by importing newly discovered entries into the ledger
        new_batch = [
            {
                "id": f"E{len(TRANSACTIONS) + 122}",
                "date": "2026-10-22",
                "display_date": "10/22/2026",
                "game_id": "—",
                "account": "SECU",
                "team": "NCSA",
                "description": "Statement scrape: Wawa tournament team snacks",
                "type": "Food",
                "category": "Expense",
                "location": "College Park, MD",
                "amount": 78.40,
                "receipt": "View"
            },
            {
                "id": f"R{len(TRANSACTIONS) + 123}",
                "date": "2026-10-22",
                "display_date": "10/22/2026",
                "game_id": "—",
                "account": "RecWell",
                "team": "Active",
                "description": "Statement scrape: RecWell allocation transfer",
                "type": "Other",
                "category": "Revenue",
                "location": "College Park, MD",
                "amount": 450.00,
                "receipt": None
            }
        ]
        for b in new_batch:
            TRANSACTIONS.insert(0, b)
        return redirect(url_for('financial_ledger'))

    return render_template('upload-transactions.html')


if __name__ == '__main__':
    app.run(debug=True)