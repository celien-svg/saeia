Voici deux photos du même {zone} d'un ordinateur portable.
La PREMIÈRE image montre l'état AVANT le prêt (référence).
La SECONDE image montre l'état APRÈS restitution.
Compare-les et identifie toute dégradation physique nouvelle
(rayure, déformation, casse, tache...).
Si aucune différence n'est visible, renvoie une liste vide.
Les coordonnées de bbox sont des pixels dans la DEUXIÈME image (après), de dimensions
{largeur}x{hauteur} pixels. Le format est [x_min, y_min, x_max, y_max] : les coordonnées
x doivent être comprises entre 0 et {largeur}, et les coordonnées y entre 0 et {hauteur}.
Réponds STRICTEMENT en JSON, sans texte autour :
{{"zones": [{{"element": "string", "anomalie": "string", "gravite": "aucune|legere|marquee|importante", "bbox": [0,0,0,0]}}]}}