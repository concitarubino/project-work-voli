from sqlalchemy.orm import Session
from sqlalchemy import func, text
from modelli import Prenotazione, Bagaglio, Pagamento, Biglietto, Cliente
from schemi import PagamentoSchema, ClienteSchema, PrenotazioneSchema
from fastapi import HTTPException

def crea_cliente(db: Session, cliente: ClienteSchema) -> Cliente:
    db_cliente = Cliente(**cliente.model_dump())
    db.add(db_cliente)
    db.commit()
    db.refresh(db_cliente)
    return db_cliente

def create_prenotazione(db: Session, prenotazione: PrenotazioneSchema) -> Prenotazione:
    db_prenotazione = Prenotazione(**prenotazione.model_dump())
    db.add(db_prenotazione)
    db.commit()
    db.refresh(db_prenotazione)
    return db_prenotazione

def salva_pagamento(db: Session, pagamento: PagamentoSchema) -> Pagamento:
    prenotazione = db.query(Prenotazione).filter(
        Prenotazione.ID_prenotazione == pagamento.ID_prenotazione
    ).first()

    if not prenotazione:
        raise HTTPException(status_code=404, detail="Prenotazione non trovata")

    if prenotazione.Stato == "Pagata":
        raise HTTPException(status_code=400, detail="Questa prenotazione è già stata pagata")

    if prenotazione.Stato == "Annullata":
        raise HTTPException(status_code=400, detail="Non è possibile effettuare il pagamento: prenotazione annullata")

    existing = db.query(Pagamento).filter(
        Pagamento.ID_prenotazione == pagamento.ID_prenotazione
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Pagamento già registrato per questa prenotazione")

    pagamento_data = pagamento.model_dump()
    pagamento_data["Importo"] = prenotazione.Prezzo

    db_pagamento = Pagamento(**pagamento_data)
    db.add(db_pagamento)
    db.commit()
    db.refresh(db_pagamento)

    return db_pagamento

def aggiorna_stato_prenotazione(db: Session, id_prenotazione: int, nuovo_stato: str) -> Prenotazione:
    prenotazione = db.query(Prenotazione).filter(Prenotazione.ID_prenotazione == id_prenotazione).first()
    if not prenotazione:
        raise HTTPException(status_code=404, detail="Prenotazione non trovata")
    prenotazione.Stato = nuovo_stato
    db.commit()
    return prenotazione

def crea_biglietto(db: Session, id_prenotazione: int) -> Biglietto:
    prenotazione = db.query(Prenotazione).filter(Prenotazione.ID_prenotazione == id_prenotazione).first()
    if not prenotazione:
        raise HTTPException(status_code=404, detail="Prenotazione non trovata")
    existing = db.query(Biglietto).filter(Biglietto.ID_prenotazione == id_prenotazione).first()
    if existing:
        return existing
    biglietto = Biglietto(
        ID_prenotazione = id_prenotazione,
        Prezzo = prenotazione.Prezzo,
        Stato_biglietto = "Prenotato" 
    )
    db.add(biglietto)
    db.commit()
    db.refresh(biglietto)
    return biglietto

def gestisci_pagamento(db: Session, pagamento: PagamentoSchema) -> Pagamento:
    db_pagamento = salva_pagamento(db, pagamento)

    if db_pagamento.Stato == "Completato":
        aggiorna_stato_prenotazione(db, db_pagamento.ID_prenotazione, "Pagata")
        crea_biglietto(db, db_pagamento.ID_prenotazione)
    elif db_pagamento.Stato == "Rifiutato":
        aggiorna_stato_prenotazione(db, db_pagamento.ID_prenotazione, "Annullata")
        raise HTTPException(status_code=400, detail="Pagamento rifiutato, prenotazione annullata")

    return db_pagamento

def calcola_prezzo_bagaglio(tipo: str) -> float:
    if tipo == "Standard":
        return 0.00
    elif tipo == "Cabina":
        return 30.00
    elif tipo == "Stiva":
        return 50.00
    else:
        raise ValueError("Tipo di bagaglio non valido")

def calcola_prezzo_prenotazione(db: Session, id_prenotazione: int) -> float:
    prenotazione = db.query(Prenotazione).filter(Prenotazione.ID_prenotazione == id_prenotazione).first()
    if not prenotazione:
        raise HTTPException(status_code=404, detail="Prenotazione non trovata")
    prezzo_bagagli = db.query(func.coalesce(func.sum(Bagaglio.Prezzo), 0)).filter(Bagaglio.ID_prenotazione == id_prenotazione).scalar()
    return float(prenotazione.Prezzo) + float(prezzo_bagagli)

def genera_codice_prenotazione(db: Session) -> str:
    next_id = db.execute(
        text("SELECT AUTO_INCREMENT FROM information_schema.TABLES WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'Prenotazione'")
    ).scalar()
    return f"PN{str(next_id).zfill(6)}"

# QUERY

# 1. Voli disponibili da un aeroporto in una data
def get_voli_disponibili(db: Session, citta: str, data: str):
    query = text("""
    SELECT 
        V.Codice_volo, 
        CONCAT(A1.Citta, ' (', A1.Codice_IATA, ')') AS Partenza,
        CONCAT(A2.Citta, ' (', A2.Codice_IATA, ')') AS Destinazione,
        DATE_FORMAT(V.Data_partenza, '%d/%m/%Y') AS Data_partenza, 
        TIME_FORMAT(V.Ora_partenza, '%H:%i') AS Ora_partenza,
        DATE_FORMAT(V.Data_arrivo, '%d/%m/%Y') AS Data_arrivo,
        TIME_FORMAT(V.Ora_arrivo, '%H:%i') AS Ora_arrivo,
        TIME_FORMAT(
            TIMEDIFF(TIMESTAMP(V.Data_arrivo, V.Ora_arrivo), TIMESTAMP(V.Data_partenza, V.Ora_partenza)), 
            '%Hh %im') AS Durata_volo,
        CONCAT(FORMAT(V.Prezzo, 2), ' €') AS Prezzo,
        COALESCE(
            GROUP_CONCAT(
                CONCAT(A3.Citta, ' (', A3.Codice_IATA, ') - Arrivo: ', S.Ora_arrivo,
                ', Partenza: ', S.Ora_partenza, ', Durata scalo: ',
                TIME_FORMAT(TIMEDIFF(TIMESTAMP(S.Ora_partenza), TIMESTAMP(S.Ora_arrivo)), '%Hh %im'))
            SEPARATOR ' | '), 
        'Nessuno') AS Scali
    FROM Volo V
    JOIN Aeroporto A1 ON V.ID_aeroporto_partenza = A1.ID_aeroporto
    JOIN Aeroporto A2 ON V.ID_aeroporto_arrivo = A2.ID_aeroporto
    LEFT JOIN Scalo S ON V.ID_volo = S.ID_volo
    LEFT JOIN Aeroporto A3 ON S.ID_aeroporto = A3.ID_aeroporto
    WHERE A1.Citta = :citta
      AND V.Data_partenza = :data
      AND EXISTS (
        SELECT 1
        FROM Posto P
        LEFT JOIN Prenotazione PR ON PR.ID_posto = P.ID_posto AND PR.ID_volo = V.ID_volo
        LEFT JOIN Biglietto B ON B.ID_prenotazione = PR.ID_prenotazione
        WHERE P.ID_volo = V.ID_volo
          AND (
            PR.ID_prenotazione IS NULL
            OR PR.Stato = 'Annullata'
          )
      )
    GROUP BY V.ID_volo
    ORDER BY V.Ora_partenza;
    """)

    result = db.execute(query, {"citta": citta, "data": data})
    return result.mappings().all()

# 2. Biglietti acquistati
def get_biglietti_cliente(db: Session, email: str):
    query = text("""
    SELECT
        P.Codice_prenotazione,
        V.Codice_volo,
        CONCAT(A1.Citta, ' (', A1.Codice_IATA, ')') AS Partenza,
        CONCAT(A2.Citta, ' (', A2.Codice_IATA, ')') AS Arrivo,
        DATE_FORMAT(V.Data_partenza, '%d/%m/%Y') AS Data_partenza,
        TIME_FORMAT(V.Ora_partenza, '%H:%i') AS Ora_partenza,
        DATE_FORMAT(V.Data_arrivo, '%d/%m/%Y') AS Data_arrivo,
        TIME_FORMAT(V.Ora_arrivo, '%H:%i') AS Ora_arrivo,
        TIME_FORMAT(
            TIMEDIFF(TIMESTAMP(V.Data_arrivo, V.Ora_arrivo), TIMESTAMP(V.Data_partenza, V.Ora_partenza)),
            '%Hh %im') AS Durata_volo,
        DATE_FORMAT(P.Data_prenotazione, '%d-%m-%Y %H:%i') AS Data_prenotazione,
        CONCAT(FORMAT(B.Prezzo, 2), ' €') AS Prezzo,
        B.Stato_biglietto,
        Pt.Numero_posto AS Posto,
        COALESCE(
            GROUP_CONCAT(
                CONCAT(A3.Citta, ' (', A3.Codice_IATA, ') - Arrivo: ', S.Ora_arrivo,
                ', Partenza: ', S.Ora_partenza, ', Durata scalo: ',
                TIME_FORMAT(TIMEDIFF(TIMESTAMP(S.Ora_partenza), TIMESTAMP(S.Ora_arrivo)), '%Hh %im'))
            SEPARATOR ' | '),
        'Nessuno') AS Scali
    FROM Biglietto B
    JOIN Prenotazione P ON B.ID_prenotazione = P.ID_prenotazione
    JOIN Cliente C ON P.ID_cliente = C.ID_cliente
    JOIN Posto Pt ON P.ID_posto = Pt.ID_posto
    JOIN Volo V ON P.ID_volo = V.ID_volo
    JOIN Aeroporto A1 ON V.ID_aeroporto_partenza = A1.ID_aeroporto
    JOIN Aeroporto A2 ON V.ID_aeroporto_arrivo = A2.ID_aeroporto
    LEFT JOIN Scalo S ON V.ID_volo = S.ID_volo
    LEFT JOIN Aeroporto A3 ON S.ID_aeroporto = A3.ID_aeroporto
    WHERE C.Email = :email
    GROUP BY B.ID_biglietto
    ORDER BY P.Data_prenotazione DESC;
    """)
    result = db.execute(query, {"email": email})
    biglietti = result.mappings().all()

    if not biglietti:
        return {"messaggio": f"Nessun biglietto trovato."}

    return biglietti

# 3. Ricerca voli tra 2 aeroporti
def get_voli_da_a_a(db: Session, citta_partenza: str, citta_arrivo: str):
    query = text("""
        SELECT
            V.Codice_volo,
            CONCAT(A1.Citta, ' (', A1.Codice_IATA, ')') AS Partenza,
            CONCAT(A2.Citta, ' (', A2.Codice_IATA, ')') AS Destinazione,
            DATE_FORMAT(V.Data_partenza, '%d/%m/%Y') AS Data_partenza, 
            TIME_FORMAT(V.Ora_partenza, '%H:%i') AS Ora_partenza,
            DATE_FORMAT(V.Data_arrivo, '%d/%m/%Y') AS Data_arrivo,
            TIME_FORMAT(V.Ora_arrivo, '%H:%i') AS Ora_arrivo,
            TIME_FORMAT(
                TIMEDIFF(TIMESTAMP(V.Data_arrivo, V.Ora_arrivo), TIMESTAMP(V.Data_partenza, V.Ora_partenza)), 
                '%Hh %im') AS Durata_volo,
            CONCAT(FORMAT(V.Prezzo, 2), ' €') AS Prezzo,
            COALESCE(
                GROUP_CONCAT(
                    CONCAT(A3.Citta, ' (', A3.Codice_IATA, ') - Arrivo: ', S.Ora_arrivo,
                    ', Partenza: ', S.Ora_partenza, ', Durata scalo: ',
                    TIME_FORMAT(TIMEDIFF(TIMESTAMP(S.Ora_partenza), TIMESTAMP(S.Ora_arrivo)), '%Hh %im'))
                SEPARATOR ' | '), 
            'Nessuno') AS Scali
        FROM Volo V
        JOIN Aeroporto A1 ON V.ID_aeroporto_partenza = A1.ID_aeroporto
        JOIN Aeroporto A2 ON V.ID_aeroporto_arrivo = A2.ID_aeroporto
        LEFT JOIN Scalo S ON V.ID_volo = S.ID_volo
        LEFT JOIN Aeroporto A3 ON S.ID_aeroporto = A3.ID_aeroporto
        WHERE A1.Citta = :partenza 
          AND A2.Citta = :arrivo
          AND EXISTS (
            SELECT 1 
            FROM Posto P
            LEFT JOIN Prenotazione PR ON PR.ID_posto = P.ID_posto AND PR.ID_volo = V.ID_volo
            LEFT JOIN Biglietto B ON B.ID_prenotazione = PR.ID_prenotazione
            WHERE P.ID_volo = V.ID_volo
              AND (
                  PR.ID_prenotazione IS NULL
                  OR PR.Stato = 'Annullata'  
              )
          )
        GROUP BY V.ID_volo
        ORDER BY V.Data_partenza;
    """)

    result = db.execute(query, {"partenza": citta_partenza, "arrivo": citta_arrivo})
    return result.mappings().all()

# 4. Ricerca posti disponibili per un volo specifico
def get_posti_disponibili(db: Session, codice_volo: str):
    query = text("""
        SELECT P.Numero_posto
        FROM Posto P
        JOIN Volo V ON P.ID_volo = V.ID_volo
        LEFT JOIN Prenotazione PR ON PR.ID_posto = P.ID_posto AND PR.ID_volo = V.ID_volo
        WHERE V.Codice_volo = :codice_volo
          AND (
              PR.ID_prenotazione IS NULL
              OR PR.Stato = 'Annullata'
          )
        ORDER BY P.Numero_posto;
    """)
    result = db.execute(query, {"codice_volo": codice_volo})
    return result.mappings().all()

# 5. Riepilogo dettagli prenotazione
def get_dettagli_prenotazione(db: Session, codice_prenotazione: str):
    query = text("""
        SELECT 
            P.Codice_prenotazione,
            CONCAT(C.Nome, ' ', C.Cognome) AS Cliente,
            CONCAT(A1.Citta, ' (', A1.Codice_IATA, ')') AS Partenza,
            CONCAT(A2.Citta, ' (', A2.Codice_IATA, ')') AS Destinazione,
            DATE_FORMAT(V.Data_partenza, '%d/%m/%Y') AS Data_partenza,
            TIME_FORMAT(V.Ora_partenza, '%H:%i') AS Ora_partenza,
            DATE_FORMAT(V.Data_arrivo, '%d/%m/%Y') AS Data_arrivo,
            TIME_FORMAT(V.Ora_arrivo, '%H:%i') AS Ora_arrivo,
            TIME_FORMAT(
                TIMEDIFF(TIMESTAMP(V.Data_arrivo, V.Ora_arrivo), TIMESTAMP(V.Data_partenza, V.Ora_partenza)), 
                '%Hh %im'
            ) AS Durata_volo,
            CONCAT(FORMAT(P.Prezzo, 2), ' €') AS Prezzo, 
            P.Stato,
            Pt.Numero_posto AS Posto,
            COALESCE(
                GROUP_CONCAT(
                    CONCAT(A3.Citta, ' (', A3.Codice_IATA, ') - Arrivo: ', S.Ora_arrivo,
                    ', Partenza: ', S.Ora_partenza, ', Durata scalo: ',
                    TIME_FORMAT(TIMEDIFF(TIMESTAMP(S.Ora_arrivo), TIMESTAMP(S.Ora_partenza)), '%Hh %im'))
                SEPARATOR ' | '), 
            'Nessuno') AS Scali
        FROM Prenotazione P
        JOIN Cliente C ON P.ID_cliente = C.ID_cliente
        JOIN Volo V ON P.ID_volo = V.ID_volo
        JOIN Aeroporto A1 ON V.ID_aeroporto_partenza = A1.ID_aeroporto
        JOIN Aeroporto A2 ON V.ID_aeroporto_arrivo = A2.ID_aeroporto
        JOIN Posto Pt ON P.ID_posto = Pt.ID_posto
        LEFT JOIN Scalo S ON V.ID_volo = S.ID_volo
        LEFT JOIN Aeroporto A3 ON S.ID_aeroporto = A3.ID_aeroporto
        WHERE P.Codice_prenotazione = :codice
        GROUP BY P.ID_prenotazione;
    """)

    result = db.execute(query, {"codice": codice_prenotazione})
    return result.mappings().all()
