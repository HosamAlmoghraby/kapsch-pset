from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import base64
import os
from helpers import apology, login_required, usd

# Configure application
app = Flask(__name__)

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///kapsch.db")

@app.route("/")
@login_required
def index():

        connection = sqlite3.connect("kapsch.db")
        countimages = connection.cursor()
        countimages.execute("SELECT count(*) FROM images WHERE category is null")
        uncategorized_images = countimages.fetchone()[0]

        if (uncategorized_images != 0):
            return redirect("/categorize_image")

        else:
            return render_template("upload_image.html")


@app.route("/upload_image", methods=["GET", "POST"])
@login_required
def upload_image():
    """Upload Images"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        uploaded_image = request.files['image']

        # Ensure photo was valid
        if not uploaded_image:
            return apology("must provide valid photo", 400)

        # Save the image temporary in temp folder
        saved_image = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_image.filename)
        uploaded_image.save(saved_image)

        # Open the image from temp folder
        with open(saved_image, "rb") as image:
            binary_image = base64.b64encode(image.read())

        # Insert the uploaded image into images table
        connection = sqlite3.connect("kapsch.db")
        sql_statement ="INSERT INTO images (image) VALUES (?)"
        cursor = connection.cursor()
        cursor.execute(sql_statement, [binary_image])
        connection.commit()

        # Remove the image from temp folder
        os.remove(saved_image)

        # Redirect user to upload more images
        flash(
            f"Thanks, image uploaded successfully, now you can start categorizing or upload more images")
        return redirect("/upload_image")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("upload_image.html")


@app.route("/categorize_image", methods=["GET", "POST"])
@login_required
def categorize_image():
    if request.method == "GET":

        # Read the images from images table
        connection = sqlite3.connect("kapsch.db")
        countimages = connection.cursor()
        countimages.execute("SELECT count(*) FROM images WHERE category is null")
        uncategorized_images = countimages.fetchone()[0]

        #
        if (uncategorized_images != 0):
            category = connection.cursor()
            category.execute("SELECT * FROM categories")
            categoryCount = connection.cursor()
            categoryCount.execute("SELECT count(*) FROM categories")
            count = categoryCount.fetchone()[0]
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM images WHERE category is null")
            currentData = {}
            currentData = cursor.fetchone()

            image_id = currentData[0]
            image_binary = currentData[1]
            with open("./static/image_name.jpg", "wb") as img:
                img.write(base64.b64decode(image_binary))

            rowData = {}  # this is a dict
            listRowData = []  # this is list

            currentRow = 0
            while currentRow <= count - 1:
                rowData = {}
                currCategory = category.fetchone()
                rowData['description'] = currCategory[1]
                rowData['id'] = currCategory[0]
                listRowData.append(rowData)
                currentRow = currentRow + 1

            # User reached route via GET (as by clicking a link or via redirect)
            return render_template("categorize_image.html", id=image_id, binary="./static/image_name.jpg", category=listRowData)

        else:
            # Redirect user to upload more images
            flash(
                f"All images categorized, Please upload a new image")
            return redirect("/upload_image")

    else:
        image_id = request.form['imgid']
        category = request.form.get('category')
        update = sqlite3.connect("kapsch.db")
        sql = "UPDATE images SET category = ? WHERE id = ?"
        cursor = update.cursor()
        cursor.execute(sql, [category, image_id])
        update.commit()

        # Redirect user to categorize more images
        flash(
            f"Thank you, image has been categorized successfully")
        return redirect("/categorize_image")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], password):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        password_confirmation = request.form.get("confirmation")
        hashed_password = generate_password_hash(password)

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not password:
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted
        elif not password_confirmation:
            return apology("must provide password confirmation", 400)

        # Query if there is any similar username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=username)

        # Ensure username not exists
        if len(rows) == 1:
            return apology("username taken", 400)

        # Ensure password and password confirmation are matching
        if password != password_confirmation:
            return apology("passwords don't match", 400)

        # Add the user into the users table in database
        rows = db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                          username=username, password=hashed_password)

        # Remember which user has logged in
        session["user_id"] = rows

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change password"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        password_confirmation = request.form.get("confirmation")

        # Ensure old password was submitted
        if not old_password:
            return apology("must provide old password", 403)

        # Ensure new password was submitted
        elif not new_password:
            return apology("must provide new password", 403)

        # Ensure password and password confirmation are matching
        elif new_password != password_confirmation:
            return apology("passwords don't match", 403)

        # Hashing the new password
        hashed_new_password = generate_password_hash(new_password)

        # Query database for old password
        rows = db.execute("SELECT password FROM users WHERE user_id = :user_id",
                          user_id=session["user_id"])

        # Ensure old password is correct
        if not check_password_hash(rows[0]["password"], old_password):
            return apology("invalid old password", 403)

        # Update user's password in the users table in database
        db.execute("UPDATE users SET password = :new_password WHERE user_id = :user_id",
                   new_password=hashed_new_password, user_id=session["user_id"])

        # Redirect user to home page
        flash("Password Changed!")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("change_password.html")



def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
