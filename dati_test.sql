USE trasporto_aereo;

INSERT INTO Aeroporto (Nome, Citta, Codice_IATA) VALUES
('Aeroporto di Roma Fiumicino', 'Roma', 'FCO'),
('Aeroporto di Milano Malpensa', 'Milano', 'MXP'),
('Aeroporto di Madrid Barajas', 'Madrid', 'MAD'),
('Aeroporto di Parigi Charles de Gaulle', 'Parigi', 'CDG');

INSERT INTO Volo (Codice_volo, ID_aeroporto_partenza, ID_aeroporto_arrivo, Data_partenza, Ora_partenza, Data_arrivo, Ora_arrivo, Prezzo, Stato_volo) VALUES
('FCO123', 1, 2, '2025-06-01', '08:00:00', '2025-06-01', '10:00:00', 100.00, 'Programmato'),
('MXP456', 2, 3, '2025-06-02', '14:00:00', '2025-06-02', '16:30:00', 120.00, 'Programmato'),
('MAD789', 3, 4, '2025-06-03', '09:30:00', '2025-06-03', '12:00:00', 120.00, 'Programmato');

INSERT INTO Scalo (ID_volo, ID_aeroporto, Ora_arrivo, Ora_partenza) VALUES
(2, 1, '15:00:00', '15:45:00');

INSERT INTO Cliente (Nome, Cognome, Email, Telefono) VALUES
('Mario', 'Rossi', 'mario.rossi@email.com', '1234567890'),
('Luca', 'Bianchi', 'luca.bianchi@email.com', '0987654321'),
('Giulia', 'Verdi', 'giulia.verdi@email.com', '3456789123'); 

INSERT INTO Posto (ID_volo, Numero_posto) VALUES
(1, '1A'), (1, '1B'), (2, '2A'), (2, '2B'), (3, '3A'), (3, '3B');


