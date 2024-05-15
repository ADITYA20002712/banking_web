from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use a more secure key in production

# Configure the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define a User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    balance = db.Column(db.Float, nullable=False, default=0.0)  # Add balance attribute

    def __repr__(self):
        return f"<User {self.username}>"

# Define routes for the application
@app.route('/')
def home():
    if 'user' in session:
        user = User.query.get(session['user'])
        return render_template('home.html', username=user.username, balance=user.balance)
    else:
        return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose another.', 'error')
            return redirect(url_for('signup'))

        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        # Create a new user and add to the database
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user'] = user.id
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))

        flash('Invalid credentials. Please try again.', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/credit', methods=['POST'])
def credit():
    if 'user' in session:
        amount = float(request.form['amount'])
        user = User.query.get(session['user'])
        user.balance += amount
        db.session.commit()
        flash(f'Credited {amount} successfully!', 'success')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))

@app.route('/debit', methods=['POST'])
def debit():
    if 'user' in session:
        amount = float(request.form['amount'])
        user = User.query.get(session['user'])
        if user.balance >= amount:
            user.balance -= amount
            db.session.commit()
            flash(f'Debited {amount} successfully!', 'success')
        else:
            flash('Insufficient balance.', 'error')
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print(app.url_map)
    app.run(debug=True)
