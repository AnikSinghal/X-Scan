from flask import Flask, render_template, request, redirect, flash, url_for
from sqlalchemy import create_engine, Column, String, Integer, LargeBinary, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import tensorflow as tf
from werkzeug.security import generate_password_hash, check_password_hash
from mailer import send_email

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Define SQLAlchemy base

# Define User class
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    uName = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password = Column(String(100), nullable=False)  # Increase column length for hashed passwords

    def __init__(self, uName, email, password):
        self.uName = uName
        self.email = email
        self.password = password

# Define Report class
class Report(Base):
    __tablename__ = 'reports'
    rid = Column(Integer, primary_key=True)
    xrayimg = Column(LargeBinary)
    link = Column(String)
    date = Column(Date, default=datetime.now)

    def __init__(self, xrayimg, link):
        self.xrayimg = xrayimg
        self.link = link

# Create engine and session for users
engine_users = create_engine("sqlite:///users.db", echo=True)
Base.metadata.create_all(bind=engine_users)
SessionUsers = sessionmaker(bind=engine_users)
session_users = SessionUsers()

# Create engine and session for reports
engine_reports = create_engine("sqlite:///reports.db", echo=True)
Base.metadata.create_all(bind=engine_reports)
SessionReports = sessionmaker(bind=engine_reports)
session_reports = SessionReports()

# Load the model from the .h5 file
model = tf.keras.models.load_model('model.h5')

# Function to store image
def store_image(image_file, link):
    image_data = image_file.read()
    new_image = Report(xrayimg=image_data, link=link)
    session_reports.add(new_image)
    session_reports.commit()

# Function to make predictions
def make_prediction(image_file):
    try:
        prediction = model.predict(image_file)
        return prediction
    except Exception as e:
        app.logger.error(f"Error making prediction: {e}")
        return None

# Home route
@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        user = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('pass')
        confirm_password = request.form.get('cnfPass')

        if password == confirm_password:
            # Hash the password before storing
            hashed_password = generate_password_hash(password)

            try:
                person = User(user, email, hashed_password)
                session_users.add(person)
                session_users.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except IntegrityError:
                session_users.rollback()
                flash('User Already Registered', 'danger')
        else:
            flash('Password and Confirm Password do not match', 'danger')

    return render_template('register.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('login-email')
        password = request.form.get('login-pass')

        user = session_users.query(User).filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Successful Login', 'success')
                return redirect(url_for('dashboard', mail=email))
            else:
                flash('Wrong Password', 'danger')
        else:
            flash('User not found', 'danger')

    return render_template('login.html')

# Dashboard route
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    mail = request.args.get('mail')
    if mail is None:
        return redirect(url_for('login'))

    if request.method == 'POST':
        img_file = request.files['ximage']
        if img_file:
            try:
                prediction = make_prediction(img_file)
                if prediction is not None:
                    # Generate a unique filename for the image
                    filename = f"{mail}_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
                    link = f"https://example.com/reports/{filename}"
                    store_image(img_file, link)
                    flash('Image uploaded successfully!', 'success')

                    report = "https://yash-agarwal-03.github.io/pneuomonia_-ve/"
                    if prediction:
                        report = "https://yash-agarwal-03.github.io/pneumonia_postve/"

                    report_content = f"""
<p>You can see your XRAY report <a href="{report}">here</a></p>
"""
                    send_email(report_content, img_file)
                    return redirect(url_for('report', prediction=prediction))
            except Exception as e:
                flash(f'Error uploading image: {str(e)}', 'danger')
        else:
            flash('No image selected!', 'danger')

    # Fetch existing reports for the user
    user_reports = session_reports.query(Report).filter_by(link=f"https://example.com/reports/{mail}").all()
    return render_template('dashboard.html', reports=user_reports)

@app.route('/report', methods=['GET'])
def report():
    prediction = request.args.get('prediction')
    return render_template("report.html", data=prediction)

if __name__ == '__main__':
    app.run(debug=True)