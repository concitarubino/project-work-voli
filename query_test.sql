--  QUERY ESEMPIO

-- 1. Voli disponibili da un aeroporto in una data, se posti non disponibili, non mostra volo
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

-- 2. Biglietti acquistati
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

-- 3. Ricerca voli tra 2 aeroporti (se posti non disponibili non mostra volo)
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

-- 4. Ricerca posti disponibili per un volo specifico
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

-- 5. Riepilogo dettagli prenotazione
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