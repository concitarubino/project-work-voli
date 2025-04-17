from sqlalchemy import Column, Integer, String, Date, Time, Numeric, Enum, ForeignKey, DateTime, UniqueConstraint, func
from configurazione import Base
import enum

# ENUM SQLAlchemy

class StatoVoloEnum(str, enum.Enum):
    Programmato = "Programmato"
    Cancellato = "Cancellato"

class StatoPrenotazioneEnum(str, enum.Enum):
    Prenotata = "Prenotata"
    Pagata = "Pagata"
    Annullata = "Annullata"

class TipoBagaglioEnum(str, enum.Enum):
    Standard = "Standard"
    Cabina = "Cabina"
    Stiva = "Stiva"

class MetodoPagamentoEnum(str, enum.Enum):
    CreditCard = "CreditCard"
    PayPal = "PayPal"
    GooglePay = "GooglePay"
    ApplePay = "ApplePay"

class StatoPagamentoEnum(str, enum.Enum):
    Completato = "Completato"
    Rifiutato = "Rifiutato"

class StatoBigliettoEnum(str, enum.Enum):
    Prenotato = "Prenotato"
    Cancellato = "Cancellato"
    Utilizzato = "Utilizzato"


# Modelli SQLAlchemy

class Aeroporto(Base):
    __tablename__ = "Aeroporto"
    ID_aeroporto = Column(Integer, primary_key=True, autoincrement=True)
    Nome = Column(String(100), nullable=False)
    Citta = Column(String(50), nullable=False)
    Codice_IATA = Column(String(3), nullable=False, unique=True)

class Volo(Base):
    __tablename__ = "Volo"
    ID_volo = Column(Integer, primary_key=True, autoincrement=True)
    Codice_volo = Column(String(10), nullable=False, unique=True)
    ID_aeroporto_partenza = Column(Integer, ForeignKey("Aeroporto.ID_aeroporto"), nullable=False)
    ID_aeroporto_arrivo = Column(Integer, ForeignKey("Aeroporto.ID_aeroporto"), nullable=False)
    Data_partenza = Column(Date, nullable=False)
    Ora_partenza = Column(Time, nullable=False)
    Data_arrivo = Column(Date, nullable=False)
    Ora_arrivo = Column(Time, nullable=False)
    Prezzo = Column(Numeric(10,2), nullable=False)
    Stato_volo = Column(Enum(StatoVoloEnum), default=StatoVoloEnum.Programmato)

class Scalo(Base):
    __tablename__ = "Scalo"
    ID_scalo = Column(Integer, primary_key=True, autoincrement=True)
    ID_volo = Column(Integer, ForeignKey("Volo.ID_volo", ondelete="CASCADE"), nullable=False)
    ID_aeroporto = Column(Integer, ForeignKey("Aeroporto.ID_aeroporto", ondelete="CASCADE"), nullable=False)
    Ora_arrivo = Column(Time, nullable=False)
    Ora_partenza = Column(Time, nullable=False)

class Cliente(Base):
    __tablename__ = "Cliente"
    ID_cliente = Column(Integer, primary_key=True, autoincrement=True)
    Nome = Column(String(50), nullable=False)
    Cognome = Column(String(50), nullable=False)
    Email = Column(String(100), nullable=False, unique=True)
    Telefono = Column(String(20), nullable=False)

class Posto(Base):
    __tablename__ = "Posto"
    ID_posto = Column(Integer, primary_key=True, autoincrement=True)
    ID_volo = Column(Integer, ForeignKey("Volo.ID_volo"), nullable=False)
    Numero_posto = Column(String(4), nullable=False)

    __table_args__ = (
    UniqueConstraint("ID_volo", "Numero_posto", name="uq_posto_volo"),
    )

class Prenotazione(Base):
    __tablename__ = "Prenotazione"
    ID_prenotazione = Column(Integer, primary_key=True, autoincrement=True)
    Codice_prenotazione = Column(String(10), unique=True)
    ID_cliente = Column(Integer, ForeignKey("Cliente.ID_cliente"), nullable=False)
    ID_volo = Column(Integer, ForeignKey("Volo.ID_volo"), nullable=False)
    ID_posto = Column(Integer, ForeignKey("Posto.ID_posto"), nullable=False)
    Data_prenotazione = Column(DateTime, server_default=func.current_timestamp())
    Prezzo = Column(Numeric(10,2))
    Stato = Column(Enum(StatoPrenotazioneEnum), default=StatoPrenotazioneEnum.Prenotata)

class Bagaglio(Base):
    __tablename__ = "Bagaglio"
    ID_bagaglio = Column(Integer, primary_key=True, autoincrement=True)
    ID_prenotazione = Column(Integer, ForeignKey("Prenotazione.ID_prenotazione", ondelete="CASCADE"), nullable=False)
    Tipo = Column(Enum(TipoBagaglioEnum), nullable=False, default=TipoBagaglioEnum.Standard)
    Prezzo = Column(Numeric(10, 2), default=0.00)

class Pagamento(Base):
    __tablename__ = "Pagamento"
    ID_pagamento = Column(Integer, primary_key=True, autoincrement=True)
    ID_prenotazione = Column(Integer, ForeignKey("Prenotazione.ID_prenotazione"), nullable=False)
    Metodo = Column(Enum(MetodoPagamentoEnum), nullable=False)
    Importo = Column(Numeric(10,2))
    Stato = Column(Enum(StatoPagamentoEnum), nullable=False)
    Data_pagamento = Column(DateTime, server_default=func.current_timestamp())

class Biglietto(Base):
    __tablename__ = "Biglietto"
    ID_biglietto = Column(Integer, primary_key=True, autoincrement=True)
    ID_prenotazione = Column(Integer, ForeignKey("Prenotazione.ID_prenotazione"), nullable=False)
    Prezzo = Column(Numeric(10,2), nullable=False)
    Stato_biglietto = Column(Enum(StatoBigliettoEnum), default=StatoBigliettoEnum.Prenotato)
