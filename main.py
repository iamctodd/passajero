from flask import Flask, render_template, request, url_for, redirect, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import login_user, LoginManager, login_required, current_user, logout_user
from models import *
from random import choice, randint, shuffle
import os
import datetime as dt
import cryptocode
import errors

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
CRYPTO_KEY = os.getenv('CRYPTO_KEY')
app.config.from_pyfile('settings.py')

# CONNECT TO DB
login_manager = LoginManager()
login_manager.init_app(app)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

db.init_app(app)   

def get_all_entries():
    result = db.session.execute(db.select(Entry))
    all_entries = result.scalars().all()
    return all_entries

def get_user_entries(user):
    result = db.session.execute(db.select(Entry).where(Entry.user_id == user))
    user_entries = result.scalars().all()
    for i in user_entries:
        i.site_password = decrypt_password_entry(i.site_password)
    return user_entries

@app.route('/account', methods=["GET", "POST"])
@login_required
def account():
    return render_template('account.html')

@app.route('/reset', methods=["GET", "POST"])
def forgot_password():
    return render_template('recover.html')

@app.route("/delete/<int:entry_id>")
@login_required
def delete_entry(entry_id):
    entry_to_delete = db.get_or_404(Entry, entry_id)
    db.session.delete(entry_to_delete)
    db.session.commit()
    return redirect(url_for('main'))

@app.route('/', methods=["GET", "POST"])
def home():
    error = None
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if not user:
            flash('Email not found')
            render_template ("index.html", error=error)
        elif not check_password_hash(user.password, password):
            flash('Incorrect password')
            render_template ("index.html", error=error)
        else:
             login_user(user)
             return redirect(url_for('main', current_user=current_user))
    return render_template("index.html")

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        name = request.form.get("name")
        password = request.form.get("password")
        hashed = generate_password_hash(password, salt_length=16)   
        new_user = User(email=email, name=name, password=hashed)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('add_new_entry', current_user=new_user))
    return render_template("register.html")


@app.route('/main')
@login_required
def main():
    if current_user.is_active and current_user.is_authenticated:
        entries = get_user_entries(current_user.id)
    else:
        return redirect('/404')
    return render_template("main.html", all_entries=entries, current_user=current_user)


@app.route('/edit/<int:entry_id>', methods=["GET", "POST"])
@login_required
def edit(entry_id):
    if current_user.is_active and current_user.is_authenticated:
        if request.method == "POST":
            result = db.session.execute(db.select(Entry).where(Entry.id == entry_id))
            entry_to_edit = result.scalar()       
            entry_to_edit.site = request.form["entry_url"]
            entry_to_edit.site_username = request.form["entry_username"]
            entry_to_edit.site_password = encrypt_password_entry(request.form["entry_password"])
            entry_to_edit.last_updated = datetime.now()
            db.session.commit()
            return redirect(url_for('main'))
        entry_to_edit = db.get_or_404(Entry, entry_id)
        entry_to_edit.site_password = decrypt_password_entry(entry_to_edit.site_password)
        return render_template("edit.html", entry=entry_to_edit)
    else:
        return redirect('/404')
    
@app.route('/import/', methods=["GET", "POST"])
@login_required
def import_entries():
    if current_user.is_active and current_user.is_authenticated:
        message = None
        if request.method == 'POST':
            file = request.files['file']
            if file.filename == '':
                return 'No selected file', 400
            if file and not allowed_file(file.filename):
                return 'File type not allowed', 400 
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            import_contents(os.path.join(UPLOAD_FOLDER, filename))
            return redirect(url_for('main', error=message))
        return render_template("import.html")
    else:
        return redirect('/404')

def import_contents(filename):
    import csv
    imported_list = []
    with open(filename) as file:
        csv_file = csv.reader(file)
        for row in csv_file:
            imported_list.append(row)
            site = row[0]
            username = row[1]
            password = encrypt_password_entry(row[2])
            new_entry = Entry(site_username=username, site=site, site_password=password, current_user=current_user)
            db.session.add(new_entry)
            db.session.commit() 
    return imported_list

@app.route("/logout")
@login_required
def logout():
    error = None
    logout_user()
    flash('You are logged out')
    return redirect(url_for('home', error=error))


@app.route('/new', methods=["GET", "POST"])
@login_required
def add_new_entry():
    if request.method == "POST":
        site = request.form.get("entry_url")
        username = request.form.get("entry_username")
        password = encrypt_password_entry(request.form.get("entry_password"))        
        new_entry = Entry(site_username=username, site=site, site_password=password, current_user=current_user)
        db.session.add(new_entry)
        db.session.commit()
        return redirect(url_for('main'))
    if current_user.is_active and current_user.is_authenticated:
        new_password = generate_password()
        return render_template("new.html", password=new_password)
    else:
        return redirect('/404')

def encrypt_password_entry(entry_pw):
    encrypted_password = cryptocode.encrypt(entry_pw, CRYPTO_KEY)
    return encrypted_password

def decrypt_password_entry(entry_pw):
    decrypted_password = cryptocode.decrypt(entry_pw, CRYPTO_KEY)
    return decrypted_password

# ---------------------------- PASSWORD GENERATOR ------------------------------- #

#Password Generator Project
def generate_password():
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

    password_letters = [choice(letters) for _ in range(randint(12, 18))]
    password_symbols = [choice(symbols) for _ in range(randint(4, 8))]
    password_numbers = [choice(numbers) for _ in range(randint(4, 8))]

    password_list = password_letters + password_symbols + password_numbers
    shuffle(password_list)
    password = "".join(password_list)
    #pyperclip.copy(password)
    return password 

# ---------------------------- START APP ------------------------------- #
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)