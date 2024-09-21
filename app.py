
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import matplotlib
import seaborn as sns
from matplotlib import pyplot as plt
matplotlib.use('Agg')
from flask import send_file
import pandas as pd
from fpdf import FPDF
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, DateField, TelField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Regexp
from flask_wtf.csrf import CSRFProtect
from wtforms.validators import DataRequired

app = Flask(__name__)

# SQLite configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quality.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set secret key for session management (using a simple string for now)
app.secret_key = 'your_random_secret_key_here'  # Replace with a proper key for production
csrf = CSRFProtect(app)  # Initialize CSRF protection

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Auto-incrementing ID
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    mobile_number = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

# Define Inspection model
class Inspection(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Auto-incrementing ID
    vehicle_type = db.Column(db.String(100), nullable=False)
    chassis_number = db.Column(db.String(100), nullable=False)
    engine_number = db.Column(db.String(100), nullable=False)
    body_condition = db.Column(db.String(255), nullable=False)
    glass_mirrors_condition = db.Column(db.String(255), nullable=False)
    indicators_lights_condition = db.Column(db.String(255), nullable=False)
    tires_wheels_condition = db.Column(db.String(255), nullable=False)
    engine_condition = db.Column(db.String(255), nullable=False)
    transmission_gearbox_condition = db.Column(db.String(255), nullable=False)
    suspension_steering_condition = db.Column(db.String(255), nullable=False)
    braking_system_condition = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False)
    inspected_at = db.Column(db.DateTime, default=db.func.now())

# Create database tables
with app.app_context():
    db.create_all()

def create_bar_chart(data):
    # Handle NaN values
    data = {k: (v if pd.notna(v) else 0) for k, v in data.items()}
    df = pd.DataFrame(list(data.items()), columns=['Status', 'Count'])

    plt.figure(figsize=(10, 6))
    sns.barplot(x='Status', y='Count', data=df, palette='tab10')

    plt.title('Inspection Status Overview')
    plt.xlabel('Status')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('static/bar_chart.png')
    plt.clf()  # Clear the current figure

def create_pie_chart(data):
    # Handle NaN values
    data = {k: (v if pd.notna(v) else 0) for k, v in data.items()}

    if sum(data.values()) == 0:
        print("Warning: All values are zero in today's counts.")
        data = {'No Data': 1}

    plt.figure(figsize=(8, 8))
    plt.pie(data.values(), labels=data.keys(), autopct='%1.1f%%', startangle=90)
    plt.axis('equal')  # Equal aspect ratio
    plt.title('Today\'s Inspection Status')
    plt.savefig('static/pie_chart.png')
    plt.clf()  # Clear the current figure



class InspectionForm(FlaskForm):
    vehicle_type = SelectField('Vehicle Type', validators=[DataRequired()], choices=[
        ('', 'Select'),
        ('Trucks', 'Trucks'),
        ('Cars', 'Cars'),
        ('EV Cars', 'EV Cars'),
        ('Buses', 'Buses'),
        ('EV Buses', 'EV Buses'),
    ])
    chassis_number = StringField('Chassis Number', validators=[DataRequired()])
    engine_number = StringField('Engine Number', validators=[DataRequired()])
    body_condition = SelectField('Body Condition', validators=[DataRequired()], choices=[
        ('', 'Select Condition'),
        ('Good', 'Good'),
        ('Average', 'Average'),
        ('Poor', 'Poor'),
        ('Missing', 'Missing'),
    ])
    glass_mirrors_condition = SelectField('Glass & Mirrors Condition', validators=[DataRequired()], choices=[
        ('', 'Select Condition'),
        ('Good', 'Good'),
        ('Average', 'Average'),
        ('Poor', 'Poor'),
        ('Missing', 'Missing'),
    ])
    indicators_lights_condition = SelectField('Indicators & Lights Condition', validators=[DataRequired()], choices=[
        ('', 'Select Condition'),
        ('Good', 'Good'),
        ('Average', 'Average'),
        ('Poor', 'Poor'),
        ('Missing', 'Missing'),
    ])
    tires_wheels_condition = SelectField('Tires & Wheels Condition', validators=[DataRequired()], choices=[
        ('', 'Select Condition'),
        ('Good', 'Good'),
        ('Average', 'Average'),
        ('Poor', 'Poor'),
        ('Missing', 'Missing'),
    ])
    engine_condition = SelectField('Engine Condition', validators=[DataRequired()], choices=[
        ('', 'Select Condition'),
        ('Good', 'Good'),
        ('Average', 'Average'),
        ('Poor', 'Poor'),
        ('Missing', 'Missing'),
    ])
    transmission_gearbox_condition = SelectField('Transmission & Gearbox Condition', validators=[DataRequired()], choices=[
        ('', 'Select Condition'),
        ('Good', 'Good'),
        ('Average', 'Average'),
        ('Poor', 'Poor'),
        ('Missing', 'Missing'),
    ])
    suspension_steering_condition = SelectField('Suspension & Steering Condition', validators=[DataRequired()], choices=[
        ('', 'Select Condition'),
        ('Good', 'Good'),
        ('Average', 'Average'),
        ('Poor', 'Poor'),
        ('Missing', 'Missing'),
    ])
    braking_system_condition = SelectField('Braking System Condition', validators=[DataRequired()], choices=[
        ('', 'Select Condition'),
        ('Good', 'Good'),
        ('Average', 'Average'),
        ('Poor', 'Poor'),
        ('Missing', 'Missing'),
    ])
    description = TextAreaField('Description')
    status = SelectField('Status', choices=[('Approved', 'Approved'), ('Rejected', 'Rejected')], validators=[DataRequired()])


#registration form
class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    dob = DateField('Date Of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    mobile = TelField('Mobile No', validators=[DataRequired(), Regexp(r'^\d{10}$', message="Mobile number must be 10 digits.")])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register')

# Decorator to require login for certain routes
from functools import wraps
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/')
def login():
    form = LoginForm()
    return render_template('login.html', form=form)

@app.route('/login', methods=['POST'])
def do_login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Fetch user from the database
        user = User.query.filter_by(email=email).first()  
        if user and user.password == password:  # Directly check password (not recommended for production)
            session['user_id'] = user.id  # Store user ID in session
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html', form=form)



@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Retrieve all inspections for the current date
    inspections_today = Inspection.query.filter(
        db.func.date(Inspection.inspected_at) == db.func.current_date()
    ).all()

    # Retrieve all inspections for overall data
    inspections_all = Inspection.query.all()

    # Prepare a list of inspections to match the expected format in the HTML
    inspection_list = []
    for inspection in inspections_today:
        inspection_list.append([
            len(inspection_list) + 1,  # SNO
            inspection.vehicle_type,
            inspection.chassis_number,
            inspection.engine_number,
            inspection.body_condition,
            inspection.glass_mirrors_condition,
            inspection.indicators_lights_condition,
            inspection.tires_wheels_condition,
            inspection.engine_condition,
            inspection.transmission_gearbox_condition,
            inspection.suspension_steering_condition,
            inspection.braking_system_condition,
            inspection.description,
            inspection.inspected_at.strftime('%Y-%m-%d %H:%M:%S')  # Format date
        ])

    # Prepare data for charts
    approval_counts = {'Approved': 0, 'Rejected': 0}
    today_counts = {'Approved': 0, 'Rejected': 0}   

    # Updated: Check if status exists before incrementing
    for inspection in inspections_all:
        if inspection.status in approval_counts:
            approval_counts[inspection.status] += 1
        else:
            print(f"Unexpected status in overall data: {inspection.status}")  # Debugging output

    # Updated: Check if status exists before incrementing
    for inspection in inspections_today:
        if inspection.status in today_counts:
            today_counts[inspection.status] += 1
        else:
            print(f"Unexpected status in today's data: {inspection.status}")  # Debugging output

    # Debugging output
    print("Approval Counts:", approval_counts)
    print("Today's Counts:", today_counts)

    # Create charts
    create_bar_chart(approval_counts)  # Create bar chart for overall data
    create_pie_chart(today_counts)     # Create pie chart for today's data  

    return render_template('dashboard.html', inspections=inspection_list)


@app.route('/download/csv')
@login_required
def download_csv():
    inspections_today = Inspection.query.filter(db.func.date(Inspection.inspected_at) == db.func.current_date()).all()

    # Convert inspection data to a DataFrame
    data = [{
        'Vehicle Type': inspection.vehicle_type,
        'Chassis Number': inspection.chassis_number,
        'Engine Number': inspection.engine_number,
        'Body Condition': inspection.body_condition,
        'Glass & Mirrors': inspection.glass_mirrors_condition,
        'Indicators & Lights': inspection.indicators_lights_condition,
        'Tires & Wheels': inspection.tires_wheels_condition,
        'Engine Condition': inspection.engine_condition,
        'Transmission & Gearbox': inspection.transmission_gearbox_condition,
        'Suspension & Steering': inspection.suspension_steering_condition,
        'Braking System': inspection.braking_system_condition,
        'Description': inspection.description,
        'Inspection Date': inspection.inspected_at.strftime('%Y-%m-%d %H:%M:%S')
    } for inspection in inspections_today]

    df = pd.DataFrame(data)
    csv_file = 'inspections_today.csv'
    df.to_csv(csv_file, index=False)

    return send_file(csv_file, as_attachment=True)

@app.route('/download/pdf')
@login_required
def download_pdf():
    inspections_today = Inspection.query.filter(db.func.date(Inspection.inspected_at) == db.func.current_date()).all()

    pdf = FPDF()
    pdf.add_page('L')  # Use landscape orientation for better fit
    pdf.set_font("Arial", size=10)

    pdf.cell(0, 10, txt="Inspections Today", ln=True, align='C')

    # Define column widths
    column_widths = [25, 30, 30, 25, 25, 30, 30, 30, 30, 30, 25, 25]

    # Add table header
    headers = [
        "Vehicle Type", "Chassis Number", "Engine Number", "Body Condition",
        "Glass & Indicators", "Tires & Wheel", "Engine Condition",
        "Transmission & Gearbox", "Suspension & Steering",
        "Braking System", "Description", "Inspection Date"
    ]
    
    for header, width in zip(headers, column_widths):
        pdf.cell(width, 10, header, 1)
    pdf.ln()

    # Add inspection data
    for inspection in inspections_today:
        pdf.cell(column_widths[0], 10, inspection.vehicle_type, 1)
        pdf.cell(column_widths[1], 10, inspection.chassis_number, 1)
        pdf.cell(column_widths[2], 10, inspection.engine_number, 1)
        pdf.cell(column_widths[3], 10, inspection.body_condition, 1)
        pdf.cell(column_widths[4], 10, inspection.glass_mirrors_condition, 1)
        pdf.cell(column_widths[5], 10, inspection.indicators_lights_condition, 1)
        pdf.cell(column_widths[6], 10, inspection.tires_wheels_condition, 1)
        pdf.cell(column_widths[7], 10, inspection.engine_condition, 1)
        pdf.cell(column_widths[8], 10, inspection.transmission_gearbox_condition, 1)
        pdf.cell(column_widths[9], 10, inspection.suspension_steering_condition, 1)
        pdf.cell(column_widths[10], 10, inspection.braking_system_condition, 1)
        pdf.cell(column_widths[11], 10, inspection.description, 1)
        pdf.cell(column_widths[11], 10, inspection.inspected_at.strftime('%Y-%m-%d'), 1)
        pdf.ln()

    pdf_file = 'inspections_today.pdf'
    pdf.output(pdf_file)

    return send_file(pdf_file, as_attachment=True)



@app.route('/inspect', methods=['GET', 'POST'])
@login_required
def inspect():
    form = InspectionForm()  # Create an instance of the form
    if form.validate_on_submit(): 
        # Determine the status based on the button clicked
        action = request.form.get('action')
        if action == 'approve':
            status = 'Approved'
        elif action == 'reject':
            status = 'Rejected' # Check if form is submitted and valid
        # Create the inspection object
        inspection = Inspection(
            vehicle_type=form.vehicle_type.data,
            chassis_number=form.chassis_number.data,
            engine_number=form.engine_number.data,
            body_condition=form.body_condition.data,
            glass_mirrors_condition=form.glass_mirrors_condition.data,
            indicators_lights_condition=form.indicators_lights_condition.data,
            tires_wheels_condition=form.tires_wheels_condition.data,
            engine_condition=form.engine_condition.data,
            transmission_gearbox_condition=form.transmission_gearbox_condition.data,
            suspension_steering_condition=form.suspension_steering_condition.data,
            braking_system_condition=form.braking_system_condition.data,
            description=form.description.data,
            status=status
        )
        
        # Debugging: Print the inspection data to check what's being submitted
        print("Inspection Data:", inspection.__dict__)

        # Add to session and commit
        db.session.add(inspection)
        db.session.commit()
        flash('Inspection recorded successfully!', 'success')
        return redirect(url_for('dashboard'))
    else:
        # Debugging: Print form errors if validation fails
        print("Form Errors:", form.errors)

    return render_template('inspect.html', form=form)  # Pass the form to the template



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()  # Initialize your registration form

    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data
            name = form.name.data
            dob = form.dob.data
            mobile = form.mobile.data
            password = form.password.data

            # Check if the user already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Email already exists. Please choose a different one.', 'danger')
                return render_template('register.html', form=form)

            # Create a new user
            new_user = User(email=email, name=name, date_of_birth=dob, mobile_number=mobile, password=password)
            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('register.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
