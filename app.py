from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt


app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'loginflask'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Init MySQL
mysql = MySQL(app) 

@app.route('/') 
def index():
    return render_template('home.html')

class SignupForm(Form):
    name = StringField('Name', [validators.Length(min=2, max=50),  validators.DataRequired()])
    email = StringField('Email', [validators.Length(min=6, max=50),  validators.DataRequired()])
    password = PasswordField('Password', [
        validators.Length(min=6, max=50),
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match.')
        ])
    confirm = PasswordField('Confirm Password', [validators.Length(min=6, max=50), validators.DataRequired()])

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create Cursor and Execute Query
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, password) VALUES (%s, %s, %s)", (name, email, password))

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()      

        flash('You are now Signed Up. You can login now.', 'success')

        redirect(url_for('login'))
    return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        current_password = request.form['password']

        # Create Cursor and Execute Query
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM users WHERE email = %s", [email])
        if result > 0:
            data = cur.fetchone()
            password = data['password']
            if sha256_crypt.verify(current_password, password):
                session['logged_in'] = True
                session['name'] = data['name']

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid Login'
                return render_template('login.html', error=error)
            cur.close()    
        else:
            error = 'Email not found'
            return render_template('login.html', error=error)

        # Commit to DB
        mysql.connection.commit()

        # Close connection
        cur.close()

    return render_template('login.html')    

@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


if __name__ == '__main__':
    app.secret_key='secret101'
    app.run(debug=True)
