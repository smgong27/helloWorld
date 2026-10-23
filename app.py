from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/log-in', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return redirect(url_for('financial_ledger'))
    return render_template('login.html')

@app.route('/financial-ledger', methods=['GET'])
def financial_ledger():
    return render_template('financial-ledger.html')

@app.route('/record-transaction', methods=['GET', 'POST'])
def record_transaction():
    if request.method == 'POST':
        return redirect(url_for('financial_ledger'))
    return render_template('record-transaction.html')

@app.route('/upload-transactions', methods=['GET', 'POST'])
def upload_transactions():
    if request.method == 'POST':
        return redirect(url_for('financial_ledger'))
    return render_template('upload-transactions.html')

if __name__ == '__main__':
    app.run(debug=True)