from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
from datetime import datetime
import os
import pytz

app = Flask(__name__)

# Files for storage
CSV_FILE = 'ledger.csv'
EXCEL_FILE = 'ledger.xlsx'

# Initialize files if not exists
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=['Datetime', 'Credit From', 'Credit Amount', 'Debit To', 'Debit Amount', 'Remaining Amount'])
    df.to_csv(CSV_FILE, index=False)

if not os.path.exists(EXCEL_FILE):
    df = pd.DataFrame(columns=['Datetime', 'Credit From', 'Credit Amount', 'Debit To', 'Debit Amount', 'Remaining Amount'])
    df.to_excel(EXCEL_FILE, index=False)

def get_indian_time():
    return datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_entries', methods=['GET'])
def get_entries():
    df = pd.read_csv(CSV_FILE)
    df = df.fillna('')  # Convert NaN values to empty strings for cleaner JSON
    entries = df.to_dict(orient='records')
    return jsonify(entries)

@app.route('/add_entry', methods=['POST'])
def add_entry():
    try:
        data = request.json
        data['Datetime'] = get_indian_time()
        
        credit_amount = float(data.get('Credit Amount', 0)) if data.get('Credit Amount') not in ['', None] else 0
        debit_amount = float(data.get('Debit Amount', 0)) if data.get('Debit Amount') not in ['', None] else 0
        
        df = pd.read_csv(CSV_FILE)
        previous_remaining = df['Remaining Amount'].iloc[-1] if len(df) > 0 else 0
        remaining_amount = previous_remaining + credit_amount - debit_amount
        data['Remaining Amount'] = remaining_amount
        
        new_entry = pd.DataFrame([data])
        df = pd.concat([df, new_entry], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        df.to_excel(EXCEL_FILE, index=False)
        
        return jsonify({"success": True, "message": "Entry added successfully!", "data": data})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error adding entry: {str(e)}"}), 400

@app.route('/delete_entry', methods=['POST'])
def delete_entry():
    try:
        index = int(request.json['index'])
        df = pd.read_csv(CSV_FILE)
        
        if index < 0 or index >= len(df):
            return jsonify({"success": False, "message": "Invalid index"}), 400
        
        deleted_entry = df.iloc[index].to_dict()
        df = df.drop(index).reset_index(drop=True)
        
        if len(df) > 0:
            df['Remaining Amount'] = df['Credit Amount'].cumsum() - df['Debit Amount'].cumsum()
        
        df.to_csv(CSV_FILE, index=False)
        df.to_excel(EXCEL_FILE, index=False)
        
        return jsonify({"success": True, "message": "Entry deleted successfully!", "data": deleted_entry})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error deleting entry: {str(e)}"}), 400

@app.route('/undo_entry', methods=['POST'])
def undo_entry():
    try:
        df = pd.read_csv(CSV_FILE)
        if len(df) == 0:
            return jsonify({"success": False, "message": "No entries to undo"}), 400
        
        last_entry = df.iloc[-1].to_dict()
        df = df[:-1]
        
        if len(df) > 0:
            df['Remaining Amount'] = df['Credit Amount'].cumsum() - df['Debit Amount'].cumsum()
        
        df.to_csv(CSV_FILE, index=False)
        df.to_excel(EXCEL_FILE, index=False)
        
        return jsonify({"success": True, "message": "Last entry undone successfully!", "data": last_entry})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error undoing entry: {str(e)}"}), 400

@app.route('/delete_all_entries', methods=['POST'])
def delete_all_entries():
    try:
        df = pd.DataFrame(columns=['Datetime', 'Credit From', 'Credit Amount', 'Debit To', 'Debit Amount', 'Remaining Amount'])
        df.to_csv(CSV_FILE, index=False)
        df.to_excel(EXCEL_FILE, index=False)
        return jsonify({"success": True, "message": "All entries deleted successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error deleting all entries: {str(e)}"}), 400

@app.route('/download/csv', methods=['GET'])
def download_csv():
    return send_file(CSV_FILE, as_attachment=True)

@app.route('/download/excel', methods=['GET'])
def download_excel():
    return send_file(EXCEL_FILE, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)