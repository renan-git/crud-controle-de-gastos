import datetime
import os

from dotenv import load_dotenv
from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, Float, Date, desc

app = Flask(__name__)

load_dotenv("D:\EnvironmentVariables\.env")

class Base(DeclarativeBase):
    pass

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("sqlite")
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Expense(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    date: Mapped[datetime.date] = mapped_column(Date(), nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False)

with app.app_context():
    db.create_all()

def string_to_date(date):
    date_datetime = datetime.datetime.strptime(date, "%Y-%m-%d")
    return date_datetime

@app.route("/")
def all_expenses():
    result = db.session.execute(db.select(Expense).where(Expense.deleted == False).order_by(desc(Expense.date)))
    all_expenses = result.scalars()
    return render_template("home.html", expenses=all_expenses)

@app.route("/add", methods = ["POST", "GET"])
def add_expense():
    if request.method == "POST":
        new_expense = Expense(
            description = request.form["description"],
            value = request.form["value"],
            date = string_to_date(request.form["date"]),
            deleted = False
        )
        db.session.add(new_expense)
        db.session.commit()
        return redirect(url_for("all_expenses"))
    return render_template("add.html")

@app.route("/edit", methods= ["POST", "GET"])
def edit_expense():
    if request.method == "POST":
        expense_id = int(request.form["id"])
        expense_to_update = db.session.execute(db.select(Expense).where(Expense.id == expense_id)).scalar()
        expense_to_update.description = request.form["description"]
        expense_to_update.value = request.form["value"]
        expense_to_update.date = string_to_date(request.form["date"])
        db.session.commit()
        return redirect(url_for("all_expenses"))
    expense_id = int(request.args.get("id"))
    expense_selected = db.session.execute(db.select(Expense).where(Expense.id == expense_id)).scalar()
    return render_template("edit.html", expense=expense_selected)

@app.route("/delete")
def delete_expense():
    expense_id = int(request.args.get("id"))
    expense_selected = db.session.execute(db.select(Expense).where(Expense.id == expense_id)).scalar()
    expense_selected.deleted = True
    db.session.commit()
    return redirect(url_for("all_expenses"))

if __name__ == "__main__":
    app.run(debug=True)
