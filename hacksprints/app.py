from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, Medicine, Message, AssistanceRequest
from datetime import datetime

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
        flash('Please log in to access your dashboard.', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if user.role == 'Doctor':
        return redirect(url_for('doctor_dashboard'))
    elif user.role == 'MR':
        return redirect(url_for('mr_dashboard'))
    elif user.role == 'Patient':
        return redirect(url_for('patient_dashboard'))
    else:
        flash('Invalid user role.', 'error')
        return redirect(url_for('login'))


@app.route('/doctor_dashboard')
def doctor_dashboard():
    if 'user_id' not in session or User.query.get(session['user_id']).role != 'Doctor':
        flash('Access denied. Doctors only.', 'error')
        return redirect(url_for('login'))
    
    # Example: Fetch medicines and messages for the doctor
    user = User.query.get(session['user_id'])
    messages = user.messages_received
    medicines = Medicine.query.all()

    return render_template('doctor_dashboard.html', user=user, messages=messages, medicines=medicines)


@app.route('/mr_dashboard')
def mr_dashboard():
    if 'user_id' not in session or User.query.get(session['user_id']).role != 'MR':
        flash('Access denied. MRs only.', 'error')
        return redirect(url_for('login'))
    
    # Example: Fetch messages sent by the MR and medicine stock details
    user = User.query.get(session['user_id'])
    messages = user.messages_sent
    medicines = Medicine.query.all()

    return render_template('mr_dashboard.html', user=user, messages=messages, medicines=medicines)


@app.route('/patient_dashboard', methods=['GET'])
def patient_dashboard():
    if 'user_id' not in session:
        flash('Please log in.', 'error')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if user.role != 'Patient':
        flash('Access denied. Only patients can access this dashboard.', 'error')
        return redirect(url_for('dashboard'))

    # Fetch all assistance requests for the logged-in patient
    assistance_requests = AssistanceRequest.query.filter_by(patient_name=user.name).all()

    return render_template('patient_dashboard.html', assistance_requests=assistance_requests)



@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# Send a message
@app.route('/send_message', methods=['GET', 'POST'])
def send_message():
    if 'user_id' not in session:
        flash('Please log in to send messages.', 'error')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        recipient_id = request.form.get('recipient_id')
        content = request.form.get('content')

        if not recipient_id or not content:
            flash('All fields are required.', 'error')
            return redirect(url_for('send_message'))

        recipient = User.query.get(recipient_id)
        if not recipient:
            flash('Recipient not found.', 'error')
            return redirect(url_for('send_message'))

        # Create and save the message
        message = Message(sender_id=user.id, recipient_id=recipient.id, content=content, timestamp=datetime.utcnow())
        db.session.add(message)
        db.session.commit()

        flash('Message sent successfully!', 'success')
        return redirect(url_for('dashboard'))

    # Fetch potential recipients
    recipients = User.query.filter(User.id != user.id and User.role!=user.role).all()
    return render_template('send_message.html', user=user, recipients=recipients)

# View received messages
@app.route('/received_messages')
def received_messages():
    if 'user_id' not in session:
        flash('Please log in to view messages.', 'error')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    messages = user.messages_received

    return render_template('received_messages.html', user=user, messages=messages)

# View all medicines
@app.route('/medicines')
def view_medicines():
    if 'user_id' not in session:
        flash('Please log in to view medicines.', 'error')
        return redirect(url_for('login'))

    medicines = Medicine.query.all()
    return render_template('medicines.html', medicines=medicines)

# Add medicine (for MR)
@app.route('/add_medicine', methods=['GET', 'POST'])
def add_medicine():
    if 'user_id' not in session:
        flash('Please log in.', 'error')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if user.role != 'MR':
        flash('Access denied. Only MRs can add medicines.', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        stock = request.form.get('stock')
        price = request.form.get('price')
        alternative = request.form.get('alternative')
        
        if not name or not stock or not price:
            flash('Name, stock, and price are required.', 'error')
            return redirect(url_for('add_medicine'))
        
        # Save medicine
        medicine = Medicine(name=name, stock=int(stock), price=float(price), alternative=alternative)
        db.session.add(medicine)
        db.session.commit()
        
        flash('Medicine added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_medicine.html')




#Patient Assistance System
@app.route('/create_assistance_request', methods=['GET', 'POST'])
def create_assistance_request():
    if 'user_id' not in session:
        flash('Please log in.', 'error')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if user.role != 'Doctor':
        flash('Access denied. Only Doctors can create assistance requests.', 'error')
        return redirect(url_for('dashboard'))

    medicines = Medicine.query.all()  # Fetch all available medicines
    patients=User.query.all()
    if request.method == 'POST':
        patient_name = request.form.get('patient_name')
        medicine_id = request.form.get('medicine_id')
        reason = request.form.get('reason')

        if not patient_name or not medicine_id:
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('create_assistance_request'))

        assistance_request = AssistanceRequest(
            patient_name=patient_name,
            doctor_id=user.id,
            medicine_id=medicine_id,
            reason=reason,
            status='Pending'
        )
        db.session.add(assistance_request)
        db.session.commit()

        flash('Patient Assistance Request created successfully!', 'success')
        return redirect(url_for('doctor_dashboard'))

    return render_template('create_assistance_request.html', medicines=medicines,patients=patients)

#Route for MRs to view and accept/reject request
@app.route('/view_assistance_requests', methods=['GET', 'POST'])
def view_assistance_requests():
    if 'user_id' not in session:
        flash('Please log in.', 'error')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if user.role != 'MR':
        flash('Access denied. Only MRs can view assistance requests.', 'error')
        return redirect(url_for('dashboard'))

    requests = AssistanceRequest.query.filter_by(status='Pending').all()  # Fetch all pending requests

    if request.method == 'POST':
        request_id = request.form.get('request_id')
        action = request.form.get('action')

        assistance_request = AssistanceRequest.query.get(request_id)
        if action == 'approve':
            assistance_request.status = 'Approved'
        elif action == 'reject':
            assistance_request.status = 'Rejected'
        
        db.session.commit()
        flash(f'Request {action}ed successfully!', 'success')
        return redirect(url_for('view_assistance_requests'))

    return render_template('view_assistance_requests.html', requests=requests)







if __name__ == "__main__":
    app.run(debug=True)
