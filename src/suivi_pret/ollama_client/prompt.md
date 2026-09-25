Voici deux photos du même {zone} d'un ordinateur portable.
La PREMIÈRE image montre l'état AVANT le prêt (référence).
La SECONDE image montre l'état APRÈS restitution.
Compare-les et identifie toute dégradation physique nouvelle
(rayure, déformation, casse, tache...).
Si aucune différence n'est visible, renvoie une liste vide.
Les coordonnées de bbox sont des pixels dans l'image 1024x1024, au format
[x_min, y_min, x_max, y_max]. Chaque coordonnée doit être comprise entre 0 et 1024.
Réponds STRICTEMENT en JSON, sans texte autour :
{{"zones": [{{"element": "string", "anomalie": "string", "gravite": "aucune|legere|marquee|importante", "bbox": [0,0,0,0]}}]}}