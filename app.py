from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'secret123'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# -------- DATABASE MODELS -------- #

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    role = db.Column(db.String(10))

class Admission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    age = db.Column(db.Integer)
    class_name = db.Column(db.String(50))
    parent_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    message = db.Column(db.String(500))

# -------- ROUTES -------- #

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/academics')
def academics():
    return render_template('academics.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')


# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            username=request.form['username'],
            password=request.form['password']
        ).first()

        if user:
            session['user'] = user.username
            session['role'] = user.role

            if user.role == 'admin':
                return redirect('/admin')
            else:
                return redirect('/admission')
        else:
            flash('Invalid login')

    return render_template('login.html')

# REGISTER
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        # Check if user exists
        if User.query.filter_by(username=username).first():
            flash("Username already exists!")
            return redirect('/register')

        user = User(username=username, password=password, role='student')
        db.session.add(user)
        db.session.commit()

        flash("Registered successfully!")
        return redirect('/login')

    return render_template('register.html')

# ADMISSION FORM
@app.route('/admission', methods=['GET', 'POST'])
def admission():

    if not session.get('user'):
        flash("Please login first to fill admission form")
        return redirect('/login')

    if request.method == 'POST':
        data = Admission(
            name=request.form['name'],
            age=request.form['age'],
            class_name=request.form['class'],
            parent_name=request.form['parent'],
            phone=request.form['phone']
        )
        db.session.add(data)
        db.session.commit()
        flash('Form submitted successfully')

    return render_template('admission.html')

# ADMIN DASHBOARD
@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return redirect('/login')

    admissions = Admission.query.all()
    messages = Contact.query.all()

    return render_template('admin_dashboard.html', data=admissions, messages=messages)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/contact', methods=['GET','POST'])
def contact():
    if request.method == 'POST':

        data = Contact(
            name=request.form['name'],
            email=request.form['email'],
            message=request.form['message']
        )

        db.session.add(data)
        db.session.commit()

        flash("Message stored successfully!")

    return render_template('contact.html')

@app.route('/delete/<int:id>')
def delete(id):
    if session.get('role') != 'admin':
        return redirect('/login')

    data = Admission.query.get(id)
    db.session.delete(data)
    db.session.commit()

    return redirect('/admin')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        # Create default admin
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password='admin123', role='admin')
            db.session.add(admin)
            db.session.commit()

    app.run(debug=True)