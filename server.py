from flask import Flask, request, render_template, redirect , url_for, session
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def root():
    if 'amministratore' in session:
        return render_template("home.html")

    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == 'matteo' and password == '1':
            session['amministratore'] = username;

            return redirect(url_for('logincorretto'))
        else :
            return redirect(url_for('loginerrato'))

    return render_template('login.html')

@app.route('/loginerrato', methods=['GET'])
def loginerrato():
    return render_template('loginerrato.html')

@app.route('/logincorretto', methods=['GET'])
def logincorretto():
    if 'amministratore' in session:
        return render_template("logincorretto.html")
    else :
        return redirect(url_for('login'))

app.run(host="127.0.0.1", port=5000)