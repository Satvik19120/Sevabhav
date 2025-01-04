from flask import Flask, render_template, request, redirect, url_for, flash, session
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


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        role = request.form['role']
        password = request.form['password']
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in.', 'error')
            return redirect(url_for('register'))
        
        # Create a new user
        new_user = User(name=name, email=email, role=role, password=password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            # Log the user in
            session['user_id'] = user.id
            session['user_name'] = user.name
            session['user_role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', user_name=session['user_name'], user_role=session['user_role'])

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))





if __name__ == "__main__":
    app.run(debug=True)
