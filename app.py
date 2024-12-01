from flask import Flask, render_template, request, redirect, url_for, session, flash
import pickle
import numpy as np
import bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, ValidationError
from flask_mysqldb import MySQL
import pandas as pd
import csv


# Initialize Flask app
app = Flask(__name__)


books_df = pd.read_csv('books.csv') 



Book_file = "Books.csv"

users_df = pd.read_csv('Users.csv', low_memory=False)
users_file="Users.csv"

def load_books():
    return pd.read_csv(
        Book_file,
        dtype={
            "ISBN": str,
            "Book-Title": str,
            "Book-Author": str,
            "Year-Of-Publication": str,  # Treat as string to avoid type issues
            "Publisher": str,
            "Image-URL-S": str,
            "Image-URL-M": str,
            "Image-URL-L": str,
        }
    )

def save_books(df):
    df.to_csv(Book_file, index=False)

users_file="Users.csv"
def load_users():
    return pd.read_csv(
        users_file,
        dtype={
            "User-ID": str,
            "Location": str,
            "Age": str,
        }
    )
def save_users(df):
    df.to_csv(users_file, index=False)

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
        location = request.form.get('location')
        age = request.form.get('age')

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Store user data in the database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users(name, email, password, location, age) VALUES (%s, %s, %s, %s, %s)",(name, email, hashed_password, location, age))
                       
        mysql.connection.commit()
        cursor.close()

        # Append data to Users.csv
        try:
            with open('Users.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([name, location, age])
        except Exception as e:
            flash(f"Error writing to Users.csv: {e}", "danger")

        flash("Registration successful! Please log in.", "success")
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

        if user and bcrypt.checkpw(password.encode('utf-8'), user[5].encode('utf-8')):
            session['user_id'] = user[0]
            return redirect(url_for('book_Recommendation'))
        else:
            flash("Login failed. Please check your email and password.")
            return redirect(url_for('login'))

    return render_template('login.html', form=form)

#admin Login    
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        # Verify admin credentials
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM admin WHERE email=%s", (email,))
        admin = cursor.fetchone()
        cursor.close()

        if admin and password == admin[2]:
            session['user_id'] = admin[0]
            return redirect(url_for('admin_page'))
        else:
            flash("Login failed. Please check your email and password.")
            return redirect(url_for('login'))

    return render_template('admin_login.html', form=form)


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

#admin Page
@app.route('/admin_page')
def admin_page():
     cursor = mysql.connection.cursor()
     # Query to fetch data
     cursor.execute("SELECT * FROM users")
     data = cursor.fetchall()
     cursor.close()

     return render_template('admin/admin_dashboard.html',data=data)
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
                           rating=list(popular_df['avg_rating'].values),
                           )

# Book recommendation page for specific book recommendation
@app.route('/recommend')
def recommend_ui():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('recommend.html')
#recommend_similar Books
# @app.route('/recommend_books', methods=['POST'])
# def recommend():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     user_input = request.form.get('user_input')

#     # Check if the user input exists in the pivot table index
#     if user_input in pt.index:
#         index = np.where(pt.index == user_input)[0][0]
#         similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:11]
#         data = []
#         for i in similar_items:
#             item = []
#             # Ensure books is a DataFrame and pt.index[i[0]] is valid
#             temp_df = books[books['Book-Title'] == pt.index[i[0]]]
#             item.extend(list(temp_df.drop_duplicates("Book-Title")['Book-Title'].values))
#             item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
#             item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
#             data.append(item)

#         return render_template('recommend.html', data=data)
#     else:
#         return render_template('recommend.html', data=[], message="Book not found. Please try another title.")

@app.route('/recommend_books', methods=['POST'])
def recommend():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_input = request.form.get('user_input')

    if user_input in pt.index:
        index = np.where(pt.index == user_input)[0][0]
        similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:11]
        data = []
        for i in similar_items:
            item = []
            temp_df = books[books['Book-Title'] == pt.index[i[0]]]
            item.extend(list(temp_df.drop_duplicates("Book-Title")['Book-Title'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
            item.extend(list(temp_df.drop_duplicates('Book-Title')['ISBN'].values))  # ISBN added here
            data.append(item)

        # Pass data to the template
        return render_template('recommend.html', data=data)
    else:
        # Ensure you still pass data as an empty list if no book is found
        return render_template('recommend.html', data=[], message="Book not found. Please try another title.")

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out successfully.")
    return redirect(url_for('login_index'))

# Delete user route
@app.route('/delete_user', methods=['POST'])
def delete_user():
    user_id = request.form.get('user_id')  # Get the user ID from the form

    # Execute deletion query
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cursor.close()

    flash("User has been deleted successfully.")
    return redirect(url_for('admin_page'))

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    
    # Fetch current user data
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()  # Assuming user has id, name, and email columns
    cursor.close()

    if request.method == 'POST':
        new_name = request.form.get('name')
        new_email = request.form.get('email')

        # Update user info in the database
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE users SET name=%s, email=%s WHERE id=%s", (new_name, new_email, user_id))
        mysql.connection.commit()
        cursor.close()

        flash("Profile updated successfully.")
        return redirect(url_for('dashboard'))

    # Render update form with current user data
    return render_template('update_profile.html', user=user)


@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Fetch the user's current password hash from the database
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT password FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()

        if not user or not bcrypt.checkpw(current_password.encode('utf-8'), user[0].encode('utf-8')):
            flash("Current password is incorrect.", "danger")
            return redirect(url_for('change_password'))

        if new_password != confirm_password:
            flash("New password and confirmation password do not match.", "danger")
            return redirect(url_for('change_password'))

        # Hash the new password and update it in the database
        hashed_new_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_new_password, user_id))
        mysql.connection.commit()
        cursor.close()

        flash("Password changed successfully.", "success")
        return redirect(url_for('dashboard'))

    return render_template('change_password.html')

# #rate books
# @app.route('/rate_book', methods=['POST'])
# def rate_book():
#     if 'user_id' not in session:
#         flash("You must be logged in to rate books.")
#         return redirect(url_for('login'))

#     # Get form data
#     user_id = session['user_id']  # Assume user is logged in and session stores their ID
#     isbn = request.form.get('isbn')  # Book's ISBN
#     rating = request.form.get('rating')  # Rating (1-5)

#     # Validate the input
#     if not isbn or not rating:
#         flash("Invalid rating submission.", "danger")
#         return redirect(url_for('book_Recommendation'))

#     # Append the new rating to the CSV file
#     try:
#         with open('ratings.csv', 'a', newline='') as file:
#             writer = csv.writer(file)
#             writer.writerow([user_id, isbn, rating])
#         flash("Thank you for rating!", "success")
#     except Exception as e:
#         flash(f"Error saving the rating: {e}", "danger")

#     return redirect(url_for('book_Recommendation'))
# @app.route('/rate_book', methods=['POST'])
# def rate_book():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     # Process the rating
#     isbn = request.form.get('isbn')
#     rating = request.form.get('rating')
#     user_id = session['user_id']

#     # Save the rating to the database (or file)
#     with open('ratings.csv', 'a') as f:
#         f.write(f'{user_id},{isbn},{rating}\n')

#     # Generate recommendations again
#     user_input = session.get('user_input')
#     if user_input in pt.index:
#         index = np.where(pt.index == user_input)[0][0]
#         similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:11]
#         data = []
#         for i in similar_items:
#             item = []
#             temp_df = books[books['Book-Title'] == pt.index[i[0]]]
#             item.extend(list(temp_df.drop_duplicates("Book-Title")['Book-Title'].values))
#             item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
#             item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
#             item.extend(list(temp_df.drop_duplicates('Book-Title')['ISBN'].values))  # ISBN added here
#             data.append(item)

#         # Render the template with updated recommendations
#         return render_template('recommend.html', data=data)
#     else:
#         return render_template('recommend.html', data=[], message="Book not found. Please try another title.")

@app.route('/rate_book', methods=['POST'])
def rate_book():
    if 'user_id' not in session:
        return "Unauthorized", 401

    # Process the rating
    isbn = request.form.get('isbn')
    rating = request.form.get('rating')
    user_id = session['user_id']

    # Save the rating to the database (or file)
    with open('ratings.csv', 'a') as f:
        f.write(f'{user_id},{isbn},{rating}\n')

    # Return a success response for AJAX
    return "Rating submitted successfully!", 200
#Book Manage
@app.route('/book_manage')
def book_manage():
    # Reload the DataFrame from the CSV file to reflect updates
    global books_df
    books_df = pd.read_csv('Books.csv')  # Reload from CSV
    
    # Get the current page number from the query string
    page = request.args.get('page', 1, type=int)
    per_page = 100  # Number of books per page

    # Calculate start and end indices for the current page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    # Slice the DataFrame for the current page
    paginated_books = books_df.iloc[start_idx:end_idx]

    # Check if there's a next page
    has_next = end_idx < len(books_df)
    has_prev = start_idx > 0

    return render_template('admin/book_manage.html', 
                           books=paginated_books.to_dict(orient='records'), 
                           page=page, 
                           has_next=has_next, 
                           has_prev=has_prev)
#Add_books
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    if 'user_id' not in session:
        flash("You must be logged in to access this page.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Get book details from the form
        isbn = request.form.get('isbn')
        title = request.form.get('title')
        author = request.form.get('author')
        year = request.form.get('year')
        publisher = request.form.get('publisher')
        image_url_s = request.form.get('image_url_s')
        image_url_m = request.form.get('image_url_m')
        image_url_l = request.form.get('image_url_l')

        # Validate inputs
        if not (isbn and title and author and year and publisher):
            flash("All fields except image URLs are mandatory.", "danger")
            return redirect(url_for('add_book'))

        # Append the new book to Books.csv
        try:
            with open('Books.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([isbn, title, author, year, publisher, image_url_s, image_url_m, image_url_l])
            flash("Book added successfully!", "success")
        except Exception as e:
            flash(f"Error adding book: {e}", "danger")
        
        return redirect(url_for('admin_page'))

    return render_template('admin/add_book.html')

@app.route("/edit_book/<isbn>", methods=["GET", "POST"])
def edit_book(isbn):
    df = load_books()
    book = df[df["ISBN"] == isbn].to_dict(orient="records")[0]
    if request.method == "POST":
        df.loc[df["ISBN"] == isbn, "Book-Title"] = request.form["title"]
        df.loc[df["ISBN"] == isbn, "Book-Author"] = request.form["author"]
        df.loc[df["ISBN"] == isbn, "Year-Of-Publication"] = request.form["year"]
        df.loc[df["ISBN"] == isbn, "Publisher"] = request.form["publisher"]
        df.loc[df["ISBN"] == isbn, "Image-URL-S"] = request.form["img_s"]
        df.loc[df["ISBN"] == isbn, "Image-URL-M"] = request.form["img_m"]
        df.loc[df["ISBN"] == isbn, "Image-URL-L"] = request.form["img_l"]
        save_books(df)
        return redirect(url_for("book_manage"))
    return render_template("admin/edit_book.html", book=book)
#Delete Book
@app.route("/delete_book/<isbn>", methods=["POST"])
def delete_book(isbn):
    df = load_books()
    df = df[df["ISBN"] != isbn]
    save_books(df)
    return redirect(url_for("book_manage"))
###################################
#User Manage
@app.route('/user_manage')
def user_manage():
    # Reload the DataFrame from the CSV file to reflect updates
    global users_df
    users_df = pd.read_csv('Users.csv')  # Reload from CSV
    
    # Get the current page number from the query string
    page = request.args.get('page', 1, type=int)
    per_page = 100  # Number of users per page

    # Calculate start and end indices for the current page
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    # Slice the DataFrame for the current page
    paginated_users = users_df.iloc[start_idx:end_idx]

    # Check if there's a next page
    has_next = end_idx < len(users_df)
    has_prev = start_idx > 0

    return render_template('admin/user_manage.html', 
                           users=paginated_users.to_dict(orient='records'), 
                           page=page, 
                           has_next=has_next, 
                           has_prev=has_prev)

# Add User
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if 'user_id' not in session:
        flash("You must be logged in to access this page.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Get user details from the form
        user_id = request.form.get('user_id')
        location = request.form.get('location')
        age = request.form.get('age')

        # Validate inputs
        if not user_id or not location or not age:
            flash("All fields are mandatory.", "danger")
            return redirect(url_for('add_user'))

        # Append the new user to Users.csv
        try:
            with open('Users.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([user_id, location, age])
            flash("User added successfully!", "success")
        except Exception as e:
            flash(f"Error adding user: {e}", "danger")
        
        return redirect(url_for('user_manage'))

    return render_template('admin/add_user.html')

# Edit User
@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    # Load the DataFrame
    df = pd.read_csv('Users.csv')

    # Get the user record
    user = df[df['User-ID'] == user_id].to_dict(orient='records')[0]

    if request.method == 'POST':
        # Update user details
        df.loc[df['User-ID'] == user_id, 'Location'] = request.form['location']
        df.loc[df['User-ID'] == user_id, 'Age'] = request.form['age']

        # Save back to CSV
        df.to_csv('Users.csv', index=False)
        flash("User updated successfully!", "success")
        return redirect(url_for('user_manage'))

    return render_template('admin/edit_user.html', user=user)

# Delete User
@app.route('/delete_users/<int:user_id>', methods=['POST'])

def delete_users(user_id):
    # Load the DataFrame
    df = pd.read_csv('Users.csv')

    # Remove the user
    df = df[df['User-ID'] != user_id]

    # Save back to CSV
    df.to_csv('Users.csv', index=False)
    flash("User deleted successfully!", "success")
    return redirect(url_for('user_manage'))
# Run the app
if __name__ == '__main__':
    app.run(debug=True)