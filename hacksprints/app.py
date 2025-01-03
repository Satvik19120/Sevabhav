from flask import Flask, render_template, request, redirect, url_for
from models import db, User, Medicine, Message, AssistanceRequest

app = Flask(__name__)
app.config['SECRET_KEY'] = 'h@cksprint@123#'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hacksprint.db'
app.app_context().push()
db.init_app(app)
print("----your application started----")


# Home Page
@app.route("/")
def home():
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)
