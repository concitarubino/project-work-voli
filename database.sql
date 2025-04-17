-- CREAZIONE DATABASE
CREATE DATABASE trasporto_aereo;
USE trasporto_aereo;

-- CREAZIONE TABELLE Aeroporto, Volo, Scalo, Posto, Prenotazione, Bagaglio, Pagamento, Biglietto

CREATE TABLE Aeroporto (
    ID_aeroporto INT AUTO_INCREMENT PRIMARY KEY,
    Nome VARCHAR(100) NOT NULL,
    Citta VARCHAR(50) NOT NULL,
    Codice_IATA CHAR(3) UNIQUE NOT NULL
);

CREATE TABLE Volo (
    ID_volo INT AUTO_INCREMENT PRIMARY KEY,
    Codice_volo VARCHAR(10) UNIQUE NOT NULL,
    ID_aeroporto_partenza INT NOT NULL,
    ID_aeroporto_arrivo INT NOT NULL,
    Data_partenza DATE NOT NULL,
    Ora_partenza TIME NOT NULL,
    Data_arrivo DATE NOT NULL,
    Ora_arrivo TIME NOT NULL,
    Prezzo DECIMAL(10,2) NOT NULL,  -- Prezzo base del volo
    Stato_volo ENUM('Programmato', 'Cancellato') DEFAULT 'Programmato',
    FOREIGN KEY (ID_aeroporto_partenza) REFERENCES Aeroporto(ID_aeroporto),
    FOREIGN KEY (ID_aeroporto_arrivo) REFERENCES Aeroporto(ID_aeroporto)
);

CREATE TABLE Scalo (
    ID_scalo INT AUTO_INCREMENT PRIMARY KEY,
    ID_volo INT NOT NULL,
    ID_aeroporto INT NOT NULL,
    Ora_arrivo TIME NOT NULL,
    Ora_partenza TIME NOT NULL,
    FOREIGN KEY (ID_volo) REFERENCES Volo(ID_volo) ON DELETE CASCADE,
    FOREIGN KEY (ID_aeroporto) REFERENCES Aeroporto(ID_aeroporto) ON DELETE CASCADE
);

CREATE TABLE Cliente (
    ID_cliente INT AUTO_INCREMENT PRIMARY KEY,
    Nome VARCHAR(50) NOT NULL,
    Cognome VARCHAR(50) NOT NULL,
    Email VARCHAR(100) NOT NULL UNIQUE,
    Telefono VARCHAR(20) NOT NULL
);

CREATE TABLE Posto (
    ID_posto INT AUTO_INCREMENT PRIMARY KEY,
    ID_volo INT NOT NULL,
    Numero_posto VARCHAR(4) NOT NULL,
    FOREIGN KEY (ID_volo) REFERENCES Volo(ID_volo),
    UNIQUE(ID_volo, Numero_posto)
);

CREATE TABLE Prenotazione (
    ID_prenotazione INT AUTO_INCREMENT PRIMARY KEY,
    Codice_prenotazione VARCHAR(10) UNIQUE, -- backend
    ID_cliente INT NOT NULL,
    ID_volo INT NOT NULL,
    ID_posto INT NOT NULL,
    Data_prenotazione DATETIME DEFAULT CURRENT_TIMESTAMP,
    Prezzo DECIMAL(10,2), -- Prezzo del volo + bagagli 
    Stato ENUM('Prenotata', 'Pagata', 'Annullata') DEFAULT 'Prenotata', -- backend
    FOREIGN KEY (ID_volo) REFERENCES Volo(ID_volo),
    FOREIGN KEY (ID_posto) REFERENCES Posto(ID_posto),
    FOREIGN KEY (ID_cliente) REFERENCES Cliente(ID_cliente)
);

CREATE TABLE Bagaglio (
    ID_bagaglio INT AUTO_INCREMENT PRIMARY KEY,
    ID_prenotazione INT NOT NULL,
    Tipo ENUM('Standard', 'Cabina', 'Stiva') NOT NULL DEFAULT 'Standard',
    Prezzo DECIMAL(10,2) DEFAULT 0.00, -- backend
    FOREIGN KEY (ID_prenotazione) REFERENCES Prenotazione(ID_prenotazione) ON DELETE CASCADE
);

CREATE TABLE Pagamento (
    ID_pagamento INT AUTO_INCREMENT PRIMARY KEY,
    ID_prenotazione INT NOT NULL,
    Metodo ENUM('CreditCard', 'PayPal', 'GooglePay', 'ApplePay') NOT NULL,
    Importo DECIMAL(10,2), -- backend
    Stato ENUM('Completato', 'Rifiutato') NOT NULL,
    Data_pagamento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ID_prenotazione) REFERENCES Prenotazione(ID_prenotazione)
);

-- tabella popolata da backend
CREATE TABLE Biglietto (
    ID_biglietto INT AUTO_INCREMENT PRIMARY KEY,
    ID_prenotazione INT NOT NULL,
    Prezzo DECIMAL(10,2) NOT NULL, -- Prezzo del volo + bagagli
    Stato_biglietto ENUM('Prenotato', 'Cancellato', 'Utilizzato') DEFAULT 'Prenotato',
    FOREIGN KEY (ID_prenotazione) REFERENCES Prenotazione(ID_prenotazione)
);

-- INDICI UTILI

CREATE INDEX idx_aeroporto_codice ON Aeroporto(Codice_IATA);

CREATE INDEX idx_volo_partenza ON Volo (ID_aeroporto_partenza, Data_partenza, Ora_partenza);
CREATE INDEX idx_volo_arrivo ON Volo(ID_aeroporto_arrivo, Data_arrivo);
CREATE INDEX idx_volo_codice ON Volo(Codice_volo);

CREATE INDEX idx_biglietto_prenotazione ON Biglietto(ID_prenotazione);

CREATE INDEX idx_bagaglio_prenotazione ON Bagaglio(ID_prenotazione);

CREATE INDEX idx_pagamento_prenotazione ON Pagamento(ID_prenotazione);

CREATE INDEX idx_prenotazione_volo ON Prenotazione(ID_volo);
CREATE INDEX idx_prenotazione_posto ON Prenotazione(ID_posto);
CREATE INDEX idx_prenotazione_codice ON Prenotazione(Codice_prenotazione);

CREATE INDEX idx_scalo_volo ON Scalo(ID_volo);
