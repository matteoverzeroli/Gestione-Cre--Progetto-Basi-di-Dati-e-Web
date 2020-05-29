from flask import Flask, request, render_template, redirect, url_for, session
import os
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(24)

path = 'database.db'
database = sqlite3.connect(path)
cursor = database.cursor();

#definizione ruoli della popolazione di riferimento
ruolo_partecipanti= ['leader', 'segretaria' ,'responsabile', 'esterno', 'animatore', 'bambino']

#totale partecimanti
totale_personale = 0;
totale_bambini = 0 ;
totale_animatori = 0;

#inizializzazione del database
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
                 "Punteggio INTEGER NOT NULL,"
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
                 "MatrBamnino CHAR(5) REFERENCES BAMBINO(Matricola),"
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

#inserisco il leader se non già inserito
try:
    cursor.execute(
        "INSERT INTO PERSONALE VALUES ('00000','admin','Pinco','Pallino','admin@gmail.com','1/1/00','via bella n.5',03598456,340586969,'leader');")
    cursor.fetchall()
except:
    pass

database.commit()


#calcolo numero partecipanti
cursor.execute("SELECT count(*)  FROM PERSONALE")
rows = cursor.fetchone()
totale_personale += int(str(rows[0]))

cursor.execute("SELECT count(*)  FROM ANIMATORE")
rows = cursor.fetchone()
totale_animatori += int(str(rows[0]))

cursor.execute("SELECT count(*)  FROM BAMBINO")
rows = cursor.fetchone()
totale_bambini += int(str(rows[0]))

database.close()

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
        cursor.execute("SELECT Matricola, Password, Ruolo  FROM PERSONALE WHERE Matricola = ? AND Password = ?",
                       [username, password])
        rows = cursor.fetchall()
        if len(rows) != 0:
            rows = rows[0][0], rows[0][1], rows[0][2]
        else:
            cursor = database.cursor();
            cursor.execute("SELECT Matricola, Password  FROM BAMBINO WHERE Matricola = ? AND Password = ?",
                           [username, password])
            rows = cursor.fetchall()

            if len(rows) != 0:
                rows = rows[0][0],rows[0][1],'bambino'

            else:
                cursor.execute("SELECT Matricola, Password  FROM ANIMATORE WHERE Matricola = ? AND Password = ?",
                               [username, password])
                rows = cursor.fetchall()

                if len(rows) != 0:
                    rows = rows[0][0],rows[0][1],'animatore'
                    print(rows)
                else:
                    database.close()
                    return redirect(url_for('loginerrato'))

        database.close()

        for partecipante in ruolo_partecipanti:
            if rows[2] == partecipante:
                session[partecipante] = username;
                return redirect(url_for('root'))

    return render_template('login.html')


@app.route('/homeLEADER', methods=['GET'])
def home_leader():
    if 'leader' in session:
        return render_template("homeLEADER.html")
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
    for partecipante in ruolo_partecipanti:
        if partecipante in session:
            session.pop(partecipante)

    return redirect(url_for('root'))

@app.route('/formInserisciSegretaria')
def form_inserisci_segretaria():
    if 'leader' in session:
        return render_template("formInserisciSegretaria.html")
    else:
        return redirect(url_for('login'))


app.run(host="127.0.0.1", port=5000)