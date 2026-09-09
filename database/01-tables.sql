-- 1. Créer le type etat_materiel
DO $$
BEGIN
    CREATE TYPE etat_materiel AS ENUM (
        'OK',
        'Réservé',
        'En réparation',
        'Endommagé',
        'Disparu'
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END
$$;

-- 2. Créer les entités
CREATE TABLE IF NOT EXISTS entites (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL UNIQUE
);

INSERT INTO entites (nom)
VALUES ('ULCO')
ON CONFLICT (nom) DO NOTHING;

-- 3. Créer les matériels
CREATE TABLE IF NOT EXISTS materiels (
    id_materiel SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    modele VARCHAR(255),
    annee INT,
    etiquette_ulco VARCHAR(255) UNIQUE,
    etat etat_materiel NOT NULL DEFAULT 'OK',
    localisation VARCHAR(255) NOT NULL,
    descriptif TEXT,
    remarque TEXT,
    entite_id INT NOT NULL REFERENCES entites(id) ON DELETE CASCADE,
    image_data BYTEA,
    image_type VARCHAR(50)
);