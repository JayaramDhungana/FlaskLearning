# admin.py
from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from functools import wraps
from flask_mysqldb import MySQL
import bcrypt

admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for('login'))
        # Access MySQL instance from the main app
        from app import mysql
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT role FROM users WHERE id=%s", (session['user_id'],))
        user = cursor.fetchone()
        cursor.close()
        if user and user[0] == 'admin':
            return f(*args, **kwargs)
        else:
            flash("Admin access required.", "danger")
            return redirect(url_for('home'))
    return decorated_function

@admin_bp.route('/')
@admin_required
def admin_dashboard():
    from app import mysql
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, name, email, role FROM users")
    users = cursor.fetchall()
    cursor.close()
    return render_template('admin_dashboard.html', users=users)

@admin_bp.route('/promote/<int:user_id>', methods=['POST'])
@admin_required
def promote_user(user_id):
    from app import mysql
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE users SET role = 'admin' WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cursor.close()
    flash("User promoted to admin successfully.", "success")
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/demote/<int:user_id>', methods=['POST'])
@admin_required
def demote_user(user_id):
    from app import mysql
    cursor = mysql.connection.cursor()
    cursor.execute("UPDATE users SET role = 'user' WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cursor.close()
    flash("Admin role removed from user.", "success")
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def delete_user(user_id):
    from app import mysql
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    mysql.connection.commit()
    cursor.close()
    flash("User deleted successfully.", "success")
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/books')
@admin_required
def manage_books():
    from app import mysql
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, title, author, image_url FROM books")
    books = cursor.fetchall()
    cursor.close()
    return render_template('manage_books.html', books=books)

@admin_bp.route('/add_book', methods=['GET', 'POST'])
@admin_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        image_url = request.form.get('image_url')

        from app import mysql
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO books (title, author, image_url) VALUES (%s, %s, %s)", (title, author, image_url))
        mysql.connection.commit()
        cursor.close()

        flash("Book added successfully.", "success")
        return redirect(url_for('admin.manage_books'))
    return render_template('add_book.html')

@admin_bp.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
@admin_required
def edit_book(book_id):
    from app import mysql
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        image_url = request.form.get('image_url')

        cursor.execute("UPDATE books SET title=%s, author=%s, image_url=%s WHERE id=%s", (title, author, image_url, book_id))
        mysql.connection.commit()
        cursor.close()

        flash("Book updated successfully.", "success")
        return redirect(url_for('admin.manage_books'))

    cursor.execute("SELECT id, title, author, image_url FROM books WHERE id=%s", (book_id,))
    book = cursor.fetchone()
    cursor.close()

    if not book:
        flash("Book not found.", "danger")
        return redirect(url_for('admin.manage_books'))

    return render_template('edit_book.html', book=book)

@admin_bp.route('/delete_book/<int:book_id>', methods=['POST'])
@admin_required
def delete_book(book_id):
    from app import mysql
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM books WHERE id=%s", (book_id,))
    mysql.connection.commit()
    cursor.close()

    flash("Book deleted successfully.", "success")
    return redirect(url_for('admin.manage_books'))
