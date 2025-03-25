from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
import uvicorn
from typing import List
from configurazione import SessionLocal
from modelli import Aeroporto, Volo, Scalo, Posto, Prenotazione, Bagaglio, Pagamento, Biglietto
from schemi import AeroportoSchema, VoloSchema, ScaloSchema, PostoSchema, PrenotazioneSchema, BagaglioSchema, PagamentoSchema, BigliettoSchema
from crud import calcola_prezzo_prenotazione, gestisci_pagamento, calcola_prezzo_bagaglio, genera_codice_prenotazione, get_biglietti_cliente, get_dettagli_prenotazione, get_posti_disponibili, get_voli_da_a_a, get_voli_disponibili

app = FastAPI(title="API per Gestione Trasporto Aereo")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/aeroporti", response_model=List[AeroportoSchema])
def read_aeroporti(db: Session = Depends(get_db)):
    return db.query(Aeroporto).all()

@app.post("/aeroporti", response_model=AeroportoSchema)
def create_aeroporto(aeroporto: AeroportoSchema, db: Session = Depends(get_db)):
    db_aeroporto = Aeroporto(**aeroporto.model_dump(exclude_unset=True))
    db.add(db_aeroporto)
    db.commit()
    db.refresh(db_aeroporto)
    return db_aeroporto

@app.get("/voli", response_model=List[VoloSchema])
def read_voli(db: Session = Depends(get_db)):
    return db.query(Volo).all()

@app.post("/voli", response_model=VoloSchema)
def create_volo(volo: VoloSchema, db: Session = Depends(get_db)):
    db_volo = Volo(**volo.model_dump(exclude_unset=True))
    db.add(db_volo)
    db.commit()
    db.refresh(db_volo)
    return db_volo

@app.get("/scali", response_model=List[ScaloSchema])
def read_scali(db: Session = Depends(get_db)):
    return db.query(Scalo).all()

@app.post("/scali", response_model=ScaloSchema)
def create_scalo(scalo: ScaloSchema, db: Session = Depends(get_db)):
    db_scalo = Scalo(**scalo.model_dump(exclude_unset=True))
    db.add(db_scalo)
    db.commit()
    db.refresh(db_scalo)
    return db_scalo

@app.get("/posti", response_model=List[PostoSchema])
def read_posti(db: Session = Depends(get_db)):
    return db.query(Posto).all()

@app.post("/posti", response_model=PostoSchema)
def create_posto(posto: PostoSchema, db: Session = Depends(get_db)):
    db_posto = Posto(**posto.model_dump(exclude_unset=True))
    db.add(db_posto)
    db.commit()
    db.refresh(db_posto)
    return db_posto

@app.get("/prenotazioni", response_model=List[PrenotazioneSchema])
def read_prenotazioni(db: Session = Depends(get_db)):
    return db.query(Prenotazione).all()

@app.post("/prenotazioni", response_model=PrenotazioneSchema)
def create_prenotazione(prenotazione: PrenotazioneSchema, db: Session = Depends(get_db)):
    prenotazione_dict = prenotazione.model_dump(exclude_unset=True)

    if "Codice_prenotazione" not in prenotazione_dict:
        prenotazione_dict["Codice_prenotazione"] = genera_codice_prenotazione(db)
    
    volo = db.query(Volo).filter(Volo.ID_volo == prenotazione_dict["ID_volo"]).first()
    if not volo:
        raise HTTPException(status_code=404, detail="Volo non trovato")
    
    prenotazione_dict["Prezzo"] = float(volo.Prezzo)

    db_prenotazione = Prenotazione(**prenotazione_dict)
    db.add(db_prenotazione)
    db.commit()
    db.refresh(db_prenotazione)

    prezzo_totale = calcola_prezzo_prenotazione(db, db_prenotazione.ID_prenotazione)
    db_prenotazione.Prezzo = prezzo_totale
    db.commit()
    db.refresh(db_prenotazione)

    return db_prenotazione

@app.get("/bagagli", response_model=List[BagaglioSchema])
def read_bagagli(db: Session = Depends(get_db)):
    return db.query(Bagaglio).all()

@app.post("/bagagli", response_model=BagaglioSchema)
def create_bagaglio(bagaglio: BagaglioSchema, db: Session = Depends(get_db)):
    bagaglio_data = bagaglio.model_dump(exclude_unset=True)
    bagaglio_data["Prezzo"] = calcola_prezzo_bagaglio(bagaglio_data["Tipo"])
    db_bagaglio = Bagaglio(**bagaglio_data)
    db.add(db_bagaglio)
    db.commit()
    db.refresh(db_bagaglio)

    prenotazione = db.query(Prenotazione).filter(Prenotazione.ID_prenotazione == db_bagaglio.ID_prenotazione).first()
    if not prenotazione:
        raise HTTPException(status_code=404, detail="Prenotazione non trovata")

    try:
        prenotazione.Prezzo = calcola_prezzo_prenotazione(db, prenotazione.ID_prenotazione)
        db.commit()
        db.refresh(prenotazione)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore aggiornamento prezzo: {str(e)}")

    return db_bagaglio

@app.get("/pagamenti", response_model=List[PagamentoSchema])
def read_pagamenti(db: Session = Depends(get_db)):
    return db.query(Pagamento).all()

@app.post("/pagamenti", response_model=PagamentoSchema)
def create_pagamento_endpoint(pagamento: PagamentoSchema, db: Session = Depends(get_db)):
    return gestisci_pagamento(db, pagamento)

@app.get("/biglietti", response_model=List[BigliettoSchema])
def read_biglietti(db: Session = Depends(get_db)):
    return db.query(Biglietto).all()


# QUERY

@app.get("/flights/available")
def search_available_flights(citta: str, data: str, db: Session = Depends(get_db)):
    return get_voli_disponibili(db, citta, data)

@app.get("/clienti/{email}/biglietti")
def search_ticket_cliente(email: str, db: Session = Depends(get_db)):
    return get_biglietti_cliente(db, email)

@app.get("/voli/ricerca")
def search_voli_da_a(partenza: str, arrivo: str, db: Session = Depends(get_db)):
    return get_voli_da_a_a(db, partenza, arrivo)

@app.get("/posti/disponibili")
def search_posti_disponibili(codice_volo: str, db: Session = Depends(get_db)):
    return get_posti_disponibili(db, codice_volo)

@app.get("/clienti/prenotazioni")
def search_prenotazione_cliente(codice_prenotazione: str, db: Session = Depends(get_db)):
    return get_dettagli_prenotazione(db, codice_prenotazione)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
