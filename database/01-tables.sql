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

-- 4. Créer les photos associées aux matériels
-- est_avant : TRUE = photo de référence (prise à l'enregistrement du matériel)
--             FALSE = photo d'analyse (prise après le prêt pour comparaison)
CREATE TABLE IF NOT EXISTS photos_materiels (
    id_photo SERIAL PRIMARY KEY,
    id_materiel INT NOT NULL REFERENCES materiels(id_materiel) ON DELETE CASCADE,
    type_photo VARCHAR(50) NOT NULL,
    est_avant BOOLEAN NOT NULL DEFAULT TRUE,
    image_data BYTEA NOT NULL,
    image_type VARCHAR(50) NOT NULL,
    UNIQUE (id_materiel, type_photo, est_avant)
);

-- 5. Conserver l'historique des rapports produits par l'IA
CREATE TABLE IF NOT EXISTS rapports_ia (
    id_rapport SERIAL PRIMARY KEY,
    id_materiel INT NOT NULL REFERENCES materiels(id_materiel) ON DELETE CASCADE,
    contenu TEXT NOT NULL,
    cree_le TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Migration des bases créées avec l'ancienne contrainte (un seul rapport)
ALTER TABLE rapports_ia DROP CONSTRAINT IF EXISTS rapports_ia_id_materiel_key;
