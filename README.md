# Project Work – Gestione voli e prenotazioni

Questo progetto è stato realizzato come Project Work universitario.  
L'obiettivo è la progettazione di uno schema di persistenza dei dati a supporto dei servizi di un’azienda nel settore dei trasporti.

---

## Contenuto del progetto

- `main.py` → Avvio dell'app FastAPI e definizione degli endpoint
- `crud.py` → Query SQL e logica dei dati
- `modelli.py`, `schemi.py` → Modelli SQLAlchemy e schemi Pydantic
- `configurazione.py` → parametri di connessione al database
- `database.sql` → Script per la creazione delle tabelle e degli indici
- `dati_test.sql` → Script con dati di test realistici
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

1.Installa le dipendenze:
```bash
pip install -r requirements.txt
```
2.Avvia il server con:
```bash
python main.py
```
3.Apri il browser e vai su:
http://127.0.0.1:8000/docs
per usare l’API da interfaccia grafica tramite Swagger UI.

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
