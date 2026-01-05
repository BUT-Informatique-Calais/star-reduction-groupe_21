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

## État du projet

- [x] Phase 1 : Érosion simple
- [ ] Phase 2 - Étape A : Création du masque d'étoiles
- [ ] Phase 2 - Étape B : Réduction localisée
- [ ] Phase 3 : Prolongements (optionnel)

## Références

- Documentation OpenCV : https://docs.opencv.org/3.4/db/df6/tutorial_erosion_dilatation.html
- Documentation Astropy : https://docs.astropy.org/
