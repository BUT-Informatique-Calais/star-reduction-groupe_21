# SAÉ S3.C2 : Réduction d'étoiles en astrophotographie

## Auteurs

- OUTMANI Zinab
- KIME Marwa

## Description

Outil de réduction d'étoiles pour le traitement d'images astronomiques FITS. L'objectif est de réduire le diamètre apparent des étoiles brillantes sans altérer les détails des nébuleuses.

## Installation

### Environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

### Dépendances

```bash
pip install -r requirements.txt
```

## Structure du projet

```
astro_project/
├── erosion.py              # Script principal
├── examples/               # Fichiers FITS de test
│   ├── HorseHead.fits
│   ├── test_M31_linear.fits
│   └── test_M31_raw.fits
├── results/                # Images de sortie
│   ├── original.png
│   └── eroded.png
├── requirements.txt
└── README.md
```

## Utilisation

### Phase 1 : Érosion simple

```bash
python erosion.py
```

Le script charge `HorseHead.fits`, applique une érosion et sauvegarde les résultats dans `results/`.

### Paramètres

Dans `erosion.py`, vous pouvez modifier :
- **Taille du kernel** : `kernel = np.ones((5,5), np.uint8)` (ligne 47)
- **Nombre d'itérations** : `iterations=1` (ligne 49)

## Fichiers de test

- `HorseHead.fits` : Nébuleuse (noir et blanc)
- `test_M31_linear.fits` : Galaxie d'Andromède (couleur)
- `test_M31_raw.fits` : Galaxie d'Andromède (couleur, brute)

  ## Phase 1 : Observations et résultats

### Tests effectués

Nous avons testé l'érosion morphologique sur différentes images FITS avec plusieurs combinaisons de paramètres :

#### Image HorseHead.fits (noir et blanc)
- **Kernel (3,3), 1 itération** : Réduction modérée des étoiles, préservation acceptable des détails
- **Kernel (5,5), 1 itération** : Réduction plus marquée, légère perte de détails sur les bords
- **Kernel (3,3), 3 itérations** : Effet cumulatif important, étoiles bien réduites mais artefacts visibles

#### Image test_M31_raw.fits (couleur)
- **Kernel (2,2), 4 itérations** : Réduction progressive, bon compromis pour les étoiles moyennes
- **Kernel (5,5), 2 itérations** : Réduction efficace mais impact sur les structures fines

### Résultats observés

 **Avantages de l'érosion simple** :
- Réduction effective du diamètre apparent des étoiles brillantes
- Implémentation simple et rapide
- Traitement uniforme sur toute l'image

 **Inconvénients majeurs identifiés** :

1. **Perte de détails de la nébuleuse** :
   - L'érosion globale affecte également les structures fines de la nébuleuse
   - Les filaments de gaz et les piliers de poussière sont "écrasés" ou atténués
   - Les zones de faible luminosité perdent en contraste

2. **Artefacts visibles** :
   - Création de halos sombres autour des étoiles trop érodées
   - Perte de texture naturelle dans les zones de transition
   - Apparition de contours artificiels sur les structures étendues

3. **Manque de sélectivité** :
   - Impossible de distinguer les étoiles du fond de ciel
   - Tous les objets brillants sont traités de la même manière
   - Les nœuds de gaz brillants dans la nébuleuse sont également réduits

4. **Paramètres non adaptatifs** :
   - Un même kernel ne convient pas aux étoiles de différentes tailles
   - Les petites étoiles peuvent disparaître complètement
   - Les grandes étoiles nécessitent un traitement plus agressif

### Conclusion Phase 1

L'érosion simple démontre la faisabilité de la réduction d'étoiles, mais elle n'est **pas adaptée pour un traitement scientifique** car elle altère l'intégrité des données de la nébuleuse.

**Nécessité de la Phase 2** : Il est impératif de développer un algorithme sélectif qui :
- Détecte uniquement les étoiles (masque binaire)
- Applique l'érosion seulement sur les zones d'étoiles
- Préserve intégralement les détails de la nébuleuse

## État du projet

- [x] Phase 1 : Érosion simple
- [ ] Phase 2 - Étape A : Création du masque d'étoiles
- [ ] Phase 2 - Étape B : Réduction localisée
- [ ] Phase 3 : Prolongements (optionnel)

## Références

- Documentation OpenCV : https://docs.opencv.org/3.4/db/df6/tutorial_erosion_dilatation.html
- Documentation Astropy : https://docs.astropy.org/
