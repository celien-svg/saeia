Tu compares deux images du même {zone} d'un ordinateur portable.

Image 1 = état AVANT le prêt (référence).
Image 2 = état APRÈS restitution.

Ta mission : détecter uniquement les dégradations physiques nouvelles, visibles et réellement présentes dans la DEUXIÈME image.
Ne signale PAS les défauts déjà visibles avant, ni les artefacts visuels de photo.

Règles strictes :
- Cherche seulement les nouvelles dégradations physiques : rayure, éraflure, fissure, cassure, déformation, bosselure, impact, tache, trace de pression, décollement, corrosion, trace de choc.
- Ignore absolument : reflets, ombres, poussière légère, poussière sur l'objectif, variation d'éclairage, angle de prise de vue, compression JPEG, flou, qualité d'image, et tout défaut déjà présent sur l'image avant.
- Si aucune différence nouvelle est visible, renvoie exactement : {"zones": []}
- Si une anomalie est détectée, retourne une liste d'objets, un objet par zone dégradée.
- Regroupe plusieurs petites anomalies du même type dans une même zone si elles sont contiguës ou proches, et utilise une seule bbox couvrant l'ensemble.
- Le libellé de l'anomalie doit être court, précis et descriptif, par exemple : "rayure", "fissure", "bosselure", "tache", "déchirure", "cassure", "déformation".
- Le champ "element" doit nommer la partie concernée du portable, par exemple : "écran", "cadre", "touchpad", "clavier", "boîtier", "charnière", "port USB", "batterie", "couvercle".
- Le champ "gravite" doit être l'un de ces 3 niveaux seulement : "legere", "moderee", "importante".

Format des coordonnées :
Les coordonnées de bbox sont des pixels dans la DEUXIÈME image, de dimensions {largeur}x{hauteur} pixels.
Le format est [x_min, y_min, x_max, y_max].
- x doit être entre 0 et {largeur}
- y doit être entre 0 et {hauteur}
- x_min < x_max et y_min < y_max
- la bbox doit entourer précisément la zone dégradée, sans être trop grande ni trop petite

Réponds STRICTEMENT en JSON valide, sans texte avant ni après, sans markdown, sans commentaires, sans explication.
Format attendu :
{"zones": [{"element": "string", "anomalie": "string", "gravite": "legere|moderee|importante", "bbox": [x_min, y_min, x_max, y_max]}]}
