from flask import Flask, request, jsonify, render_template

from storage import get_conn, init_db, edgar_summary, stocktwits_summary

app = Flask(__name__)

# if just loading up the page
@app.route("/")
def index():
    return render_template("stockSearcher.html")

# if ticker is entered as search
@app.route("/ticker_given")
def summary():
    ticker = request.args.get("ticker", "").strip().upper()

    if not ticker:
        return jsonify ({"error": "missing ticker"}), 400
    
    with get_conn() as conn:
        edgar = edgar_summary(conn, ticker)
        stocktwits = stocktwits_summary(conn, ticker)

    return jsonify ({"ticker": ticker, "edgar": edgar, "stocktwits": stocktwits})

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=8080)
