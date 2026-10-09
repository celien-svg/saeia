CREATE TABLE IF NOT EXISTS validations_humaines (
    id_validation SERIAL PRIMARY KEY,
    id_rapport INT NOT NULL REFERENCES rapports_ia(id_rapport) ON DELETE CASCADE,
    decision VARCHAR(50) NOT NULL CHECK (
        decision IN ('accepter_degradation', 'modifier_type_gravite', 'ignorer_faux_positif')
    ),
    type_anomalie VARCHAR(255),
    gravite VARCHAR(20) CHECK (gravite IN ('aucune', 'legere', 'marquee', 'importante')),
    remarque TEXT,
    cree_le TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
