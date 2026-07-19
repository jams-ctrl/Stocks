from flask import Flask, request, jsonify, render_template

from storage import get_conn, init_db, edgar_summary, stocktwits_summary, news_summary

from company_name_converter import get_other_names

import sys
import os

# go up one parent folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from model.prediction import predict_latest

app = Flask(__name__)

# if just loading up the page
@app.route("/")
def index():
    return render_template("stockSearcher.html")

# if ticker is entered as search
@app.route("/company_given")
def summary():
    company = request.args.get("company", "").strip().lower()
    if len(company) == 4:
        if (get_other_names(company.upper()) is not None):
            ticker = company.upper()
        else:
            return jsonify ({"error": "company not in database"}), 400
    else:
        result = get_other_names(company.capitalize())
        if result is None:
            return jsonify({"error": "company not in database"}), 400
        i, ticker, j = result
        if ticker is None:
            return jsonify({"error": "company not in database"}), 400

    with get_conn() as conn:
        edgar = edgar_summary(conn, ticker)
        stocktwits = stocktwits_summary(conn, ticker)
        news = news_summary(conn, ticker)
        prediction, probability = predict_latest(ticker)
        bot = {"prediction": prediction, "probability": probability}

    return jsonify ({"ticker": ticker, "edgar": edgar, "stocktwits": stocktwits, "news": news, "bot": bot})

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=8080)
