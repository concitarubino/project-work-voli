from pydantic import BaseModel
from datetime import date, time, datetime
from typing import Optional
from modelli import StatoVoloEnum, StatoPrenotazioneEnum, TipoBagaglioEnum, MetodoPagamentoEnum, StatoPagamentoEnum, StatoBigliettoEnum


# Schemi Pydantic

class AeroportoSchema(BaseModel):
    ID_aeroporto: Optional[int] = None
    Nome: str
    Citta: str
    Codice_IATA: str

    class Config:
        from_attributes = True

class VoloSchema(BaseModel):
    ID_volo: Optional[int] = None
    Codice_volo: str
    ID_aeroporto_partenza: int
    ID_aeroporto_arrivo: int
    Data_partenza: date
    Ora_partenza: time
    Data_arrivo: date
    Ora_arrivo: time
    Prezzo: float
    Stato_volo: StatoVoloEnum = StatoVoloEnum.Programmato

    class Config:
        from_attributes = True

class ScaloSchema(BaseModel):
    ID_scalo: Optional[int] = None
    ID_volo: int
    ID_aeroporto: int
    Ora_arrivo: time
    Ora_partenza: time

    class Config:
        from_attributes = True

class PostoSchema(BaseModel):
    ID_posto: Optional[int] = None
    ID_volo: int
    Numero_posto: str

    class Config:
        from_attributes = True

class PrenotazioneSchema(BaseModel):
    ID_prenotazione: Optional[int] = None
    Codice_prenotazione: Optional[str] = None
    Nome: str
    Cognome: str
    Email: str
    Telefono: str
    ID_volo: int
    ID_posto: int
    Data_prenotazione: Optional[datetime] = None
    Prezzo: Optional[float] = None
    Stato: StatoPrenotazioneEnum = StatoPrenotazioneEnum.Prenotata

    class Config:
        from_attributes = True

class BagaglioSchema(BaseModel):
    ID_bagaglio: Optional[int] = None
    ID_prenotazione: int
    Tipo: TipoBagaglioEnum = TipoBagaglioEnum.Standard
    Prezzo: Optional[float] = None

    class Config:
        from_attributes = True

class PagamentoSchema(BaseModel):
    ID_pagamento: Optional[int] = None
    ID_prenotazione: int
    Metodo: MetodoPagamentoEnum
    Importo: Optional[float] = None
    Stato: StatoPagamentoEnum
    Data_pagamento: Optional[datetime] = None

    class Config:
        from_attributes = True

class BigliettoSchema(BaseModel):
    ID_biglietto: Optional[int] = None
    ID_prenotazione: int
    Prezzo: float
    Stato_biglietto: StatoBigliettoEnum = StatoBigliettoEnum.Prenotato

    class Config:
        from_attributes = True
