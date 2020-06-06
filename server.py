import os
import sqlite3
import hashlib
from flask import Flask, request, render_template, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = os.urandom(24)

path = 'database.db'
database = sqlite3.connect(path)
cursor = database.cursor()

# definizione ruoli della popolazione di riferimento
ruolo_partecipanti = ['leader', 'segretaria', 'responsabile', 'esterno', 'animatore', 'bambino']

# totale partecimanti
totale_leader = -1;
totale_segretarie = 0;
totale_responsabili = 0;
totale_esterni = 0;
totale_bambini = -1;
totale_animatori = -1;

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
                 "MatrResponsabile CHAR(5) NOT NULL DEFAULT '00000', "
                 "NomeSquadra VARCHAR(10),  "
                 "PRIMARY KEY (Matricola), "
                 "FOREIGN KEY (MatrResponsabile) "
                 "REFERENCES PERSONALE(Matricola) ON DELETE SET DEFAULT, "
                 "FOREIGN KEY (NomeSquadra) "
                 "REFERENCES SQUADRA(Nome))")

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
                 "NomeSquadra VARCHAR(10),  "
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
                 "MatrSegretaria CHAR(5) NOT NULL DEFAULT '00000',"
                 "FOREIGN KEY (TipoEvento,Luogo,Data,Ora) "
                 "REFERENCES EVENTO(TipoEvento,Luogo,Data,Ora),"
                 "FOREIGN KEY (MatrSegretaria) "
                 "REFERENCES PERSONALE(Matricola) ON DELETE SET DEFAULT);")

database.execute("CREATE TABLE IF NOT EXISTS EVENTO("
                 "TipoEvento VARCHAR(10), "
                 "Luogo VARCHAR(50),"
                 "Data DATE,"
                 "Ora TIME,"
                 "Descrizione VARCHAR(50) NOT NULL,"
                 "Punteggio INTEGER,"
                 "MatrLeader CHAR(5) NOT NULL DEFAULT '00000', "
                 "PRIMARY KEY (TipoEvento,Luogo,Data,Ora),"
                 "FOREIGN KEY (MatrLeader) "
                 "REFERENCES PERSONALE(Matricola) ON DELETE SET DEFAULT );")

database.execute("CREATE TABLE IF NOT EXISTS SQUADRA("
                 "Nome VARCHAR(10),"
                 "Punteggio INTEGER DEFAULT 0,"
                 "Colore VARCHAR(10) NOT NULL,"
                 "Motto VARCHAR(50) NOT NULL,"
                 "PRIMARY KEY (Nome));")

database.execute("CREATE TABLE IF NOT EXISTS APPELLOBAMBINO("
                 "IdBambino CHAR(5) DEFAULT '00002' REFERENCES BAMBINO(Matricola) ON DELETE SET DEFAULT,"
                 "Data DATA NOT NULL,"
                 "Presenza BIT NOT NULL,"
                 "PRIMARY KEY (IdBambino, Data));")

database.execute("CREATE TABLE IF NOT EXISTS APPELLOANIMATORE("
                 "IdAnimatore CHAR(5) DEFAULT '00003' REFERENCES ANIMATORE(Matricola) ON DELETE SET DEFAULT,"
                 "Data DATA NOT NULL,"
                 "Presenza BIT NOT NULL,"
                 "PRIMARY KEY (IdAnimatore, Data));")

database.execute("CREATE TABLE IF NOT EXISTS APPELLOPERSONALE("
                 "IdPersonale CHAR(5) DEFAULT '00000' REFERENCES PERSONALE(Matricola) ON DELETE SET DEFAULT,"
                 "Data DATA NOT NULL,"
                 "Presenza BIT NOT NULL,"
                 "PRIMARY KEY (IdPersonale, Data));")

database.execute("CREATE TABLE IF NOT EXISTS ARBITRA("
                 "MatrResponsabile CHAR(5) REFERENCES PERSONALE(Matricola),"
                 "TipoEvento VARCHAR(10) NOT NULL, "
                 "Luogo VARCHAR(50) NOT NULL,"
                 "Data DATE NOT NULL,"
                 "Ora TIME NOT NULL, "
                 "PRIMARY KEY (MatrResponsabile, TipoEvento,Luogo,Data,Ora), "
                 "FOREIGN KEY (TipoEvento,Luogo,Data,Ora) "
                 "REFERENCES EVENTO(TipoEvento,Luogo,Data,Ora));")

database.execute("CREATE TABLE IF NOT EXISTS GESTISCE("
                 "MatrEsterno CHAR(5) REFERENCES PERSONALE(Matricola),"
                 "TipoEvento VARCHAR(10) NOT NULL, "
                 "Luogo VARCHAR(50) NOT NULL,"
                 "Data DATE NOT NULL,"
                 "Ora TIME NOT NULL, "
                 "PRIMARY KEY (MatrEsterno,TipoEvento,Luogo,Data,Ora), "
                 "FOREIGN KEY (TipoEvento,Luogo,Data,Ora) "
                 "REFERENCES EVENTO(TipoEvento,Luogo,Data,Ora));")

database.execute("CREATE TABLE IF NOT EXISTS ISCRIZIONE("
                 "MatrBambino CHAR(5) REFERENCES BAMBINO(Matricola),"
                 "TipoEvento VARCHAR(10) NOT NULL, "
                 "Luogo VARCHAR(50) NOT NULL,"
                 "Data DATE NOT NULL,"
                 "Ora TIME NOT NULL,"
                 "DataIscrizione DATE NOT NULL,"
                 "PRIMARY KEY (MatrBambino,TipoEvento,Luogo,Data,Ora),"
                 "FOREIGN KEY (TipoEvento,Luogo,Data,Ora) "
                 "REFERENCES EVENTO(TipoEvento,Luogo,Data,Ora));")

database.execute("CREATE TABLE IF NOT EXISTS PARTECIPA("
                 "NomeSquadra VARCHAR(10) REFERENCES SQUADRA(Nome),"
                 "TipoEvento VARCHAR(10) NOT NULL, "
                 "Luogo VARCHAR(50) NOT NULL,"
                 "Data DATE NOT NULL,"
                 "Ora TIME NOT NULL, "
                 "PRIMARY KEY (NomeSquadra,TipoEvento,Luogo,Data,Ora),"
                 "FOREIGN KEY (TipoEvento,Luogo,Data,Ora) "
                 "REFERENCES EVENTO(TipoEvento,Luogo,Data,Ora));")

# inizializzo il db inserendo un leader e un leader , un bambino e un animatore "fantocci" per gestire l'eliminazione
try:
    cursor.execute(
        "INSERT INTO PERSONALE VALUES ('00001','admin','Pinco','Pallino','admin@gmail.com','0000-1-1','via bella n.5',03598456,340586969,'leader');")
except:
    pass
try:
    cursor.execute(
        "INSERT INTO PERSONALE VALUES ('00000','admin','00000','XXXXXX','xxx@xxx.com','0000-1-1','xxxxxx',00000000,0000000,'leader');")
except:
    pass
try:
    cursor.execute(
        "INSERT INTO BAMBINO VALUES ('00002','00002','XXXXX','XXXXX','XXX@XX.IT','0000-1-1','XXXXX',00000,0000,'xxxx','yyyy','NULL')")
except:
    pass
try:
    cursor.execute(
        "INSERT INTO ANIMATORE VALUES ('00003','00003','XXXXX','XXXXX','XXXXX@XX.it','0000-1-1','XXXXX',00000,0000,'00000','NULL');")
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
def updateSessionData(partecipante, rows):
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
                updateSessionData(partecipante, rows)
                return redirect(url_for('root'))

    return render_template('login.html')


@app.route('/homeLEADER', methods=['GET', 'POST'])
def home_leader():
    if request.method == 'POST' and 'form_modifica' in request.form:
        database = sqlite3.connect(path)
        cursor = database.cursor();
        cursor.execute(
            "UPDATE PERSONALE SET Password = ?, Nome = ?, Cognome = ?, Email = ?, DataNascita = ?, Indirizzo = ?, NumTelefono = ?, NumCellulare = ? WHERE Matricola = ?;",
            [request.form['password'], request.form['nome'], request.form['cognome'], request.form['email'],
             request.form['data'],
             request.form['indirizzo'], request.form['telefono'], request.form['cellulare'], request.form['matricola']])
        rows = request.form['matricola'], request.form['password'], request.form['nome'], request.form[
            'cognome'], 'leader', request.form['email'], request.form['data'], request.form['indirizzo'], request.form[
                   'telefono'], request.form['cellulare']
        database.commit()
        database.close()
        updateSessionData('leader', rows)

    if request.method == 'POST' and 'form_appello' in request.form:
        presenza = request.form.get('options')
        data = request.form.get('dataappello')

        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")

        try:
            cursor = database.cursor();
            cursor.execute("INSERT INTO APPELLOPERSONALE(IdPersonale,Data,Presenza) VALUES (?,?,?) ",
                           [session['matricola'], data, presenza])
            database.commit()
        except:
            flash("Attenzione: Appello già compilato per questa giornata!")
        finally:
            database.close()

    if 'leader' in session:
        database = sqlite3.connect(path)
        cursor = database.cursor()

        cursor.execute(
            "SELECT TipoEvento, Luogo, Data, Ora, Descrizione FROM EVENTO WHERE MatrLeader = ? ORDER BY Data ASC, Ora ASC",
            [session['matricola']])
        listeventi = cursor.fetchall()
        database.close()
        return render_template("homeLEADER.html", usernamesession=session['nome'] + " " + session
        ['cognome'], matricola=session['matricola'], password=session['password'], nome=session['nome'],
                               cognome=session['cognome'], email=session['email'], data=session['dataNascita'],
                               indirizzo=session['indirizzo'],
                               telefono=session['numTelefono'], cellulare=session['numCellulare'], totalepartecipanti=(
                    totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini,
                               listeventi=listeventi)
    else:
        return redirect(url_for('login'))


@app.route('/homeSEGRETARIA', methods=['GET', 'POST'])
def home_segretaria():
    if request.method == 'POST' and 'form_modifica' in request.form:
        database = sqlite3.connect(path)
        cursor = database.cursor();
        cursor.execute(
            "UPDATE PERSONALE SET Password = ?, Nome = ?, Cognome = ?, Email = ?, DataNascita = ?, Indirizzo = ?, NumTelefono = ?, NumCellulare = ? WHERE Matricola = ?;",
            [request.form['password'], request.form['nome'], request.form['cognome'], request.form['email'],
             request.form['data'],
             request.form['indirizzo'], request.form['telefono'], request.form['cellulare'], request.form['matricola']])
        rows = request.form['matricola'], request.form['password'], request.form['nome'], request.form[
            'cognome'], 'leader', request.form['email'], request.form['data'], request.form['indirizzo'], request.form[
                   'telefono'], request.form['cellulare']
        database.commit()
        database.close()
        updateSessionData('segretaria', rows)

    elif request.method == 'POST' and 'form_elimina' in request.form:
        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")

        cursor = database.cursor();
        cursor.execute("DELETE FROM PERSONALE WHERE Matricola= ?;", [session['matricola']])
        database.commit()
        database.close()

        global totale_segretarie
        totale_segretarie -= 1

        return redirect(url_for("logout"))
    elif request.method == 'POST' and 'form_appello' in request.form:
        presenza = request.form.get('options')
        data = request.form.get('dataappello')

        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")

        try:
            cursor = database.cursor();
            cursor.execute("INSERT INTO APPELLOPERSONALE(IdPersonale,Data,Presenza) VALUES (?,?,?) ",
                           [session['matricola'], data, presenza])
            database.commit()
        except:
            flash("Attenzione: Appello già compilato per questa giornata!")
        finally:
            database.close()

    if 'segretaria' in session:
        database = sqlite3.connect(path)
        cursor = database.cursor()

        cursor.execute("SELECT TipoEvento, Luogo, Data, Ora, Descrizione FROM EVENTO ORDER BY Data ASC, Ora ASC")
        rows = cursor.fetchall()
        database.close()
        return render_template("homeSEGRETARIA.html", usernamesession=session['nome'] + " " + session
        ['cognome'], matricola=session['matricola'], password=session['password'], nome=session['nome'],
                               cognome=session['cognome'], email=session['email'], data=session['dataNascita'],
                               indirizzo=session['indirizzo'],
                               telefono=session['numTelefono'], cellulare=session['numCellulare'], totalepartecipanti=(
                    totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini,
                               listeventi=rows)
    else:
        return redirect(url_for('login'))


@app.route('/homeRESPONSABILE', methods=['GET', 'POST'])
def home_responsabile():
    if request.method == 'POST' and 'form_modifica' in request.form:
        database = sqlite3.connect(path)
        cursor = database.cursor();
        cursor.execute(
            "UPDATE PERSONALE SET Password = ?, Nome = ?, Cognome = ?, Email = ?, DataNascita = ?, Indirizzo = ?, NumTelefono = ?, NumCellulare = ? WHERE Matricola = ?;",
            [request.form['password'], request.form['nome'], request.form['cognome'], request.form['email'],
             request.form['data'],
             request.form['indirizzo'], request.form['telefono'], request.form['cellulare'], request.form['matricola']])
        rows = request.form['matricola'], request.form['password'], request.form['nome'], request.form[
            'cognome'], 'leader', request.form['email'], request.form['data'], request.form['indirizzo'], request.form[
                   'telefono'], request.form['cellulare']
        database.commit()
        database.close()
        updateSessionData('responsabile', rows)

    elif request.method == 'POST' and 'form_elimina' in request.form:
        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")

        cursor = database.cursor();
        cursor.execute("DELETE FROM PERSONALE WHERE Matricola= ?;", [session['matricola']])
        database.commit()
        database.close()
        global totale_responsabili
        totale_responsabili -= 1
        return redirect(url_for("logout"))
    elif request.method == 'POST' and 'form_appello' in request.form:
        presenza = request.form.get('options')
        data = request.form.get('dataappello')

        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")

        try:
            cursor = database.cursor();
            cursor.execute("INSERT INTO APPELLOPERSONALE(IdPersonale,Data,Presenza) VALUES (?,?,?) ",
                           [session['matricola'], data, presenza])
            database.commit()
        except:
            flash("Attenzione: Appello già compilato per questa giornata!")
        finally:
            database.close()

    if 'responsabile' in session:
        database = sqlite3.connect(path)
        cursor = database.cursor()

        cursor.execute("SELECT TipoEvento, Luogo, Data, Ora, Descrizione FROM EVENTO ORDER BY Data ASC, Ora ASC")
        rows = cursor.fetchall()

        cursor = database.cursor()

        cursor.execute(
            "SELECT E.TipoEvento, E.Luogo, E.Data, E.Ora, E.Descrizione FROM ARBITRA A JOIN EVENTO E ON (E.TipoEvento, E.Luogo, E.Data, E.Ora)=(A.TipoEvento, A.Luogo, A.Data, A.Ora) WHERE A.MatrResponsabile = ? ORDER BY E.Data ASC, E.Ora ASC",
            [session['matricola']])
        listgiochi = cursor.fetchall()

        database.close()
        return render_template("homeRESPONSABILE.html", usernamesession=session['nome'] + " " + session
        ['cognome'], matricola=session['matricola'], password=session['password'], nome=session['nome'],
                               cognome=session['cognome'], email=session['email'], data=session['dataNascita'],
                               indirizzo=session['indirizzo'],
                               telefono=session['numTelefono'], cellulare=session['numCellulare'], totalepartecipanti=(
                    totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader, totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini,
                               listeventi=rows,
                               tipologia="Animatori", listgiochi=listgiochi)
    else:
        return redirect(url_for('login'))


@app.route('/homeESTERNO', methods=['GET', 'POST'])
def home_esterno():
    if request.method == 'POST' and 'form_modifica' in request.form:
        database = sqlite3.connect(path)
        cursor = database.cursor();
        cursor.execute(
            "UPDATE PERSONALE SET Password = ?, Nome = ?, Cognome = ?, Email = ?, DataNascita = ?, Indirizzo = ?, NumTelefono = ?, NumCellulare = ? WHERE Matricola = ?;",
            [request.form['password'], request.form['nome'], request.form['cognome'], request.form['email'],
             request.form['data'],
             request.form['indirizzo'], request.form['telefono'], request.form['cellulare'], request.form['matricola']])
        rows = request.form['matricola'], request.form['password'], request.form['nome'], request.form[
            'cognome'], 'leader', request.form['email'], request.form['data'], request.form['indirizzo'], request.form[
                   'telefono'], request.form['cellulare']
        database.commit()
        database.close()
        updateSessionData('esterno', rows)

    elif request.method == 'POST' and 'form_elimina' in request.form:
        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")

        cursor = database.cursor();
        cursor.execute("DELETE FROM PERSONALE WHERE Matricola= ?;", [session['matricola']])
        database.commit()
        database.close()
        global totale_esterni
        totale_esterni -= 1
        return redirect(url_for("logout"))

    elif request.method == 'POST' and 'form_appello' in request.form:
        presenza = request.form.get('options')
        data = request.form.get('dataappello')

        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")

        try:
            cursor = database.cursor();
            cursor.execute("INSERT INTO APPELLOPERSONALE(IdPersonale,Data,Presenza) VALUES (?,?,?) ",
                           [session['matricola'], data, presenza])
            database.commit()
        except:
            flash("Attenzione: Appello già compilato per questa giornata!")
        finally:
            database.close()

    if 'esterno' in session:
        database = sqlite3.connect(path)
        cursor = database.cursor()

        cursor.execute(
            "SELECT E.TipoEvento,E.Luogo,E.Data,E.Ora,E.Descrizione,P.Nome,P.Cognome FROM EVENTO E JOIN GESTISCE G ON (E.TipoEvento,E.Luogo,E.Data,E.Ora) = (G.TipoEvento,G.Luogo,G.Data,G.Ora)  JOIN PERSONALE P ON E.MatrLeader= P.Matricola WHERE G.MatrEsterno = ?;",
            [session['matricola']])
        rows = cursor.fetchall()
        database.close()

        return render_template("homeESTERNO.html", usernamesession=session['nome'] + " " + session
        ['cognome'], matricola=session['matricola'], password=session['password'], nome=session['nome'],
                               cognome=session['cognome'], email=session['email'], data=session['dataNascita'],
                               indirizzo=session['indirizzo'],
                               telefono=session['numTelefono'], cellulare=session['numCellulare'], totalepartecipanti=(
                    totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini,
                               listlaboratori=rows)
    else:
        return redirect(url_for('login'))


@app.route('/homeANIMATORE', methods=['GET'])
def home_animatore():
    if request.method == 'POST' and 'form_modifica' in request.form:
        database = sqlite3.connect(path)
        cursor = database.cursor();
        cursor.execute(
            "UPDATE PERSONALE SET Password = ?, Nome = ?, Cognome = ?, Email = ?, DataNascita = ?, Indirizzo = ?, NumTelefono = ?, NumCellulare = ? WHERE Matricola = ?;",
            [request.form['password'], request.form['nome'], request.form['cognome'], request.form['email'],
             request.form['data'],
             request.form['indirizzo'], request.form['telefono'], request.form['cellulare'], request.form['matricola']])
        rows = request.form['matricola'], request.form['password'], request.form['nome'], request.form[
            'cognome'], 'leader', request.form['email'], request.form['data'], request.form['indirizzo'], request.form[
                   'telefono'], request.form['cellulare']
        database.commit()
        database.close()
        updateSessionData('animatore', rows)

    elif request.method == 'POST' and 'form_elimina' in request.form:
        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")

        cursor = database.cursor();
        cursor.execute("DELETE FROM PERSONALE WHERE Matricola= ?;", [session['matricola']])
        database.commit()
        database.close()
        global totale_animatori
        totale_animatori -= 1
        return redirect(url_for("logout"))

    if 'animatore' in session:
        database = sqlite3.connect(path)
        cursor = database.cursor()

        cursor.execute("SELECT E.TipoEvento, E.Luogo, E.Data, E.Ora, E.Descrizione FROM EVENTO E JOIN "
                       "PARTECIPA P ON (P.TipoEvento, P.Luogo, P.Data,P.Ora) = (E.TipoEvento, E.Luogo, E.Data,E.Ora) "
                       "JOIN ANIMATORE A ON A.NomeSquadra = P.NomeSquadra WHERE A.Matricola = ?  ORDER BY E.Data ASC, E.Ora ASC",
                       [session['matricola']])
        listeventi = cursor.fetchall()
        database.close()
        return render_template("homeANIMATORE.html", usernamesession=session['nome'] + " " + session
        ['cognome'], matricola=session['matricola'], password=session['password'], nome=session['nome'],
                               cognome=session['cognome'], email=session['email'], data=session['dataNascita'],
                               indirizzo=session['indirizzo'],
                               telefono=session['numTelefono'], cellulare=session['numCellulare'], totalepartecipanti=(
                    totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini,
                               listeventi=listeventi,
                               tipologia=session['nomeSquadra'])
    else:
        return redirect(url_for('login'))


@app.route('/homeBAMBINO', methods=['GET'])
def home_bambino():
    if request.method == 'POST' and 'form_modifica' in request.form:
        database = sqlite3.connect(path)
        cursor = database.cursor();
        cursor.execute(
            "UPDATE PERSONALE SET Password = ?, Nome = ?, Cognome = ?, Email = ?, DataNascita = ?, Indirizzo = ?, NumTelefono = ?, NumCellulare = ? WHERE Matricola = ?;",
            [request.form['password'], request.form['nome'], request.form['cognome'], request.form['email'],
             request.form['data'],
             request.form['indirizzo'], request.form['telefono'], request.form['cellulare'], request.form['matricola']])
        rows = request.form['matricola'], request.form['password'], request.form['nome'], request.form[
            'cognome'], 'leader', request.form['email'], request.form['data'], request.form['indirizzo'], request.form[
                   'telefono'], request.form['cellulare']
        database.commit()
        database.close()
        global totale_bambini
        totale_bambini -= 1
        updateSessionData('bambino', rows)

    elif request.method == 'POST' and 'form_elimina' in request.form:
        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")

        cursor = database.cursor();
        cursor.execute("DELETE FROM PERSONALE WHERE Matricola= ?;", [session['matricola']])
        database.commit()
        database.close()
        return redirect(url_for("logout"))

    if 'bambino' in session:
        database = sqlite3.connect(path)
        cursor = database.cursor()

        cursor.execute("SELECT E.TipoEvento, E.Luogo, E.Data, E.Ora, E.Descrizione FROM EVENTO E JOIN "
                       "PARTECIPA P ON (P.TipoEvento, P.Luogo, P.Data,P.Ora) = (E.TipoEvento, E.Luogo, E.Data,E.Ora) "
                       "JOIN BAMBINO B ON B.NomeSquadra = P.NomeSquadra WHERE B.Matricola = ?  ORDER BY E.Data ASC, E.Ora ASC",
                       [session['matricola']])
        listeventi = cursor.fetchall()
        database.close()
        return render_template("homeBAMBINO.html", usernamesession=session['nome'] + " " + session
        ['cognome'], matricola=session['matricola'], password=session['password'], nome=session['nome'],
                               cognome=session['cognome'], email=session['email'], data=session['dataNascita'],
                               indirizzo=session['indirizzo'],
                               telefono=session['numTelefono'], cellulare=session['numCellulare'], totalepartecipanti=(
                    totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini,
                               listeventi=listeventi)
    else:
        return redirect(url_for('login'))


@app.route('/loginerrato', methods=['GET'])
def loginerrato():
    flash("ATTENZIONE MATRICOLA O PASSWORD ERRATI!!!")
    return redirect(url_for('login'))


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


@app.route('/formInserisciResponsabile', methods=['GET', 'POST'])
def form_inserisci_responsabile():
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
            [matricola, password, nome, cognome, email, data, indirizzo, telefono, cellulare, 'responsabile'])

        database.commit()
        database.close()

        global totale_responsabili
        totale_responsabili += 1

        global matricola_max
        matricola_max += 1

        return redirect(url_for('form_inserisci_responsabile'))

    if 'leader' in session:
        return render_template("formInserisciResponsabile.html",
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


@app.route('/formInserisciEsterno', methods=['GET', 'POST'])
def form_inserisci_esterno():
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
        nomelaboratorio = request.form['nomelaboratorio']

        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")

        cursor = database.cursor()

        cursor.execute(
            "INSERT INTO PERSONALE VALUES (?,?,?,?,?,?,?,?,?,?);",
            [matricola, password, nome, cognome, email, data, indirizzo, telefono, cellulare, 'esterno'])

        database.commit()

        cursor = database.cursor()

        cursor.execute(
            "INSERT INTO GESTISCE VALUES (?,?,?,?,?);",
            [matricola, str(nomelaboratorio).split()[0], str(nomelaboratorio).split()[3],
             str(nomelaboratorio).split()[4], str(nomelaboratorio).split()[5]])
        database.commit()

        database.close()

        global totale_esterni
        totale_esterni += 1

        global matricola_max
        matricola_max += 1

        return redirect(url_for('form_inserisci_esterno'))

    if 'leader' in session:
        database = sqlite3.connect(path)
        cursor = database.cursor()
        cursor.execute(
            "SELECT TipoEvento, Descrizione,Luogo,Data,Ora FROM EVENTO WHERE CAST(TipoEvento as INTEGER) > 200 and CAST(TipoEvento as INTEGER) < 300")
        laboratori = cursor.fetchall()
        database.close()
        return render_template("formInserisciEsterno.html",
                               matricola=str((matricola_max + 1)).zfill(5),
                               usernamesession=session['nome'] + " " + session
                               ['cognome'], totalepartecipanti=(
                    totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader, totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni, totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini, listlaboratori=laboratori)
    else:
        return redirect(url_for('login'))


@app.route('/formInserisciAnimatore', methods=['GET', 'POST'])
def form_inserisci_animatore():
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
        matricolaresponsabile = request.form.get('matricolaresponsabile')
        nomesquadra = request.form.get('nomesquadra')

        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")

        cursor = database.cursor()
        cursor.execute(
            "INSERT INTO ANIMATORE VALUES (?,?,?,?,?,?,?,?,?,?,?);",
            [matricola, password, nome, cognome, email, data, indirizzo, telefono, cellulare, matricolaresponsabile,
             nomesquadra])
        database.commit()
        database.close()

        global totale_animatori
        totale_animatori += 1

        global matricola_max
        matricola_max += 1

        return redirect(url_for('form_inserisci_animatore'))

    if 'leader' in session:
        database = sqlite3.connect(path)
        cursor = database.cursor()
        cursor.execute("SELECT Nome  FROM SQUADRA")
        squadre = cursor.fetchall()

        cursor.execute("SELECT Matricola FROM PERSONALE WHERE Ruolo = 'responsabile'")
        matricole = cursor.fetchall()
        database.close()
        return render_template("formInserisciAnimatore.html",
                               matricola=str((matricola_max + 1)).zfill(5),
                               usernamesession=session['nome'] + " " + session['cognome'],
                               totalepartecipanti=(
                                       totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini,
                               matricole=matricole,
                               listsquadra=squadre)
    else:
        return redirect(url_for('login'))


@app.route('/formInserisciBambino', methods=['GET', 'POST'])
def form_inserisci_bambino():
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
        nominativopadre = request.form['nominativopadre']
        nominativomadre = request.form['nominativomadre']
        nomesquadra = request.form.get('nomesquadra')

        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")

        cursor = database.cursor()
        cursor.execute(
            "INSERT INTO BAMBINO VALUES (?,?,?,?,?,?,?,?,?,?,?,?);",
            [matricola, password, nome, cognome, email, data, indirizzo, telefono, cellulare, nominativomadre,
             nominativopadre,
             nomesquadra])

        database.commit()
        database.close()

        global totale_bambini
        totale_bambini += 1

        global matricola_max
        matricola_max += 1

        return redirect(url_for('form_inserisci_bambino'))

    if 'leader' in session:
        database = sqlite3.connect(path)
        cursor = database.cursor()
        cursor.execute("SELECT Nome  FROM SQUADRA")
        squadre = cursor.fetchall()
        database.close()
        return render_template("formInserisciBambino.html",
                               matricola=str((matricola_max + 1)).zfill(5),
                               usernamesession=session['nome'] + " " + session['cognome'],
                               totalepartecipanti=(
                                       totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini,
                               listsquadra=squadre)
    else:
        return redirect(url_for('login'))


@app.route('/formCreaGita', methods=['GET', 'POST'])
def form_crea_gita():
    if request.method == 'POST':
        tipoGita = request.form['tipoGita']
        luogo = request.form['luogo']
        date = request.form['date']
        time = request.form['time']
        descrizione = request.form['descrizione']

        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")

        cursor = database.cursor()

        # inserisco evento se non già inserito
        try:
            cursor.execute(
                "INSERT INTO EVENTO VALUES (?,?,?,?,?,?,?);",
                [tipoGita, luogo, date, time, descrizione, 'NULL', session['matricola']])
            database.commit()
        except:
            flash("Attenzione: gita già inserita!")
        finally:
            database.close()
        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")

        cursor = database.cursor()

        try:
            cursor.execute("SELECT Nome FROM SQUADRA")
            rows = cursor.fetchall()

            for squadra in rows:
                if request.form.get(squadra[0]) == "on":
                    partecipa = True;
                else:
                    partecipa = False
                cursor = database.cursor()
                # inserisco partecipazione se non già inserita
                if partecipa == True:
                    cursor.execute("INSERT INTO PARTECIPA VALUES (?,?,?,?,?);",
                                   [squadra[0], tipoGita, luogo, date, time])
                    cursor.fetchall()

            database.commit()
        except:
            flash("Attenzione: Almeno un squadra già partecipa all'evento")
        finally:
            database.close()

    if 'leader' in session:

        database = sqlite3.connect(path)
        cursor = database.cursor()

        cursor.execute("SELECT Nome FROM SQUADRA")
        listsquadre = cursor.fetchall()

        return render_template("formCreaGita.html", usernamesession=session['nome'] + " " + session
        ['cognome'], totalepartecipanti=(
                totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader, totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni, totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini, listsquadre=listsquadre)
    else:
        return redirect(url_for('login'))


@app.route('/formCreaGioco', methods=['GET', 'POST'])
def form_crea_gioco():
    if request.method == 'POST':
        tipoGioco = request.form['tipoGioco']
        luogo = request.form['luogo']
        date = request.form['date']
        time = request.form['time']
        descrizione = request.form['descrizione']
        punteggio = request.form['punteggio']

        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")

        cursor = database.cursor()

        # inserisco evento se non già inserito
        try:
            cursor.execute(
                "INSERT INTO EVENTO VALUES (?,?,?,?,?,?,?);",
                [tipoGioco, luogo, date, time, descrizione, punteggio, session['matricola']])

            cursor.fetchall()
            database.commit()
        except:
            flash("Attenzione: gioco già inserito!")
        finally:
            database.close()

        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")

        cursor = database.cursor()

        try:
            cursor.execute("SELECT Nome FROM SQUADRA")
            rows = cursor.fetchall()

            for squadra in rows:
                if request.form.get(squadra[0]) == "on":
                    partecipa = True;
                else:
                    partecipa = False
                cursor = database.cursor()
                # inserisco partecipazione se non già inserita
                if partecipa == True:
                    cursor.execute("INSERT INTO PARTECIPA VALUES (?,?,?,?,?);",
                                   [squadra[0], tipoGioco, luogo, date, time])
                    cursor.fetchall()

            database.commit()
        except:
            flash("Attenzione: Almeno un squadra già partecipa all'evento")
        finally:
            database.close()

    if 'leader' in session:
        database = sqlite3.connect(path)
        cursor = database.cursor()

        cursor.execute("SELECT Nome FROM SQUADRA")
        listsquadre = cursor.fetchall()

        return render_template("formCreaGioco.html", usernamesession=session['nome'] + " " + session
        ['cognome'], totalepartecipanti=(
                totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader, totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni, totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini, listsquadre=listsquadre)
    else:
        return redirect(url_for('login'))


@app.route('/formCreaLaboratorio', methods=['GET', 'POST'])
def form_crea_laboratorio():
    if request.method == 'POST':
        tipoLab = request.form['tipoLab']
        luogo = request.form['luogo']
        date = request.form['date']
        time = request.form['time']
        descrizione = request.form['descrizione']
        if str(request.form['nomeesterno']) != "":
            esterno = str(request.form['nomeesterno']).split()[0].lstrip()

        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")

        cursor = database.cursor()
        # inserisco evento se non già presente
        try:
            cursor.execute(
                "INSERT INTO EVENTO VALUES (?,?,?,?,?,?,?);",
                [tipoLab, luogo, date, time, descrizione, 'NULL', session['matricola']])
            if str(request.form['nomeesterno']) != "":
                cursor.execute(
                    "INSERT INTO GESTISCE(MatrEsterno,TipoEvento,Luogo,Data, Ora) VALUES (?,?,?,?,?);",
                    [esterno, tipoLab, luogo, date, time])

            cursor.fetchall()
            database.commit()
        except:
            flash("Attenzione: laboratorio già inserito!")
        finally:
            database.close()
        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")

        cursor = database.cursor()

        try:
            cursor.execute("SELECT Nome FROM SQUADRA")
            rows = cursor.fetchall()

            for squadra in rows:
                if request.form.get(squadra[0]) == "on":
                    partecipa = True;
                else:
                    partecipa = False
                cursor = database.cursor()
                # inserisco partecipazione se non già inserita
                if partecipa == True:
                    cursor.execute("INSERT INTO PARTECIPA VALUES (?,?,?,?,?);",
                                   [squadra[0], tipoLab, luogo, date, time])
                    cursor.fetchall()

            database.commit()
        except:
            flash("Attenzione: Almeno un squadra già partecipa all'evento")
        finally:
            database.close()

    if 'leader' in session:
        database = sqlite3.connect(path)
        cursor = database.cursor()

        cursor.execute(
            "SELECT Matricola,Nome,Cognome FROM PERSONALE WHERE Ruolo = 'esterno'")
        listesterni = cursor.fetchall()

        cursor.execute("SELECT Nome FROM SQUADRA")
        listsquadre = cursor.fetchall()

        database.close()
        return render_template("formCreaLaboratorio.html", usernamesession=session['nome'] + " " + session
        ['cognome'], totalepartecipanti=(
                totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader, totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni, totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini, listesterni=listesterni, listsquadre=listsquadre)
    else:
        return redirect(url_for('login'))


@app.route('/formCreaSquadra', methods=['GET', 'POST'])
def form_crea_squadra():
    if request.method == 'POST':
        nomesquadra = request.form['nomesquadra']
        coloresquadra = request.form['coloresquadra']
        mottosquadra = request.form['mottosquadra']

        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")

        cursor = database.cursor()

        try:
            cursor.execute(
                "INSERT INTO SQUADRA(Nome,Colore,Motto) VALUES (?,?,?);",
                [nomesquadra, coloresquadra, mottosquadra])

            cursor.fetchall()
            database.commit()

        except:
            flash("Attenzione: Squadra già inserita!")
        finally:
            database.close()

    if 'leader' in session:
        return render_template("formCreaSquadra.html", usernamesession=session['nome'] + " " + session
        ['cognome'], totalepartecipanti=(
                totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini)
    else:
        return redirect(url_for('login'))


@app.route('/formAggiungiMovimento', methods=['GET', 'POST'])
def form_aggiungi_movimento():
    if request.method == 'POST':
        tipoEvento = request.form['tipoEvento']
        descrizione = request.form['descrizione']
        valore = request.form['valore']
        if float(valore) >= 0:
            inout = 1
        else:
            inout = 0

        idEvento = set_id_evento(tipoEvento)

        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")

        cursor = database.cursor()

        try:
            cursor.execute(
                "INSERT INTO MOVIMENTO(TipoEvento,Luogo,Data, Ora, Descrizione, Valore, Inout, MatrSegretaria) VALUES (?,?,?,?,?,?,?,?);",
                [idEvento, str(tipoEvento).split(",")[1].lstrip(), str(tipoEvento).split(",")[2].lstrip(),
                 str(tipoEvento).split(",")[3].lstrip(),
                 descrizione, abs(float(valore)), inout, session['matricola']])

            database.commit()
        except:
            flash("Attenzione: Errore!")
        finally:
            database.close()

    if 'segretaria' in session:
        database = sqlite3.connect(path)
        cursor = database.cursor()
        cursor.execute(
            "SELECT TipoEvento, Luogo, Data, Ora, Descrizione FROM EVENTO ORDER BY Data ASC, Ora ASC")
        listeventi = cursor.fetchall()
        database.close()
        return render_template("formAggiungiMovimento.html", usernamesession=session['nome'] + " " + session
        ['cognome'], totalepartecipanti=(
                totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini,
                               listeventi=listeventi)
    else:
        return redirect(url_for('login'))


@app.route('/tabellaMovimenti', methods=['GET'])
def tabella_movimenti():
    if 'segretaria' in session:
        database = sqlite3.connect(path)
        cursor = database.cursor()
        cursor.execute(
            "SELECT TipoEvento, Luogo, Data, Ora, Descrizione,Valore,InOut,MatrSegretaria FROM MOVIMENTO ORDER BY Data ASC, Ora ASC")
        listmovimenti = cursor.fetchall()
        database.close()
        return render_template("tabellaMovimenti.html", usernamesession=session['nome'] + " " + session
        ['cognome'], totalepartecipanti=(
                totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini,
                               listmovimenti=listmovimenti)
    else:
        return redirect(url_for('login'))


@app.route('/formAssegnaArbitraggio', methods=['GET', 'POST'])
def assegna_arbitraggio():
    if request.method == 'POST':
        giocoselezionato = request.form['nomegioco']
        responsabileselezionato = str(request.form['nomeresponsabile']).split()[0].lstrip()

        idEvento = set_id_evento(giocoselezionato)

        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")

        cursor = database.cursor()
        try:
            cursor.execute(
                "INSERT INTO ARBITRA(MatrResponsabile,TipoEvento,Luogo,Data, Ora) VALUES (?,?,?,?,?);",
                [responsabileselezionato, idEvento, str(giocoselezionato).split(",")[1].lstrip(),
                 str(giocoselezionato).split(",")[2].lstrip(), str(giocoselezionato).split(",")[3].lstrip()])

            database.commit()
        except Exception as e:
            flash("Attenzione: Arbitraggio già inserito!")
        finally:
            database.close()

    if 'leader' in session:
        database = sqlite3.connect(path)
        cursor = database.cursor()
        cursor.execute(
            "SELECT TipoEvento, Luogo, Data, Ora, Descrizione FROM EVENTO WHERE MatrLeader = ? and CAST(TipoEvento as INTEGER) > 100 and CAST(TipoEvento as INTEGER)  < 201 ORDER BY Data ASC, Ora ASC",
            [session['matricola']])
        listgiochi = cursor.fetchall()

        cursor = database.cursor()
        cursor.execute(
            "SELECT Matricola,Nome,Cognome FROM PERSONALE WHERE Ruolo = 'responsabile'")
        listresponsabili = cursor.fetchall()

        database.close()

        return render_template("formAssegnaArbitraggio.html", usernamesession=session['nome'] + " " + session
        ['cognome'], totalepartecipanti=(
                totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini,
                               listresponsabili=listresponsabili,
                               listgiochi=listgiochi)
    else:
        return redirect(url_for('login'))


@app.route('/formAggiungiAppello', methods=['GET', 'POST'])
def form_aggiungi_appello():
    if request.method == 'POST':
        data = request.form['date']
        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")
        cursor = database.cursor()
        if 'animatore' in session:
            cursor.execute("SELECT Matricola FROM BAMBINO WHERE NomeSquadra = ?", [session['nomeSquadra']])
        elif 'responsabile' in session:
            cursor.execute("SELECT Matricola FROM ANIMATORE WHERE MatrResponsabile = ?", [session['matricola']])
        rows = cursor.fetchall()

        try:
            for matricola in rows:
                if request.form.get(matricola[0]) == "on":
                    presente = 1;
                else:
                    presente = 0
                cursor = database.cursor()
                # inserisco appello se non già inserito
                if 'animatore' in session:
                    cursor.execute(
                        "INSERT INTO APPELLOBAMBINO VALUES (?,?,?);",
                        [matricola[0], data, presente])
                elif 'responsabile' in session:
                    cursor.execute(
                        "INSERT INTO APPELLOANIMATORE VALUES (?,?,?);",
                        [matricola[0], data, presente])
                cursor.fetchall()

            database.commit()
        except:
            flash("Attenzione: Appello già compilato per questa giornata!")
        finally:
            database.close()

    if 'animatore' in session:
        database = sqlite3.connect(path)
        cursor = database.cursor()
        cursor.execute(
            "SELECT Matricola, Nome, Cognome FROM BAMBINO WHERE NomeSquadra = ?", [session['nomeSquadra']])
        rows = cursor.fetchall()
        database.close()

        return render_template("formAggiungiAppello.html", usernamesession=session['nome'] + " " + session
        ['cognome'], matricola=session['matricola'], password=session['password'], nome=session['nome'],
                               cognome=session['cognome'], email=session['email'], data=session['dataNascita'],
                               indirizzo=session['indirizzo'],
                               telefono=session['numTelefono'], cellulare=session['numCellulare'], totalepartecipanti=(
                    totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini,
                               bambini=rows,
                               tipologia=session['nomeSquadra'])

    elif 'responsabile' in session:
        database = sqlite3.connect(path)
        cursor = database.cursor()
        cursor.execute(
            "SELECT Matricola, Nome, Cognome FROM ANIMATORE WHERE MatrResponsabile = ?", [session['matricola']])
        rows = cursor.fetchall()
        database.close()

        return render_template("formAggiungiAppello.html", usernamesession=session['nome'] + " " + session
        ['cognome'], matricola=session['matricola'], password=session['password'], nome=session['nome'],
                               cognome=session['cognome'], email=session['email'], data=session['dataNascita'],
                               indirizzo=session['indirizzo'],
                               telefono=session['numTelefono'], cellulare=session['numCellulare'], totalepartecipanti=(
                    totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini,
                               bambini=rows,
                               tipologia="Animatori")
    else:
        return redirect(url_for('login'))


@app.route('/formMostraAppello', methods=['GET', 'POST'])
def form_mostra_appello():
    if request.method == 'POST':
        data = request.form['date']
        database = sqlite3.connect(path)
        cursor = database.cursor()
        if 'animatore' in session:
            cursor.execute(
                "SELECT A.IdBambino, B.Nome, B.Cognome, A.Presenza FROM BAMBINO B JOIN APPELLOBAMBINO A ON (A.IdBambino = B.Matricola) WHERE A.Data = ?",
                [data])
            tipologia = session['nomeSquadra']
        elif 'responsabile' in session:
            cursor.execute(
                "SELECT A.IdAnimatore, B.Nome, B.Cognome, A.Presenza FROM ANIMATORE B JOIN APPELLOANIMATORE A ON (A.IdAnimatore = B.Matricola) WHERE B.MatrResponsabile = ? AND A.Data = ?",
                [session['matricola'], data])
            tipologia = "Animatori"
        elif 'leader' in session:
            cursor.execute(
                "SELECT A.IdPersonale, Nome, Cognome, Presenza FROM APPELLOPERSONALE A JOIN PERSONALE P ON A.IdPersonale = P.Matricola  WHERE A.Data = ? ",
                [data])
            tipologia = "Personale"

        rows = cursor.fetchall()
        database.close()
        return render_template("formMostraAppello.html", usernamesession=session['nome'] + " " + session
        ['cognome'], matricola=session['matricola'], password=session['password'], nome=session['nome'],
                               cognome=session['cognome'], email=session['email'], data=session['dataNascita'],
                               indirizzo=session['indirizzo'],
                               telefono=session['numTelefono'], cellulare=session['numCellulare'], totalepartecipanti=(
                    totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini,
                               bambini=rows,
                               tipologia=tipologia)

    if 'animatore' in session:
        return render_template("formMostraAppello.html", usernamesession=session['nome'] + " " + session
        ['cognome'], matricola=session['matricola'], password=session['password'], nome=session['nome'],
                               cognome=session['cognome'], email=session['email'], data=session['dataNascita'],
                               indirizzo=session['indirizzo'],
                               telefono=session['numTelefono'], cellulare=session['numCellulare'], totalepartecipanti=(
                    totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini,
                               tipologia=session['nomeSquadra'])

    elif 'responsabile' in session:
        return render_template("formMostraAppello.html", usernamesession=session['nome'] + " " + session
        ['cognome'], matricola=session['matricola'], password=session['password'], nome=session['nome'],
                               cognome=session['cognome'], email=session['email'], data=session['dataNascita'],
                               indirizzo=session['indirizzo'],
                               telefono=session['numTelefono'], cellulare=session['numCellulare'], totalepartecipanti=(
                    totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini,
                               tipologia="Animatori"
                               )
    elif 'leader' in session:
        return render_template("formMostraAppello.html", usernamesession=session['nome'] + " " + session
        ['cognome'], matricola=session['matricola'], password=session['password'], nome=session['nome'],
                               cognome=session['cognome'], email=session['email'], data=session['dataNascita'],
                               indirizzo=session['indirizzo'],
                               telefono=session['numTelefono'], cellulare=session['numCellulare'], totalepartecipanti=(
                    totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini,
                               tipologia="Personale"
                               )
    else:
        return redirect(url_for('login'))


@app.route('/formInserisciIscrizioneGita', methods=['GET', 'POST'])
def form_iscrizione_gita():
    if request.method == 'POST':
        tipoEvento = request.form.get('gita')

        idEvento = set_id_evento(tipoEvento)
        dataiscrizione = request.form.get('dataiscrizione')

        database = sqlite3.connect(path)
        database.execute("PRAGMA foreign_keys = 1")

        cursor = database.cursor()

        try:
            cursor.execute(
                "INSERT INTO ISCRIZIONE(MatrBambino,TipoEvento,Luogo,Data, Ora, DataIscrizione) VALUES (?,?,?,?,?,?);",
                [session['matricola'], idEvento, str(tipoEvento).split(",")[1].lstrip(),
                 str(tipoEvento).split(",")[2].lstrip(),
                 str(tipoEvento).split(",")[3].lstrip(),dataiscrizione])

            database.commit()
        except Exception as e:
            flash("Attenzione: Errore! Iscrizione già inserita")
        finally:
            database.close()

    if 'bambino' in session:
        database = sqlite3.connect(path)
        cursor = database.cursor()

        cursor.execute("SELECT E.TipoEvento, E.Luogo, E.Data, E.Ora, E.Descrizione FROM EVENTO E JOIN "
                       "PARTECIPA P ON (P.TipoEvento, P.Luogo, P.Data,P.Ora) = (E.TipoEvento, E.Luogo, E.Data,E.Ora) "
                       "JOIN BAMBINO B ON B.NomeSquadra = P.NomeSquadra WHERE B.Matricola = ? AND CAST(E.TipoEvento as INTEGER) <101"
                       " AND (?,E.TipoEvento, E.Luogo, E.Data, E.Ora) NOT IN (SELECT I.MatrBambino,I.TipoEvento, I.Luogo, I.Data, I.Ora FROM ISCRIZIONE I)  "
                       "ORDER BY E.Data ASC, E.Ora ASC",
                       [session['matricola'], session['matricola']])
        listgite = cursor.fetchall()
        database.close()

        return render_template("formInserisciIscrizioneGita.html", usernamesession=session['nome'] + " " + session
        ['cognome'], matricola=session['matricola'], password=session['password'], nome=session['nome'],
                               cognome=session['cognome'], email=session['email'], data=session['dataNascita'],
                               indirizzo=session['indirizzo'],
                               telefono=session['numTelefono'], cellulare=session['numCellulare'], totalepartecipanti=(
                    totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini, listgite=listgite)
    else:
        return redirect(url_for('login'))


@app.route('/formAssegnaPunteggio', methods=['GET', 'POST'])
def form_assegna_punteggio():
    if request.method == 'POST' and 'form_evento' in request.form:
        tipoEvento = request.form['tipoEvento']
        idEvento = set_id_evento(tipoEvento)
        database = sqlite3.connect(path)
        cursor = database.cursor()
        cursor.execute("SELECT NomeSquadra FROM PARTECIPA WHERE TipoEvento = ? AND Luogo = ? AND Data = ? AND Ora = ?",
                       [idEvento, str(tipoEvento).split(",")[1].lstrip(), str(tipoEvento).split(",")[
                           2].lstrip(), str(tipoEvento).split(",")[3].lstrip()])
        listsquadre = cursor.fetchall()
        database.close()
        return render_template("formAssegnaPunteggio.html", usernamesession=session['nome'] + " " + session
        ['cognome'], matricola=session['matricola'], password=session['password'], nome=session['nome'],
                               cognome=session['cognome'], email=session['email'], data=session['dataNascita'],
                               indirizzo=session['indirizzo'],
                               telefono=session['numTelefono'], cellulare=session['numCellulare'], totalepartecipanti=(
                    totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini,
                               listsquadre=listsquadre,
                               stato="getsquadre",
                               event=tipoEvento)

    elif request.method == 'POST' and 'form_assegna' in request.form:
        squadra = request.form['squadra']
        tipoEvento = request.form['event']
        idEvento = set_id_evento(tipoEvento)
        database = sqlite3.connect(path)
        cursor = database.cursor()
        cursor.execute("SELECT Punteggio FROM EVENTO WHERE TipoEvento = ? AND Luogo = ? AND Data = ? AND Ora = ?",
                       [idEvento, str(tipoEvento).split(",")[1].lstrip(), str(tipoEvento).split(",")[
                           2].lstrip(), str(tipoEvento).split(",")[3].lstrip()])
        punteggio = cursor.fetchone()
        cursor = database.cursor()
        cursor.execute(
            "UPDATE SQUADRA SET PUNTEGGIO = PUNTEGGIO + " + str(punteggio[0]) + " WHERE Nome = ? ", [squadra])
        cursor = database.cursor()
        cursor.execute("UPDATE EVENTO SET Punteggio = 0 WHERE TipoEvento = ?  AND Luogo = ? AND Data = ? AND Ora = ?",
                       [idEvento, str(tipoEvento).split(",")[1].lstrip(), str(tipoEvento).split(",")[
                           2].lstrip(), str(tipoEvento).split(",")[3].lstrip()])

        database.commit()
        database.close()

    if 'responsabile' in session:
        database = sqlite3.connect(path)
        cursor = database.cursor()
        cursor.execute(
            "SELECT E.TipoEvento, E.Luogo, E.Data, E.Ora, E.Descrizione FROM ARBITRA A JOIN EVENTO E ON (E.TipoEvento, E.Luogo, E.Data, E.Ora)=(A.TipoEvento, A.Luogo, A.Data, A.Ora) WHERE A.MatrResponsabile = ? AND PUNTEGGIO > 0 ORDER BY E.Data ASC, E.Ora ASC",
            [session['matricola']])
        listgiochi = cursor.fetchall()

        database.close()
        return render_template("formAssegnaPunteggio.html", usernamesession=session['nome'] + " " + session
        ['cognome'], matricola=session['matricola'], password=session['password'], nome=session['nome'],
                               cognome=session['cognome'], email=session['email'], data=session['dataNascita'],
                               indirizzo=session['indirizzo'],
                               telefono=session['numTelefono'], cellulare=session['numCellulare'], totalepartecipanti=(
                    totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini,
                               listgiochi=listgiochi,
                               stato="geteventi")
    else:
        return redirect(url_for('login'))


@app.route('/formMostraClassifica', methods=['GET', 'POST'])
def form_mostra_classifica():
    if 'responsabile' in session:
        database = sqlite3.connect(path)
        cursor = database.cursor()
        cursor.execute("SELECT Nome, Punteggio FROM SQUADRA ORDER BY Punteggio DESC")
        listsquadre = cursor.fetchall()

        database.close()
        return render_template("formMostraClassifica.html", usernamesession=session['nome'] + " " + session
        ['cognome'], matricola=session['matricola'], password=session['password'], nome=session['nome'],
                               cognome=session['cognome'], email=session['email'], data=session['dataNascita'],
                               indirizzo=session['indirizzo'],
                               telefono=session['numTelefono'], cellulare=session['numCellulare'], totalepartecipanti=(
                    totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini,
                               listsquadre=listsquadre)
    else:
        return redirect(url_for('login'))


@app.route('/formMostraAppelloGita', methods=['GET', 'POST'])
def form_mostra_appello_gita():
    if request.method == 'POST':
        tipoEvento = request.form['tipoEvento']
        idEvento = set_id_evento(tipoEvento)
        database = sqlite3.connect(path)
        cursor = database.cursor()

        cursor.execute(
            "SELECT B.Matricola, B.Nome, B.Cognome, B.DataNascita, B.NumTelefono FROM BAMBINO B JOIN ISCRIZIONE I ON (B.Matricola) = (I.MatrBambino) WHERE I.TipoEvento = ? AND I.Luogo = ?  AND I.Data = ? "
            " AND I.Ora = ?  AND B.NomeSquadra = ? ", [idEvento, str(tipoEvento).split(",")[1].lstrip(),
                                                       str(tipoEvento).split(",")[2].lstrip(),
                                                       str(tipoEvento).split(",")[3].lstrip(), session['nomeSquadra']])
        listbimbi = cursor.fetchall()

        print(listbimbi)

        cursor = database.cursor()
        cursor.execute(
            "SELECT TipoEvento, Luogo, Data, Ora FROM PARTECIPA  WHERE NomeSquadra = ?  AND CAST(TipoEvento as INTEGER) > 0 AND CAST(TipoEvento as INTEGER) < 101 ",
            [session['nomeSquadra']])
        listgite = cursor.fetchall()
        database.close()

        return render_template("formMostraAppelloGita.html", usernamesession=session['nome'] + " " + session
        ['cognome'], matricola=session['matricola'], password=session['password'], nome=session['nome'],
                               cognome=session['cognome'], email=session['email'], data=session['dataNascita'],
                               indirizzo=session['indirizzo'],
                               telefono=session['numTelefono'], cellulare=session['numCellulare'], totalepartecipanti=(
                    totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini,
                               listbimbi=listbimbi,
                               tipologia=session['nomeSquadra'],
                               tipo="MostraTab",
                               event=tipoEvento,
                               listgite=listgite)
    if 'animatore' in session:
        database = sqlite3.connect(path)
        cursor = database.cursor()
        cursor.execute(
            "SELECT TipoEvento, Luogo, Data, Ora FROM PARTECIPA  WHERE NomeSquadra = ?  AND CAST(TipoEvento as INTEGER) > 0 AND CAST(TipoEvento as INTEGER) < 101",
            [session['nomeSquadra']])
        listgite = cursor.fetchall()

        database.close()
        return render_template("formMostraAppelloGita.html", usernamesession=session['nome'] + " " + session
        ['cognome'], matricola=session['matricola'], password=session['password'], nome=session['nome'],
                               cognome=session['cognome'], email=session['email'], data=session['dataNascita'],
                               indirizzo=session['indirizzo'],
                               telefono=session['numTelefono'], cellulare=session['numCellulare'], totalepartecipanti=(
                    totale_leader + totale_segretarie + totale_esterni + totale_responsabili + totale_animatori + totale_bambini),
                               totaleleader=totale_leader,
                               totalesegretarie=totale_segretarie,
                               totaleresponsabili=totale_responsabili,
                               totaleesterni=totale_esterni,
                               totaleanimatori=totale_animatori,
                               totalebambini=totale_bambini,
                               tipologia=session['nomeSquadra'],
                               listgite=listgite)
    else:
        return redirect(url_for('login'))


def set_id_evento(tipoEvento):
    if str(tipoEvento).split(",")[0].__contains__("CUCINA"):
        return "201"
    elif str(tipoEvento).split(",")[0].__contains__("PITTURA"):
        return "202"
    elif str(tipoEvento).split(",")[0].__contains__("CIRCO"):
        return "203"
    elif str(tipoEvento).split(",")[0].__contains__("COMPITI"):
        return "204"
    elif str(tipoEvento).split(",")[0].__contains__("MUSICA"):
        return "205"
    elif str(tipoEvento).split(",")[0].__contains__("ALTRO LABORATORIO"):
        return "206"
    elif str(tipoEvento).split(",")[0].__contains__("CALCIO"):
        return "101"
    elif str(tipoEvento).split(",")[0].__contains__("PALLAVOLO"):
        return "102"
    elif str(tipoEvento).split(",")[0].__contains__("PALLA PRIGIONIERA"):
        return "103"
    elif str(tipoEvento).split(",")[0].__contains__("CACCIA AL TESORO"):
        return "104"
    elif str(tipoEvento).split(",")[0].__contains__("ALTRO GIOCO"):
        return "105"
    elif str(tipoEvento).split(",")[0].__contains__("GITA IN MONTAGNA"):
        return "1"
    elif str(tipoEvento).split(",")[0].__contains__("GITA AL MARE"):
        return "2"
    elif str(tipoEvento).split(",")[0].__contains__("GITA AL LAGO"):
        return "3"
    elif str(tipoEvento).split(",")[0].__contains__("GITA CULTURALE"):
        return "4"
    elif str(tipoEvento).split(",")[0].__contains__("ALTRA GITA"):
        return "5"


app.run(host="127.0.0.1", port=5000, debug='true')
