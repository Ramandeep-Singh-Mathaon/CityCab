from flask import Flask, render_template, request, redirect, url_for, flash, Blueprint, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import inspect, text
from functools import wraps
import os
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')

# Resolve the SQLite database to an absolute path inside the instance folder.
# A relative "sqlite:///citycab.db" depends on the current working directory and
# can trigger "unable to open database file" / "disk I/O error" when the app is
# launched from a different folder or the instance dir is missing.
basedir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(basedir, 'instance')
os.makedirs(instance_dir, exist_ok=True)
# Use forward slashes: SQLAlchemy's sqlite:/// URLs require them, and on Windows
# os.path.join would otherwise produce backslashes and a malformed database URL.
db_path = os.path.join(instance_dir, 'citycab.db').replace('\\', '/')
default_db = 'sqlite:///' + db_path
db_url = os.getenv('DATABASE_URL', default_db)
if db_url in ('sqlite:///citycab.db', 'sqlite:///instance/citycab.db'):
    db_url = default_db
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB file size limit
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# ────────── MODELS ──────────
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20))
    avatar = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship('Booking', backref='passenger', foreign_keys='Booking.user_id', lazy=True)
    driven_bookings = db.relationship('Booking', backref='driver', foreign_keys='Booking.driver_id', lazy=True)
    is_driver = db.Column(db.Boolean, default=False)

    def get_id(self): return str(self.id)
    @property
    def is_authenticated(self): return True
    @property
    def is_active(self): return True
    @property
    def is_anonymous(self): return False

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ride_type = db.Column(db.String(10), nullable=False)  # 'normal' or 'future'
    customer_name = db.Column(db.String(80), nullable=False)
    pickup = db.Column(db.String(255), nullable=False)
    drop = db.Column(db.String(255), nullable=False)
    distance_km = db.Column(db.Float, nullable=False)
    duration_min = db.Column(db.Float, nullable=False)
    fare = db.Column(db.Integer, nullable=False)
    scheduled_time = db.Column(db.DateTime)  # Only for future rides
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    driver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    status = db.Column(db.String(20), default='pending')
    

# ────────── LOGIN MANAGER ──────────
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ────────── HELPER FUNCTIONS ──────────
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def initialize_database():
    with app.app_context():
        # Create all tables 
        db.create_all()
        
        # Check and add missing columns for user table
        inspector = inspect(db.engine)
        try:
            # User table columns
            user_columns = [col['name'] for col in inspector.get_columns('user')]
            
            if 'phone' not in user_columns:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE user ADD COLUMN phone VARCHAR(20)"))
                    print("✓ Added phone column to user table")
            
            if 'avatar' not in user_columns:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE user ADD COLUMN avatar VARCHAR(255)"))
                    print("✓ Added avatar column to user table")
            
            if 'created_at' not in user_columns:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE user ADD COLUMN created_at DATETIME"))
                    print("✓ Added created_at column to user table")
            
            # Booking table columns
            booking_columns = [col['name'] for col in inspector.get_columns('booking')]
            
            if 'ride_type' not in booking_columns:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE booking ADD COLUMN ride_type VARCHAR(10)"))
                    print("✓ Added ride_type column to booking table")
            
            if 'scheduled_time' not in booking_columns:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE booking ADD COLUMN scheduled_time DATETIME"))
                    print("✓ Added scheduled_time column to booking table")
            
            # Driver-related columns
            if 'is_driver' not in user_columns: 
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE user ADD COLUMN is_driver BOOLEAN DEFAULT FALSE"))
                    print("✓ Added is_driver column to user table")
            
            if 'driver_id' not in booking_columns:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE booking ADD COLUMN driver_id INTEGER REFERENCES user(id)"))
                    print("✓ Added driver_id column to booking table")
            
            if 'status' not in booking_columns:
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE booking ADD COLUMN status VARCHAR(20) DEFAULT 'pending'"))
                    print("✓ Added status column to booking table")
                    
        except Exception as e:
            print(f"Database initialization error: {e}")
# ────────── ROUTES ──────────

@app.route('/driver')
@login_required
def driver_dashboard():
    if not current_user.is_driver:
        abort(403)
    return render_template('driver_dashboard.html')

@app.route('/driver/rides')
@login_required
def available_rides():
    if not current_user.is_driver:
        abort(403)
        
    rides = Booking.query.filter_by(driver_id=None).all()
    return jsonify([{
        'id': ride.id,
        'pickup': ride.pickup,
        'drop': ride.drop,
        'fare': ride.fare,
        'distance': f"{ride.distance_km:.1f} km",
        'duration': f"{ride.duration_min:.0f} mins",
        'customer': ride.customer_name
    } for ride in rides])

@app.route('/driver/rides/<int:ride_id>/accept', methods=['POST'])
@login_required
def accept_ride(ride_id):
    if not current_user.is_driver:
        abort(403)
        
    ride = Booking.query.get_or_404(ride_id)
    if ride.driver_id:
        return jsonify({'error': 'Ride already accepted'}), 400
        
    ride.driver_id = current_user.id
    ride.status = 'accepted'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Ride accepted successfully'
    })

# Update the booking route to include driver info
@app.route('/rides', methods=['GET', 'POST'])
@login_required
def rides():
    if request.method == 'POST':
        try:
            ride_id = int(request.form.get('ride_id', 0))
            ride = Booking.query.get_or_404(ride_id)
            if ride.user_id == current_user.id:
                ride.status = 'Cancelled'
                db.session.commit()
                flash('Ride cancelled successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error cancelling ride: {str(e)}', 'danger')
        
        return redirect(url_for('rides'))
    
    # For drivers, show rides they've accepted
    if current_user.is_driver:
        rides = Booking.query.filter_by(driver_id=current_user.id)\
                   .order_by(Booking.timestamp.desc())\
                   .all()
    # For regular users, show their own rides
    else:
        rides = Booking.query.filter_by(user_id=current_user.id)\
                   .order_by(Booking.timestamp.desc())\
                   .all()
                   
    return render_template('rides.html', rides=rides)

# Update the book route to set initial status
@app.route('/book', methods=['GET', 'POST'])
@login_required
def book():
    if request.method == 'POST':
        try:
            booking = Booking(
                user_id=current_user.id,
                ride_type='normal',
                customer_name=request.form.get('name', '').strip(),
                pickup=request.form.get('pickup', '').strip(),
                drop=request.form.get('drop', '').strip(),
                distance_km=float(request.form.get('distance_km', 0)),
                duration_min=float(request.form.get('duration_min', 0)),
                fare=int(request.form.get('fare', 0)),
                status='pending'
            )
            db.session.add(booking)
            db.session.commit()
            flash('✅ Your booking is confirmed!', 'success')
            return '', 204
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating booking: {str(e)}', 'danger')
    
    return render_template('book.html', user=current_user)

@app.route('/')
def index():
    return redirect(url_for('book'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not all([name, email, password]):
            flash('All fields are required', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'danger')
            return redirect(url_for('register'))
        
        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('book'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash(f'Welcome back, {user.name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('book'))
        flash('Invalid credentials. Please try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'warning')
    return redirect(url_for('login'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            current_user.name = request.form.get('name', current_user.name).strip()
            current_user.phone = request.form.get('phone', current_user.phone).strip()
            
            # Handle avatar upload
            if 'avatar' in request.files:
                avatar_file = request.files['avatar']
                if avatar_file and avatar_file.filename != '':
                    # Validate file
                    if not allowed_file(avatar_file.filename):
                        return jsonify({
                            'success': False,
                            'message': 'Invalid file type. Only PNG, JPG, JPEG, GIF allowed.'
                        }), 400
                    
                    # Delete old avatar if exists
                    if current_user.avatar:
                        old_path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.avatar)
                        if os.path.exists(old_path):
                            try:
                                os.remove(old_path)
                            except Exception as e:
                                print(f"Error deleting old avatar: {e}")
                    
                    # Save new avatar
                    filename = secure_filename(avatar_file.filename)
                    unique_filename = f"{uuid.uuid4().hex}_{filename}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    
                    # Create directory if it doesn't exist
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    avatar_file.save(filepath)
                    
                    current_user.avatar = unique_filename
            
            db.session.commit()
            
            # Return the avatar URL in the response
            avatar_url = url_for('static', filename=f'uploads/{current_user.avatar}', _external=True) if current_user.avatar else None
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully',
                'avatarUrl': avatar_url
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                'success': False,
                'message': f'Error updating profile: {str(e)}'
            }), 500
    
    # For GET requests, pass the avatar URL to the template
    avatar_url = url_for('static', filename=f'uploads/{current_user.avatar}') if current_user.avatar else None
    return render_template('profile.html', user=current_user)

@app.route('/profile/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'message': 'Invalid request data'}), 400
        
    old_password = data.get('old_password', '').strip()
    new_password = data.get('new_password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()
    
    if not all([old_password, new_password, confirm_password]):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    
    if not check_password_hash(current_user.password, old_password):
        return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400
    
    if new_password != confirm_password:
        return jsonify({'success': False, 'message': 'New passwords do not match'}), 400
    
    if len(new_password) < 8:
        return jsonify({'success': False, 'message': 'Password must be at least 8 characters'}), 400
    
    try:
        current_user.password = generate_password_hash(new_password)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Password changed successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    

@app.route('/future', methods=['GET', 'POST'])
@login_required
def future():
    if request.method == 'POST':
        try:
            # Validate required fields
            if not all([request.form.get('name'), 
                       request.form.get('pickup'),
                       request.form.get('drop'),
                       request.form.get('date'),
                       request.form.get('time')]):
                flash('Please fill all required fields', 'danger')
                return redirect(url_for('future'))

            # Create the booking with status='pending'
            booking = Booking(
                user_id=current_user.id,
                ride_type='future',
                customer_name=request.form.get('name', '').strip(),
                pickup=request.form.get('pickup', '').strip(),
                drop=request.form.get('drop', '').strip(),
                distance_km=float(request.form.get('distance_km', 0)),
                duration_min=float(request.form.get('duration_min', 0)),
                fare=int(request.form.get('fare', 0)),
                scheduled_time=datetime.strptime(
                    f"{request.form.get('date', '')} {request.form.get('time', '')}",
                    "%Y-%m-%d %H:%M"
                ),
                status='pending'  # Explicitly setting status
            )
            
            db.session.add(booking)
            db.session.commit()
            flash('✅ Your future ride has been scheduled!', 'success')
            return redirect(url_for('rides'))
            
        except ValueError as e:
            db.session.rollback()
            flash(f'Invalid input: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error scheduling ride: {str(e)}', 'danger')
    
    return render_template('future_book.html', user=current_user)



# ────────── ADMIN BLUEPRINT ──────────
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return view(*args, **kwargs)
    return wrapped

@admin_bp.route('/')
@admin_required
def admin_table():
    bookings = Booking.query.order_by(Booking.timestamp.desc()).all()
    return render_template('admin.html', bookings=bookings)

app.register_blueprint(admin_bp)

# ────────── ERROR HANDLERS ──────────
@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', error="403 - Forbidden"), 403

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="404 - Page Not Found"), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('error.html', error="500 - Internal Server Error"), 500

# Initialize database on startup
initialize_database()

if __name__ == '__main__':
    # Debug mode is opt-in via the environment so it is never on by default in
    # a deployed setting (the Werkzeug debugger allows arbitrary code execution).
    debug = os.getenv('FLASK_DEBUG', '0').lower() in ('1', 'true', 'yes')
    app.run(debug=debug)