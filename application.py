import sqlite3
import urllib.request
import xmltodict

from flask import Flask, flash, g, redirect, render_template, request, session, escape, request, url_for
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

# Configure Application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Secret Key for the Session
app.secret_key = b'sngIORGNVBIO%#$^&VUIDHGiu'

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if session.get('user_id') is None:
            return redirect("login")

        return view(*args, **kwargs)

    return wrapped_view


@login_required
def display_feeds(feed):
    # A method that takes feed information and returns a feeds_list object that can be displayed for the user
    # This involves parsing the feed text into meaningful readable information

    feeds_list = []

    # Convert the feed text to dict
    doc = xmltodict.parse(feed)

    news = doc['rss']['channel']['item']

    for x in news:
        art = {'title': "", 'link': "", 'pubDate': "", 'description': "", 'img': ""}
        for k, v in x.items():
            if k == 'title':
                art['title'] = v

            elif k == 'link':
                art['link'] = v

            elif k == 'pubDate':
                art['pubDate'] = v

            elif k == 'description':
                data = filter_description(v)
                art['img'] = data[0]
                art['description'] = data[1]

            elif k == 'content:encoded':
                data = filter_description(v)
                art['img'] = data[0]

            elif k == 'img':
                art['img'] = v
            elif k == 'media:thumbnail':
                art['img'] = v['@url']

            elif k == 'media:content':
                if v is None:
                    e = 0
                else:
                    art['img'] = v[0]['@url']

        # Add parsed feed data to feeds_list per article
        feeds_list.append(art)

    return feeds_list


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    # HomePage of Website After Login

    connection = sqlite3.connect('news.db', isolation_level=None)
    cursor = connection.cursor()

    id = session["user_id"]

    if request.method == "POST":

        # Get name of user for greeting message on web page
        greeting = cursor.execute("SELECT name FROM users WHERE id=?", (id,))
        message = greeting.fetchone()

        if not request.form.get("feed"):
            return render_template("error.html", message="Please add a valid url to add it to your feed")

        addition = request.form.get("feed")

        # Send url to method that will retrieve the feed information and add it to the database
        pull_text(addition)

        # Send feeds to method to return a list to be displayed on the index page
        feeds = get_header(cursor.execute("SELECT * FROM feed_list WHERE list_id=?", ((id + 5),)))

        # Send feeds to method to return a list to be displayed on the index page
        articles = sort(cursor.execute("SELECT * FROM feed_list WHERE list_id=?", ((id + 5),)))

        connection.close()
        return render_template("index.html", name=message[0], articles=articles, feeds=feeds)

    else:

        # Get name of user for greeting message on web page
        greeting = cursor.execute("SELECT name FROM users WHERE id=?", (id,))
        message = greeting.fetchone()

        # Have program update feeds in users feed list
        current = cursor.execute("SELECT * FROM feed_list WHERE list_id=?", ((id + 5),))

        update(current)

        # Send feeds to method to return a list of headers to be displayed
        feeds = get_header(cursor.execute("SELECT * FROM feed_list WHERE list_id=?", ((id + 5),)))

        # Send feeds to method to return a list to be displayed on the index page
        articles = sort(cursor.execute("SELECT * FROM feed_list WHERE list_id=?", ((id + 5),)))

        connection.close()
        return render_template("index.html", name=message[0], articles=articles, feeds=feeds)


@login_required
@app.route("/selection", methods=["POST"])
def selection():
    # Method that enables the user to select specific feeds to view
    id = session['user_id']
    articles = []

    connection = sqlite3.connect('news.db', isolation_level=None)
    cursor = connection.cursor()

    # Get name of user for greeting message on web page
    greeting = cursor.execute("SELECT name FROM users WHERE id=?", (id,))
    message = greeting.fetchone()

    feeds = cursor.execute("SELECT * FROM feed_list WHERE list_id=?", ((id + 5),))

    if request.form['selected'] == "All":
        articles = sort(feeds)

    for i in feeds:
        x = str(i[0])
        if request.form['selected'] == x:
            articles = sort(cursor.execute("SELECT * FROM feed_list WHERE item_id=?", (i[0], )))

    # Send feeds to method to return a list of headers to be displayed
    feeds = get_header(cursor.execute("SELECT * FROM feed_list WHERE list_id=?", ((id + 5),)))

    connection.close()
    return render_template("index.html", message=message, articles=articles, feeds=feeds)


@app.route("/login", methods=["GET", "POST"])
def login():
    # Login page of the Web Application

    connection = sqlite3.connect('news.db', isolation_level=None)
    cursor = connection.cursor()

    session.clear()

    if request.method == "POST":

        # Check to ensure all fields filled in
        if not request.form.get("username") or not request.form.get("password"):
            return render_template("error.html", message="Invalid Username or Password")

        username = request.form.get("username")

        # Check to ensure that the provided username is in the database
        user = cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        p = user.fetchone()

        if p == None:
            return render_template("error.html", message="Invalid Username")

        password_hash = p[3]

        if not check_password_hash(password_hash, request.form.get("password")):
            return render_template("error.html", message="Invalid Password")

        # Remember which user is logged in
        session['user_id'] = p[0]

        connection.close()
        # Redirect user to the Home Page
        return redirect("/")

    else:
        connection.close()
        return render_template("login.html")


@app.route('/logout', methods=["GET"])
@login_required
def logout():
    # Logout from account

    # Forget user_id
    session.clear()

    # redirect to login screen
    return redirect("/")


@app.route('/register', methods=["GET", "POST"])
def register():
    # Registration page of the application

    connection = sqlite3.connect('news.db')
    cursor = connection.cursor()

    if request.method == "POST":

        # Check to Ensure all fields were filled out
        if not request.form.get("name") or not request.form.get("username") or not request.form.get(
                "email") or not request.form.get("password") or not request.form.get("confirmation"):
            return render_template("error.html", message="You must Complete all Fields to Complete Registration")

        # Check to ensure that the provided username is still available
        x = request.form.get("username")
        user = cursor.execute("SELECT * FROM users WHERE username=?", (x,))

        if user.fetchone() is not None:
            return render_template("error.html", message="That username has already been taken")

        if request.form.get("password") != request.form.get("confirmation"):
            return render_template("error.html", message="The passwords do not match")

        password = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8)

        data = (request.form.get("name"), request.form.get("username"), password, request.form.get("email"))

        # Enter new users info into the database
        cursor.execute("INSERT INTO users (name, username, password, email) VALUES (?, ?, ?, ?)", data)
        connection.commit()

        # Get user ID for registered user
        entry = cursor.execute("SELECT * FROM users WHERE username=?", (x,))

        person = entry.fetchone()

        # Store user info in session
        session['user_id'] = person[0]

        connection.close()
        return redirect("/")

    else:
        connection.close()
        return render_template("register.html")


@login_required
def pull_text(url):
    # A method that will take the url provided by the user and pull the feed from it and store it into the database
    # If the method receives a 0 as value t then it will create a new db entry. If it receives a 1 it will update an existing
    # entry.
    connection = sqlite3.connect('news.db', isolation_level=None)
    cursor = connection.cursor()

    user = session["user_id"]

    # Pull information from the provided url
    response = urllib.request.urlopen(url)

    # read the data from the url
    data = response.read()

    # convert url data to string
    text = data.decode('utf-8')

    feed = (user + 5, url, text)

    # Insert feed into database
    cursor.execute("INSERT INTO feed_list (list_id, url, feed) VALUES (?,?,?)", feed)

    connection.close()


def filter_description(text):
    # A method that will take any image data out of an article description, it will also make the description shorter
    # and more human readable

    image = ""
    desc = ""

    # Find the beginning of a src image link
    image_start = text.find("src")

    # Find the end of the source image link
    image_end = text.find("jpg")

    if image_end == -1:
        image_end = text.find("png")

    for elem in text[image_start + 5:image_end + 3:1]:
        image += elem

    desc_start = text.find("<p>")
    desc_end = text.find("</p>")

    alt_desc_start = text.find("<h1>")
    alt_desc_end = text.find("</h1>")

    if alt_desc_start == -1:
        for x in text[desc_start + 1:desc_end:1]:
            desc += x

    else:
        for y in text[alt_desc_start + 1:alt_desc_end:1]:
            desc += y

    return image, desc


def get_header(feed):
    # A method that will retrieve the header information of the each feed

    headers = []

    for i in feed:

        doc = xmltodict.parse(i[3])

        info = doc['rss']['channel']
        top = {'title': "", 'image': "", 'feed_id': i[0]}

        for k, v in info.items():
            if k == 'title':
                top['title'] = v
            if k == 'image':
                for x, y in v.items():
                    if x == 'url':
                        top['url'] = y

        headers.append(top)

    return headers


def sort(feed):
    # A method that will take a list of parsed feeds and sort the order they get displayed

    # The list received directly from the database is indexed into each feed
    # If I send each individual feed to be parsed and returned into  a list
    # I can add the list into a list of lists and then create a loop that will
    # create a final list to return to index to be displayed.
    list_a = []

    for i in feed:
        # Have each feed parsed individually and saved into their own separate list

        alpha = display_feeds(i[3])

        list_a.append(alpha)

        length = 1000
    # Determine the shortest list

    if len(list_a) == 0:
        return list_a

    for x in list_a:
        if len(x) < length:
            length = len(x)

    num = len(list_a)
    sorted_list = []

    for y in range(length):
        for z in list_a:
            sorted_list.append(z[y])

    return sorted_list


def update(feeds):
    connection = sqlite3.connect('news.db')
    cursor = connection.cursor()

    for x in feeds:
        # Pull information from the provided url
        response = urllib.request.urlopen(x[2])

        # read the data from the url
        data = response.read()

        # convert url data to string
        text = data.decode('utf-8')

        temp = (text, x[2])
        cursor.execute("UPDATE feed_list SET feed=? WHERE url=?", temp)

    connection.commit()
    connection.close()


@app.route('/premade', methods=["POST"])
def premade():
    # A method that will change the feed display to a premade news list the user selects
    connection = sqlite3.connect('news.db', isolation_level=None)
    cursor = connection.cursor()

    id = session['user_id']

    # Get name of user for greeting message on web page
    greeting = cursor.execute("SELECT name FROM users WHERE id=?", (id,))
    message = greeting.fetchone()

    if request.form['category'] == "arts":

        # Have program update feeds in feed list
        current = cursor.execute("SELECT * FROM feed_list WHERE list_id=?", (1, ))

        update(current)

        # Send feeds to method to return a list of headers to be displayed
        feeds = get_header(cursor.execute("SELECT * FROM feed_list WHERE list_id=?", (1, )))

        # Send feeds to method to return a list to be displayed on the index page
        articles = sort(cursor.execute("SELECT * FROM feed_list WHERE list_id=?", (1, )))

    elif request.form['category'] == "science":

        # Have program update feeds in feed list
        current = cursor.execute("SELECT * FROM feed_list WHERE list_id=?", (2,))

        update(current)

        # Send feeds to method to return a list of headers to be displayed
        feeds = get_header(cursor.execute("SELECT * FROM feed_list WHERE list_id=?", (2,)))

        # Send feeds to method to return a list to be displayed on the index page
        articles = sort(cursor.execute("SELECT * FROM feed_list WHERE list_id=?", (2,)))

    elif request.form['category'] == "tech":
        # Have program update feeds in feed list
        current = cursor.execute("SELECT * FROM feed_list WHERE list_id=?", (3,))

        update(current)

        # Send feeds to method to return a list of headers to be displayed
        feeds = get_header(cursor.execute("SELECT * FROM feed_list WHERE list_id=?", (3,)))

        # Send feeds to method to return a list to be displayed on the index page
        articles = sort(cursor.execute("SELECT * FROM feed_list WHERE list_id=?", (3,)))

    elif request.form['category'] == "world":
        # Have program update feeds in feed list
        current = cursor.execute("SELECT * FROM feed_list WHERE list_id=?", (5,))

        update(current)

        # Send feeds to method to return a list of headers to be displayed
        feeds = get_header(cursor.execute("SELECT * FROM feed_list WHERE list_id=?", (5,)))

        # Send feeds to method to return a list to be displayed on the index page
        articles = sort(cursor.execute("SELECT * FROM feed_list WHERE list_id=?", (5,)))

    elif request.form['category'] == "custom":
        # Have program update feeds in users feed list
        current = cursor.execute("SELECT * FROM feed_list WHERE list_id=?", ((id + 5),))

        update(current)

        # Send feeds to method to return a list of headers to be displayed
        feeds = get_header(cursor.execute("SELECT * FROM feed_list WHERE list_id=?", ((id + 5),)))

        # Send feeds to method to return a list to be displayed on the index page
        articles = sort(cursor.execute("SELECT * FROM feed_list WHERE list_id=?", ((id + 5),)))

    connection.close()
    return render_template("index.html", message=message, articles=articles, feeds=feeds)