import os
import glob

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
import smtplib
from other_functions import login_required, apology
import Account_management
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///store_database.db")

app.config['SECRET_KEY'] = 'ultra_secret_key'

# Configure session to use filesystem (instead of signed cookies)
"""
app.config["SESSION_FILE_DIR"] = mkdtemp()
"""
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    
    if request.method == "POST":
        name = request.form.get("name")
        return render_template("name.html", name=name)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        
        registration = Account_management.register(username, password)
        
        if registration != "Success":
            return render_template("apology.html", p=registration)
        
        else:
            return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    if request.method == "POST":
        #Errorchecking.
        if not request.form.get('username'):
            return render_template("apology.html", p="No username entered")
        if not request.form.get('password'):
            return render_template("apology.html", p="No password entered.")

        #Loging in.
        username = request.form.get('username')
        password = request.form.get('password')

        #return render_template("index.html")
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get('username'))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not request.form.get('password'): #check_password_hash(rows[0]["hash"], 
           return render_template("apology.html", p="Invalid.")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        #return redirect("/")
        session['user_name'] = username
        return render_template("success.html", username=session['user_name'])
        

        # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@login_required
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")

@app.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
    if request.method == "GET":
        return render_template("e_mail.html")
    
    if request.method == "POST":
        if not request.form.get('e_mail'):
            return apology("No E-Mail entered.")
        
        else:
            #Sending a E-Mail.
            entered_message = request.form.get('message')
            e_mail = request.form.get('e_mail')
            message = "Success. This is a test. " + entered_message
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login("server.coltex@gmail.com", os.getenv("G-Mail_password"))
            server.sendmail("server.coltex@gmail.com", e_mail, message)
            return render_template("success.html")
"""
@app.route("/about")
def about():
    return render_template("about.html")
"""
@app.route("/chat", methods=["GET", "POST"])
@login_required
def chat():
    if request.method == "GET":
        if session['user_name'] != "Wolf":
            message_package = db.execute("SELECT sender, message FROM com WHERE sender = ? OR receiver = ?", session['user_name'], session['user_name'])
            if message_package == []:
                db.execute("INSERT INTO com (sender, message, receiver) VALUES (?, ?, ?)", "Server", "Initialising Chat. Wenn es Fragen gibt, bitte hier stellen.", session['user_name'])
                return redirect("/chat")
            package = message_package[0]
            return render_template("chat.html", message_package=message_package)
        
        else:
            message_package = db.execute("SELECT sender, message, receiver FROM com")
            package = message_package[0]
            recipients = db.execute("SELECT username FROM users")
            return render_template("chat.html", message_package=message_package, recipients=recipients)
    
    if request.method == "POST":
        if session['user_name'] != "Wolf":
            comment = request.form.get('comment')
            db.execute("INSERT INTO com (sender, message, receiver) VALUES (?, ?, ?)", session['user_name'], comment, "Wolf")
            return redirect("/chat")
        else:
            comment = request.form.get('comment')
            receiver = request.form.get('selected_recipient')
            db.execute("INSERT INTO com (sender, message, receiver) VALUES (?, ?, ?)", "Admin", comment, receiver)
            return redirect("/chat")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/test")
def test():
    return render_template("test.html")

app.config['UPLOAD_FOLDER'] = "./Uploads"

@app.route("/order", methods=["GET", "POST"])
def order():
    if request.method == "GET":
        return render_template("order.html")
    
    if request.method == "POST":
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect("order.html")
        
        file = request.files['file']

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        
        # Checking for Entered Email
        Email = request.form.get('Email')
        
        if Email == None:
            return render_template("apology.html", p="No Email Entered.")
        
        
        """#Sending a E-Mail.
        entered_message = request.form.get('message')
        e_mail = "willers.colt@gmail.com"
        message = "Success. This is a test. " + entered_message
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("server.coltex@gmail.com", os.getenv("G-Mail_password"))
        server.sendmail("server.coltex@gmail.com", e_mail, message)"""
        
        ###########################################################
        # Finding Latest File Submitted. 
        list_of_files = glob.glob('./uploads/*') # * means all if need specific format then for example: *.csv
        latest_file = max(list_of_files, key=os.path.getctime)
        ###########################################################
        email = 'server.coltex@gmail.com'
        password = 'Business123!'
        send_to_email = 'willers.colt@gmail.com'
        subject = 'File'
        if request.form.get('message') != None:
            message = request.form.get('message')
        else:
            message = 'No Message Entered.'
        
        message = message + "\n" + Email
        file_location = str(latest_file) ########################################### Working here. Find out how to send newest File. 

        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = send_to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        # Setup the attachment
        filename = os.path.basename(file_location)
        attachment = open(file_location, "rb")
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', "attachment; filename= %s" % filename)

        # Attach the attachment to the MIMEMultipart object
        msg.attach(part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, password)
        text = msg.as_string()
        server.sendmail(email, send_to_email, text)
        server.quit()

        return render_template("order_success.html")