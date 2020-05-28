from flask import Flask, request, render_template, redirect, url_for, session
import os
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(24)

path = 'database.db';
database = sqlite3.connect(path)
cursor = database.cursor();

database.execute("CREATE TABLE IF NOT EXISTS PERSONALE("
                 "Matricola CHAR(5), "
                 "Password CHAR(5) NOT NULL, "
                 "Nome VARCHAR(50) NOT NULL, "
                 "Cognome VARCHAR(50) NOT NULL, "
                 "DataNascita DATE NOT NULL, "
                 "Indirizzo VARCHAR(50) NOT NULL, "
                 "NumTelefono INTEGER NOT NULL, "
                 "Ruolo VARCHAR(12) NOT NULL, "
                 "PRIMARY KEY(Matricola));")
try:
    cursor.execute(
        "INSERT INTO PERSONALE VALUES ('00000','admin','Pinco','Pallino','1/1/00','via bella n.5',03598456,'leader');")
    cursor.fetchall();
except:
    pass

database.commit();
database.close();


@app.route('/')
def root():
    if 'amministratore' in session:
        return render_template("homeAMMINISTRATORE.html")
    elif 'segretaria' in session:
        return render_template("homeSEGRETARIA.html")

    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        database = sqlite3.connect(path)
        cursor = database.cursor();
        cursor.execute("SELECT Matricola, Password, Ruolo  FROM PERSONALE WHERE Matricola = ? AND Password = ?",
                       [username, password])
        rows = cursor.fetchall()
        database.close();

        if len(rows) == 0:
            return redirect(url_for('loginerrato'))

        elif rows[0][2] == "leader":
            session['amministratore'] = username;
            return redirect(url_for('homeAMMINISTRATORE'))
        elif rows[0][2] == "segretaria":
            session['segretaria'] = username;
            print(session)
            return redirect(url_for('homeSEGRETARIA'))
        else:
            return redirect(url_for('loginerrato'))

    return render_template('login.html')


@app.route('/homeAMMINISTRATORE', methods=['GET'])
def homeAMMINISTRATORE():
    if 'amministratore' in session:
        return render_template("homeAMMINISTRATORE.html")
    else:
        return redirect(url_for('login'))


@app.route('/homeSEGRETARIA', methods=['GET'])
def homeSEGRETARIA():
    if 'segretaria' in session:
        return render_template("homeSEGRETARIA.html")
    else:
        return redirect(url_for('login'))


@app.route('/loginerrato', methods=['GET'])
def loginerrato():
    return render_template('loginerrato.html')

@app.route('/logout', methods=['GET'])
def logout():
    if 'amministratore' in session:
        session.pop('amministratore')
    elif 'segretaria' in session:
        session.pop('segretaria')
    return redirect(url_for('login'))


app.run(host="127.0.0.1", port=5000)
