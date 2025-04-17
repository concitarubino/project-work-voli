# Project Work – Dalla modellazione dei dati al backend: un sistema per la gestione dei voli

Questo progetto è stato realizzato come Project Work universitario.  
Traccia: Progettazione di uno schema di persistenza dei dati a supporto dei servizi di un’azienda nel settore dei trasporti.

---

## Contenuto del progetto

- `requirements.txt` → liberie necessarie
- `main.py` → Avvio dell'app FastAPI e definizione degli endpoint
- `crud.py` → Query SQL e logica dei dati
- `modelli.py`, `schemi.py` → Modelli SQLAlchemy e schemi Pydantic
- `configurazione.py` → parametri di connessione al database
- `database.sql` → Script per la creazione delle tabelle e degli indici
- `dati_test.sql` → Dati test realistici per tabelle statiche (aeroporti, voli, scali, clienti, posti)
- `test_api.json` → Dati test realistici per tabelle dinamiche (prenotazioni, bagagli, pagamenti)
- `test_api_runner.py` → Script Python per eseguire automaticamente i test e popolare le tabelle dinamiche
- `query_test.sql` → Query sql che ho utilizzato in crud.py
- `Diagramma E-R.png` → Schema E-R del database

---

## Configurazione ambiente
Per collegarti al database, crea un file .env nella root del progetto con:
```bash
DATABASE_URL=mysql+pymysql://<user>:<password>@localhost/trasporto_aereo
```
dove inserire user e password personali

---

## Come avviare il progetto

1. Esegui il file database.sql per creare la struttura del database e gli indici

2. Esegui il file dati_test.sql per popolare le tabelle statiche

3. Installa le dipendenze:
```bash
pip install -r requirements.txt
```
4. Avvia il server con:
```bash
python main.py
```
5. In un nuovo terminale, esegui:
```bash
python test_api_runner.py
```
Questo popola le tabelle dinamiche (Prenotazione, Bagagli, Pagamenti) usando il file test_api.json.
In alternativa, è comunque possibile utilizzare la documentazione interattiva generata da FastAPI (Swagger) per inserire dati ed effettuare chiamate.

6. Apri il browser e vai su:
http://127.0.0.1:8000/docs
per utilizzare Swagger UI e testare le API da interfaccia grafica.

---

## Funzionalità

- Ricerca voli per città e data, con gestione degli scali
- Prenotazione con assegnazione automatica del codice e calcolo del prezzo
- Pagamento e generazione automatica del biglietto
- Controllo reale dei posti disponibili (evita doppie prenotazioni)
- Visualizzazione biglietti e prenotazioni per cliente
- Query SQL avanzate integrate negli endpoint (JOIN, GROUP_CONCAT, COALESCE…)

---

## Autrice

Concetta Rubino  
GitHub → https://github.com/concitarubino


