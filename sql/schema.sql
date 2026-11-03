CREATE TABLE IF NOT EXISTS ereignisse (
    ereignis_id TEXT PRIMARY KEY,
    zeitpunkt TEXT NOT NULL,
    umgebung TEXT NOT NULL,
    stufe TEXT NOT NULL,
    nachricht TEXT NOT NULL,
    ist_zeitueberschreitung INTEGER NOT NULL CHECK (ist_zeitueberschreitung IN (0, 1))
);
