from flask import Flask, render_template, request, redirect, url_for, session, flash
import pickle
import numpy as np
import bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
from flask_mysqldb import MySQL
import pandas as pd

# Initialize Flask app
app = Flask(__name__)

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'login_sample_db'
app.secret_key = 'your_secret_key_here'

mysql = MySQL(app)

# Load the pickled files for book recommendation system
# Make sure these files are correct and the paths are valid
try:
    popular_df = pd.read_pickle(r'popular.pkl')
    pt = pd.read_pickle(r'pt.pkl')
    books = pd.read_pickle(r'books.pkl')
    similarity_scores = pickle.load(open(r'similarity_scores.pkl', 'rb'))
except Exception as e:
    print(f"Error loading pickle files: {e}")
    raise

# FlaskForm class for registration
class RegisterForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users where email=%s", (field.data,))
        user = cursor.fetchone()
        cursor.close()
        if user:
            raise ValidationError('Email Already Taken')

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

# Home route - Check if user is logged in or not
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('book_Recommendation'))
    else:
        return redirect(url_for('login_index'))

# Login/Registration Index - First index for login and registration
@app.route('/login_index')
def login_index():
    return render_template('login_index.html')  # This is the index for login and registration

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Store user data in the database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users(name, email, password) VALUES (%s, %s, %s)", (name, email, hashed_password))
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Verify user credentials
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()
        cursor.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['user_id'] = user[0]
            return redirect(url_for('book_Recommendation'))
        else:
            flash("Login failed. Please check your email and password.")
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

# Dashboard route - only accessible if logged in
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        user_id = session['user_id']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            return render_template('dashboard.html', user=user)
    return redirect(url_for('login'))

# Book Recommendation System Index - Second index for logged-in users
@app.route('/book_Recommendation')
def book_Recommendation():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values))

# Book recommendation page for specific book recommendation
@app.route('/recommend')
def recommend_ui():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_input = request.form.get('user_input')

    # Check if the user input exists in the pivot table index
    if user_input in pt.index:
        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:11]
        data = []
        for i in similar_items:
            item = []
            # Ensure `books` is a DataFrame and `pt.index[i[0]]` is valid
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates("Book-Title")['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
            data.append(item)

        return render_template('recommend.html', data=data)
    else:
        return render_template('recommend.html', data=[], message="Book not found. Please try another title.")

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out successfully.")
    return redirect(url_for('login_index'))

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
