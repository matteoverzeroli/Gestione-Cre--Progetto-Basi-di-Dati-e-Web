from flask import Flask, request, render_template, redirect, url_for, session
import os
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(24)

path = 'database.db'
database = sqlite3.connect(path)
cursor = database.cursor()

# definizione ruoli della popolazione di riferimento
ruolo_partecipanti = ['leader', 'segretaria', 'responsabile', 'esterno', 'animatore', 'bambino']

# totale partecimanti
totale_leader = 0;
totale_segretarie = 0;
totale_responsabili = 0;
totale_esterni = 0;
totale_bambini = 0;
totale_animatori = 0;

# cerco matricola massima utilizzata
matricola_max = 0

# inizializzazione del database
database.execute("CREATE TABLE IF NOT EXISTS PERSONALE("
                 "Matricola CHAR(5), "
                 "Password CHAR(5) NOT NULL, "
                 "Nome VARCHAR(50) NOT NULL, "
                 "Cognome VARCHAR(50) NOT NULL, "
                 "Email VARCHAR(50) NOT NULL, "
                 "DataNascita DATE NOT NULL, "
                 "Indirizzo VARCHAR(50) NOT NULL, "
                 "NumTelefono INTEGER NOT NULL, "
                 "NumCellulare INTEGER, "
                 "Ruolo VARCHAR(12) NOT NULL, "
                 "PRIMARY KEY (Matricola));")

database.execute("CREATE TABLE IF NOT EXISTS ANIMATORE("
                 "Matricola CHAR(5), "
                 "Password CHAR(5) NOT NULL, "
                 "Nome VARCHAR(50) NOT NULL, "
                 "Cognome VARCHAR(50) NOT NULL, "
                 "Email VARCHAR(50) NOT NULL, "
                 "DataNascita DATE NOT NULL, "
                 "Indirizzo VARCHAR(50) NOT NULL, "
                 "NumTelefono INTEGER NOT NULL, "
                 "NumCellulare INTEGER, "
                 "MatrResponsabile CHAR(5) NOT NULL, "
                 "NomeSquadra VARCHAR(10) NOT NULL,  "
                 "PRIMARY KEY (Matricola), "
                 "FOREIGN KEY (MatrResponsabile) "
                 "REFERENCES PERSONALE(Matricola), "
                 "FOREIGN KEY (NomeSquadra) "
                 "REFERENCES SQUADRA(Nome));")

database.execute("CREATE TABLE IF NOT EXISTS BAMBINO("
                 "Matricola CHAR(5), "
                 "Password CHAR(5) NOT NULL, "
                 "Nome VARCHAR(50) NOT NULL, "
                 "Cognome VARCHAR(50) NOT NULL, "
                 "Email VARCHAR(50) NOT NULL, "
                 "DataNascita DATE NOT NULL, "
                 "Indirizzo VARCHAR(50) NOT NULL, "
                 "NumTelefono INTEGER NOT NULL, "
                 "NumCellulare INTEGER, "
                 "NominativoMadre VARCHAR(50) NOT NULL, "
                 "NominativoPadre VARCHAR(50) NOT NULL, "
                 "NomeSquadra VARCHAR(10) NOT NULL,  "
                 "PRIMARY KEY (Matricola) "
                 "FOREIGN KEY (NomeSquadra) "
                 "REFERENCES SQUADRA(Nome));")

database.execute("CREATE TABLE IF NOT EXISTS MOVIMENTO("
                 "Id INTEGER primary key AUTOINCREMENT, "
                 "TipoEvento VARCHAR(10), "
                 "Luogo VARCHAR(50),"
                 "Data DATE,"
                 "Ora TIME,"
                 "Descrizione VARCHAR(50) NOT NULL,"
                 "Valore FLOAT NOT NULL,"
                 "Inout BIT NOT NULL,"
                 "MatrSegretaria CHAR(5) NOT NULL,"
                 "FOREIGN KEY (TipoEvento,Luogo,Data,Ora) "
                 "REFERENCES EVENTO(TipoEvento,Luogo,Data,Ora),"
                 "FOREIGN KEY (MatrSegretaria) "
                 "REFERENCES PERSONALE(Matricola));")

database.execute("CREATE TABLE IF NOT EXISTS EVENTO("
                 "TipoEvento VARCHAR(10), "
                 "Luogo VARCHAR(50),"
                 "Data DATE,"
                 "Ora TIME,"
                 "Descrizione VARCHAR(50) NOT NULL,"
                 "Punteggio INTEGER,"
                 "MatrLeader CHAR(5) NOT NULL, "
                 "PRIMARY KEY (TipoEvento,Luogo,Data,Ora),"
                 "FOREIGN KEY (MatrLeader) "
                 "REFERENCES PERSONALE(Matricola));")

database.execute("CREATE TABLE IF NOT EXISTS SQUADRA("
                 "Nome VARCHAR(10),"
                 "Punteggio INTEGER DEFAULT 0,"
                 "Colore VARCHAR(10) NOT NULL,"
                 "Motto VARCHAR(50) NOT NULL,"
                 "PRIMARY KEY (Nome));")

database.execute("CREATE TABLE IF NOT EXISTS APPELLOBAMBINO("
                 "IdBambino CHAR(5) REFERENCES BAMBINO(Matricola),"
                 "Data DATA NOT NULL,"
                 "Presenza BIT NOT NULL,"
                 "PRIMARY KEY (IdBambino));")

database.execute("CREATE TABLE IF NOT EXISTS APPELLOANIMATORE("
                 "IdAnimatore CHAR(5) REFERENCES ANIMATORE(Matricola),"
                 "Data DATA NOT NULL,"
                 "Presenza BIT NOT NULL,"
                 "PRIMARY KEY (IdAnimatore));")

database.execute("CREATE TABLE IF NOT EXISTS APPELLOPERSONALE("
                 "IdPersonale CHAR(5) REFERENCES PERSONALE(Matricola),"
                 "Data DATA NOT NULL,"
                 "Presenza BIT NOT NULL,"
                 "PRIMARY KEY (IdPersonale));")

database.execute("CREATE TABLE IF NOT EXISTS ARBITRA("
                 "MatrResponsabile CHAR(5) REFERENCES PERSONALE(Matricola),"
                 "TipoEvento VARCHAR(10) NOT NULL, "
                 "Luogo VARCHAR(50) NOT NULL,"
                 "Data DATE NOT NULL,"
                 "Ora TIME NOT NULL,"
                 "FOREIGN KEY (TipoEvento,Luogo,Data,Ora)"
                 "REFERENCES EVENTO(TipoEvento,Lugo,Data,Ora));")

database.execute("CREATE TABLE IF NOT EXISTS GESTISCE("
                 "MatrEsterno CHAR(5) REFERENCES PERSONALE(Matricola),"
                 "TipoEvento VARCHAR(10) NOT NULL, "
                 "Luogo VARCHAR(50) NOT NULL,"
                 "Data DATE NOT NULL,"
                 "Ora TIME NOT NULL,"
                 "FOREIGN KEY (TipoEvento,Luogo,Data,Ora)"
                 "REFERENCES EVENTO(TipoEvento,Lugo,Data,Ora));")

database.execute("CREATE TABLE IF NOT EXISTS PARTECIPA("
                 "MatrBambino CHAR(5) REFERENCES BAMBINO(Matricola),"
                 "TipoEvento VARCHAR(10) NOT NULL, "
                 "Luogo VARCHAR(50) NOT NULL,"
                 "Data DATE NOT NULL,"
                 "Ora TIME NOT NULL,"
                 "Costo FLOAT NOT NULL,"
                 "Scadenza DATE NOT NULL, "
                 "FOREIGN KEY (TipoEvento,Luogo,Data,Ora)"
                 "REFERENCES EVENTO(TipoEvento,Lugo,Data,Ora));")

database.execute("CREATE TABLE IF NOT EXISTS ISCRIZIONE("
                 "NomeSquadra VARCHAR(10) REFERENCES SQUADRA(Nome),"
                 "TipoEvento VARCHAR(10) NOT NULL, "
                 "Luogo VARCHAR(50) NOT NULL,"
                 "Data DATE NOT NULL,"
                 "Ora TIME NOT NULL,"
                 "FOREIGN KEY (TipoEvento,Luogo,Data,Ora)"
                 "REFERENCES EVENTO(TipoEvento,Lugo,Data,Ora));")

# inserisco il leader se non già inserito
try:
    cursor.execute(
        "INSERT INTO PERSONALE VALUES ('00001','admin','Pinco','Pallino','admin@gmail.com','0000-1-1','via bella n.5',03598456,340586969,'leader');")
    cursor.fetchall()
except:
    pass

database.commit()

# calcolo numero partecipanti
cursor.execute("SELECT count(*)  FROM PERSONALE WHERE Ruolo = 'leader' ")
rows = cursor.fetchone()
totale_leader += int(str(rows[0]))

cursor.execute("SELECT count(*)  FROM PERSONALE WHERE Ruolo = 'segretaria' ")
rows = cursor.fetchone()
totale_segretarie += int(str(rows[0]))

cursor.execute("SELECT count(*)  FROM PERSONALE WHERE Ruolo = 'responsabile' ")
rows = cursor.fetchone()
totale_responsabili += int(str(rows[0]))

cursor.execute("SELECT count(*)  FROM PERSONALE WHERE Ruolo = 'esterno' ")
rows = cursor.fetchone()
totale_esterni += int(str(rows[0]))

cursor.execute("SELECT count(*)  FROM ANIMATORE")
rows = cursor.fetchone()
totale_animatori += int(str(rows[0]))

cursor.execute("SELECT count(*)  FROM BAMBINO")
rows = cursor.fetchone()
totale_bambini += int(str(rows[0]))

# cerco la matricola massima utilizzata all'interno del db
cursor.execute("SELECT Matricola  FROM PERSONALE ORDER BY Matricola desc")
rows = cursor.fetchone();
if rows is not None:
    rows = int(str(rows[0]))
    if rows > matricola_max:
        matricola_max = rows

cursor.execute("SELECT Matricola  FROM ANIMATORE ORDER BY Matricola desc")
rows = cursor.fetchone();
if rows is not None:
    rows = int(str(rows[0]))
    if rows > matricola_max:
        matricola_max = rows

cursor.execute("SELECT Matricola  FROM BAMBINO ORDER BY Matricola desc")
rows = cursor.fetchone();
if rows is not None:
    rows = int(str(rows[0]))
    if rows > matricola_max:
        matricola_max = rows

cursor.execute("SELECT Matricola  FROM ANIMATORE ORDER BY Matricola desc")
rows = cursor.fetchone();
if rows is not None:
    rows = int(str(rows[0]))
    if rows > matricola_max:
        matricola_max = rows

database.close()


# funzione per aggiornare dati inseriti nella session
def updateSessionData(partecipante,rows):
    session[partecipante] = rows[0]
    session['matricola'] = rows[0]
    session['password'] = rows[1]
    session['nome'] = rows[2]
    session['cognome'] = rows[3]
    session['email'] = rows[5]
    session['dataNascita'] = rows[6]
    session['indirizzo'] = rows[7]
    session['numTelefono'] = rows[8]
    session['numCellulare'] = rows[9]
    if rows[4] == 'bambino':
        session['nominativoMadre'] = rows[10]
        session['nominativoPadre'] = rows[11]
        session['nomeSquadra'] = rows[12]
    elif rows[4] == 'animatore':
        session['matrResponsabile'] = rows[10]
        session['nomeSquadra'] = rows[11]


@app.route('/')
def root():
    if ruolo_partecipanti[0] in session:
        return redirect(url_for('home_leader'))
    elif ruolo_partecipanti[1] in session:
        return redirect(url_for('home_segretaria'))
    elif ruolo_partecipanti[2] in session:
        return redirect(url_for('home_responsabile'))
    elif ruolo_partecipanti[3] in session:
        return redirect(url_for('home_esterno'))
    elif ruolo_partecipanti[4] in session:
        return redirect(url_for('home_animatore'))
    elif ruolo_partecipanti[5] in session:
        return redirect(url_for('home_bambino'))

    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        database = sqlite3.connect(path)
        cursor = database.cursor();
        cursor.execute(
            "SELECT Matricola, Password,Nome,Cognome,Ruolo, Email,DataNascita,Indirizzo,NumTelefono,NumCellulare  FROM PERSONALE WHERE Matricola = ? AND Password = ?",
            [username, password])
        rows = cursor.fetchall()
        if len(rows) != 0:
            rows = rows[0][0], rows[0][1], rows[0][2], rows[0][3], rows[0][4], rows[0][5], rows[0][6], rows[0][7], \
                   rows[0][8], rows[0][9]
        else:
            cursor = database.cursor();
            cursor.execute(
                "SELECT Matricola, Password,Nome,Cognome,Email,DAtaNascita,Indirizzo,NumTelefono,NumCellulare,NominativoMadre,NominativoPadre,NomeSquadra  FROM BAMBINO WHERE Matricola = ? AND Password = ?",
                [username, password])
            rows = cursor.fetchall()

            if len(rows) != 0:
                rows = rows[0][0], rows[0][1], rows[0][2], rows[0][3], 'bambino', rows[0][4], rows[0][5], rows[0][6], \
                       rows[0][7], rows[0][8], rows[0][9], rows[0][10], rows[0][11]

            else:
                cursor.execute(
                    "SELECT Matricola, Password,Nome,Cognome,Email,DataNascita,Indirizzo,NumTelefono,NumCellulare,MatrResponsabile,NomeSquadra  FROM ANIMATORE WHERE Matricola = ? AND Password = ?",
                    [username, password])
                rows = cursor.fetchall()

                if len(rows) != 0:
                    rows = rows[0][0], rows[0][1], rows[0][2], rows[0][3], 'animatore', rows[0][4], rows[0][5], rows[0][
                        6], \
                           rows[0][7], rows[0][8], rows[0][9], rows[0][10]
                else:
                    database.close()
                    return redirect(url_for('loginerrato'))

        database.close()

        for partecipante in ruolo_partecipanti:
            if rows[4] == partecipante:
                updateSessionData(partecipante,rows)
                return redirect(url_for('root'))

    return render_template('login.html')


@app.route('/homeLEADER', methods=['GET', 'POST'])
def home_leader():
    if request.method == 'POST' and 'form_modifica' in request.form:
        database = sqlite3.connect(path)
        cursor = database.cursor();
        cursor.execute(
            "UPDATE PERSONALE SET Password = ?, Nome = ?, Cognome = ?, Email = ?, DataNascita = ?, Indirizzo = ?, NumTelefono = ?, NumCellulare = ? WHERE Matricola = ?;",
            [request.form['password'],request.form['nome'], request.form['cognome'], request.form['email'], request.form['data'],
             request.form['indirizzo'], request.form['telefono'], request.form['cellulare'], request.form['matricola']])
        rows= request.form['matricola'],request.form['password'],request.form['nome'], request.form['cognome'],'leader', request.form['email'], request.form['data'],request.form['indirizzo'], request.form['telefono'], request.form['cellulare']
        database.commit()
        database.close()
        updateSessionData('leader',rows)

    elif request.method == 'POST' and 'form_elimina' in request.form:
        database = sqlite3.connect(path)
        cursor = database.cursor();
        cursor.execute("DELETE FROM PERSONALE WHERE Matricola= ?;",[session['matricola']])
        database.commit()
        database.close()
        return redirect(url_for("logout"))

    if 'leader' in session:
        return render_template("homeLEADER.html", usernamesession=session['nome'] + " " + session
        ['cognome'], matricola=session['matricola'], password=session['password'], nome=session['nome'],
                               cognome=session['cognome'], email=session['email'], data=session['dataNascita'],
                               indirizzo=session['indirizzo'],
                               telefono=session['numTelefono'], cellulare=session['numCellulare'], totalepartecipanti=(
                    totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader, totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni, totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini)
    else:
        return redirect(url_for('login'))


@app.route('/homeSEGRETARIA', methods=['GET'])
def home_segretaria():
    if 'segretaria' in session:
        return render_template("homeSEGRETARIA.html")
    else:
        return redirect(url_for('login'))


@app.route('/homeRESPONSABILE', methods=['GET'])
def home_responsabile():
    if 'responsabile' in session:
        return render_template("homeRESPONSABILE.html")
    else:
        return redirect(url_for('login'))


@app.route('/homeESTERNO', methods=['GET'])
def home_esterno():
    if 'esterno' in session:
        return render_template("homeESTERNO.html")
    else:
        return redirect(url_for('login'))


@app.route('/homeANIMATORE', methods=['GET'])
def home_animatore():
    if 'animatore' in session:
        return render_template("homeANIMATORE.html")
    else:
        return redirect(url_for('login'))


@app.route('/homeBAMBINO', methods=['GET'])
def home_bambino():
    if 'bambino' in session:
        return render_template("homeBAMBINO.html")
    else:
        return redirect(url_for('login'))


@app.route('/loginerrato', methods=['GET'])
def loginerrato():
    return render_template('loginerrato.html')


@app.route('/logout', methods=['GET'])
def logout():
    keys = list(session.keys())
    for key in keys:
            session.pop(key)
    return redirect(url_for('root'))


@app.route('/formInserisciSegretaria', methods=['GET', 'POST'])
def form_inserisci_segretaria():
    if request.method == 'POST':
        matricola = request.form['matricola']
        password = request.form['password']
        nome = request.form['nome']
        cognome = request.form['cognome']
        email = request.form['email']
        data = request.form['data']
        indirizzo = request.form['indirizzo']
        telefono = request.form['telefono']
        cellulare = request.form['cellulare']

        database = sqlite3.connect(path)
        cursor = database.cursor()
        cursor.execute(
            "INSERT INTO PERSONALE VALUES (?,?,?,?,?,?,?,?,?,?);",
            [matricola, password, nome, cognome, email, data, indirizzo, telefono, cellulare, 'segretaria'])

        cursor.fetchall()
        database.commit()
        database.close()

        global totale_segretarie
        totale_segretarie += 1

        global matricola_max
        matricola_max += 1

        return redirect(url_for('form_inserisci_segretaria'))

    if 'leader' in session:
        return render_template("formInserisciSegretaria.html",
                               matricola=str((matricola_max + 1)).zfill(5),
                               usernamesession=session['nome'] + " " + session
                               ['cognome'], totalepartecipanti=(
                    totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader, totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni, totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini)
    else:
        return redirect(url_for('login'))


@app.route('/formCreaGita', methods=['GET', 'POST'])
def form_crea_gita():
    if request.method == 'POST':
        tipoGita = request.form['tipoGita']

    if 'leader' in session:
        return render_template("formCreaGita.html", usernamesession=session['nome'] + " " + session
        ['cognome'], totalepartecipanti=(
                totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader, totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni, totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini)
    else:
        return redirect(url_for('login'))


@app.route('/formCreaGioco')
def form_crea_gioco():

    if 'leader' in session:
        return render_template("formCreaGioco.html", usernamesession=session['nome'] + " " + session
        ['cognome'], totalepartecipanti=(
                totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader, totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni, totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini)
    else:
        return redirect(url_for('login'))


@app.route('/formCreaLaboratorio')
def form_crea_laboratorio():
    if 'leader' in session:
        return render_template("formCreaLaboratorio.html", usernamesession=session['nome'] + " " + session
        ['cognome'], totalepartecipanti=(
                totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader, totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni, totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini)
    else:
        return redirect(url_for('login'))


app.run(host="127.0.0.1", port=5000)
