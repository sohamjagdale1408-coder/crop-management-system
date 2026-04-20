import os
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models import db, User, Crop, Log

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-scms'
basedir = os.path.abspath(os.path.dirname(__name__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'scms.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def get_expected_harvest(sowing_date, duration_days):
    return sowing_date + timedelta(days=duration_days)

def initialize_database():
    with app.app_context():
        db.create_all()

@app.route('/')
@login_required
def dashboard():
    crops = Crop.query.filter_by(user_id=current_user.id).all()
    
    total_investment = 0
    crop_data = []
    
    for crop in crops:
        # Calculate Expected Harvest
        expected_harvest = get_expected_harvest(crop.sowing_date, crop.growth_duration_days)
        
        # Calculate Total Cost for this crop
        logs = Log.query.filter_by(crop_id=crop.id).all()
        crop_cost = sum(log.cost for log in logs)
        total_investment += crop_cost
        
        # Determine Status
        today = datetime.utcnow().date()
        status = "Ready" if today >= expected_harvest else "Growing"
        
        crop_data.append({
            'crop': crop,
            'expected_harvest': expected_harvest,
            'total_cost': crop_cost,
            'status': status
        })
        
    return render_template('dashboard.html', crops=crop_data, total_investment=total_investment)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Simple validation
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or Email already exists.', 'danger')
            return redirect(url_for('signup'))
            
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! You can now log in.', 'success')
        return redirect(url_for('login'))
        
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/add_crop', methods=['GET', 'POST'])
@login_required
def add_crop():
    if request.method == 'POST':
        crop_name = request.form.get('crop_name')
        sowing_date_str = request.form.get('sowing_date')
        duration = request.form.get('growth_duration_days')
        
        if not crop_name or not sowing_date_str or not duration:
            flash('All fields are required!', 'danger')
            return redirect(url_for('add_crop'))
            
        sowing_date = datetime.strptime(sowing_date_str, '%Y-%m-%d').date()
        
        new_crop = Crop(
            user_id=current_user.id,
            crop_name=crop_name,
            sowing_date=sowing_date,
            growth_duration_days=int(duration)
        )
        db.session.add(new_crop)
        db.session.commit()
        flash('Crop added successfully!', 'success')
        return redirect(url_for('dashboard'))
        
    return render_template('add_crop.html')

@app.route('/crop/<int:crop_id>', methods=['GET', 'POST'])
@login_required
def crop_details(crop_id):
    crop = Crop.query.get_or_404(crop_id)
    if crop.user_id != current_user.id:
        flash('You do not have permission to view this crop.', 'danger')
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        log_type = request.form.get('log_type')
        quantity = request.form.get('quantity_workers')
        cost = request.form.get('cost')
        log_date_str = request.form.get('date')
        
        log_date = datetime.strptime(log_date_str, '%Y-%m-%d').date() if log_date_str else datetime.utcnow().date()
        
        new_log = Log(
            crop_id=crop.id,
            log_type=log_type,
            quantity_workers=quantity,
            cost=float(cost),
            date=log_date
        )
        db.session.add(new_log)
        db.session.commit()
        flash('Log added successfully!', 'success')
        return redirect(url_for('crop_details', crop_id=crop.id))
        
    logs = Log.query.filter_by(crop_id=crop.id).order_by(Log.date.desc()).all()
    expected_harvest = get_expected_harvest(crop.sowing_date, crop.growth_duration_days)
    total_cost = sum(log.cost for log in logs)
    
    return render_template('crop_details.html', crop=crop, logs=logs, expected_harvest=expected_harvest, total_cost=total_cost)

if __name__ == '__main__':
    initialize_database()
    app.run(debug=True)
