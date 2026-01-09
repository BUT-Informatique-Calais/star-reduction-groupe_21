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
├── batch_processing.py     # Traitement en lot de plusieurs fichiers FITS
├── comparator.py           # Comparateur Avant/Après (Phase 3 optionnelle)
├── examples/               # Fichiers FITS de test
│   ├── HorseHead.fits
│   ├── test_M31_linear.fits
│   └── test_M31_raw.fits
├── results/                # Images de sortie
│   ├── original.png       # Image originale
│   ├── eroded.png         # Phase 1 : après érosion
│   ├── dilated.png        # Phase 1 : après dilatation (ouverture)
│   ├── masque.png         # Phase 2 : masque d'étoiles
│   ├── resultat.png       # Phase 2 : résultat final (brut)
│   ├── resultat_normal.png # Phase 2 : résultat final (normalisé)
│   ├── comparison_animation_phase2.gif  # Phase 3 : animation de comparaison
│   ├── comparison_side_phase2.png       # Phase 3 : comparaison côte à côte
│   └── batch_output/      # Résultats du batch processing
│       ├── *_processed.png # Images traitées (une par fichier FITS)
├── requirements.txt
└── README.md
```

## Utilisation

```bash
python erosion.py
```

Le script charge l'image FITS spécifiée (par défaut `test_M31_linear.fits`), applique les traitements des Phase 1 et Phase 2, et sauvegarde les résultats dans `results/`.

### Paramètres

Dans `erosion.py`, vous pouvez modifier :
- **Fichier FITS** : `fichier_fits = './examples/test_M31_linear.fits'` (ligne 7)
- **Taille du kernel** : `noyau = np.ones((5,5), np.uint8)` (ligne 47)
- **Nombre d'itérations** : `iterations=1` (ligne 50, 54)

## Fichiers de test

- `HorseHead.fits` : Nébuleuse (noir et blanc)
- `test_M31_linear.fits` : Galaxie d'Andromède (couleur)
- `test_M31_raw.fits` : Galaxie d'Andromède (couleur, brute)

## Phase 1 : Érosion et Dilatation globale

### Principe

La Phase 1 consiste à appliquer une **ouverture morphologique** (érosion suivie de dilatation) sur toute l'image :

- **Érosion** : Réduit la taille des étoiles en remplaçant chaque pixel par le minimum de son voisinage
- **Dilatation** : Restaure les structures étendues (nébuleuses) tout en conservant la réduction des étoiles

Cette méthode simple permet de valider le concept mais présente des limitations importantes.

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

L'ouverture morphologique globale démontre la faisabilité de la réduction d'étoiles, mais elle n'est **pas adaptée pour un traitement scientifique** car elle altère l'intégrité des données de la nébuleuse.

**Nécessité de la Phase 2** : Il est impératif de développer un algorithme sélectif qui :

- Détecte uniquement les étoiles (masque binaire)
- Applique l'érosion seulement sur les zones d'étoiles
- Préserve intégralement les détails de la nébuleuse

## Phase 2 : Réduction sélective avec masque d'étoiles

### Principe

La Phase 2 implémente un algorithme sélectif qui ne traite que les zones d'étoiles, préservant ainsi les détails de la nébuleuse.

### Étape A : Création du masque d'étoiles

1. **Conversion en niveaux de gris** : L'image est convertie en gris pour la détection
2. **Seuillage adaptatif** : Utilisation d'un seuil basé sur le percentile (88%) pour détecter les pixels les plus brillants
3. **Nettoyage morphologique** : Ouverture puis fermeture pour éliminer le bruit et boucher les petits trous
4. **Dilatation** : 2 itérations pour couvrir toute l'étoile, y compris les halos
5. **Flou gaussien** : Adoucit les transitions pour éviter les halos artificiels
6. **Renforcement** : Le masque est multiplié par 1.4 pour un effet plus visible

### Étape B : Réduction des étoiles

Application d'une **ouverture morphologique** (érosion puis dilatation) uniquement sur les zones détectées comme étoiles :

- Kernel de taille (5,5)
- 1 itération d'érosion puis 1 itération de dilatation

### Étape C : Combinaison avec l'image originale

La formule de combinaison permet de mélanger intelligemment l'image érodée et l'image originale :

```
I_final = M × I_erode + (1-M) × I_original
```

Où :

- `M` est le masque normalisé (entre 0 et 1)
- `I_erode` est l'image après ouverture morphologique
- `I_original` est l'image originale

**Résultat** : Les étoiles sont réduites là où le masque est fort, tandis que la nébuleuse reste intacte.

### Paramètres ajustables

Dans `erosion.py`, vous pouvez modifier :

- **Percentile du seuil** : `valeur_seuil = np.percentile(gris, 88)` (ligne 70) - Plus bas = plus d'étoiles détectées
- **Itérations de dilatation du masque** : `iterations=2` (ligne 80) - Plus d'itérations = masque plus large
- **Renforcement du masque** : `masque_normalise * 1.4` (ligne 87) - Plus élevé = effet plus fort
- **Taille du kernel d'érosion** : `noyau_erosion = np.ones((5, 5), np.uint8)` (ligne 95)

### Résultats Phase 2

**Avantages** :

- Réduction sélective des étoiles sans affecter la nébuleuse
- Préservation des détails fins (filaments, piliers de poussière)
- Pas d'artefacts majeurs sur les structures étendues
- Méthode adaptative selon la luminosité des étoiles

**Limitations observées** :

- Quelques petits "trous" peuvent apparaître autour des étoiles très brillantes si les paramètres sont trop agressifs
- Le masque peut parfois capturer des zones de nébuleuse très brillantes
- Nécessite un ajustement des paramètres selon l'image

## Phase 3 : Comparateur Avant/Après (optionnel)

### Principe

Le comparateur permet de visualiser facilement les différences entre l'image originale et l'image traitée par la Phase 2. Il génère deux types de comparaisons :

1. **Animation de superposition** : Animation GIF avec effet de fondu entre l'image originale et l'image traitée
2. **Comparaison côte à côte** : Image statique montrant les deux versions simultanément

### Utilisation

```bash
# 1. Générer les images avec erosion.py
python erosion.py

# 2. Créer la comparaison automatiquement
python comparator.py
```

Le comparateur détecte automatiquement les fichiers générés par `erosion.py` et crée les comparaisons dans le dossier `results/`.

### Fonctionnalités

- **Détection automatique** : Le script cherche automatiquement les fichiers Phase 2 (priorité : `resultat_normal.png` > `resultat.png` > `phase2_final.png`)
- **Préparation des images** : Conversion automatique en niveaux de gris et normalisation pour une comparaison cohérente
- **Animation fluide** : Transition progressive avec indication du pourcentage de superposition
- **Comparaison claire** : Image côte à côte pour une visualisation directe

### Fichiers générés

- `results/comparison_animation_phase2.gif` : Animation de superposition (fondu progressif)
- `results/comparison_side_phase2.png` : Comparaison côte à côte (image statique)

### Avantages

- Visualisation claire des améliorations apportées par la Phase 2
- Animation intuitive pour présenter les résultats
- Outil utile pour la documentation et les présentations
- Génération automatique sans configuration supplémentaire

## Batch Processing : Traitement en lot

### Principe

Le script `batch_processing.py` permet de traiter automatiquement **plusieurs fichiers FITS** en une seule exécution. Il utilise exactement le même algorithme que `erosion.py` (Phase 2) pour garantir la cohérence des résultats.

### Fonctionnalités

- **Traitement automatique** : Scanne un dossier et traite tous les fichiers `.fits` et `.FITS`
- **Algorithme identique** : Utilise la même logique que `erosion.py` (Phase 2 : réduction sélective)
- **Paramètres configurables** : Tous les paramètres sont ajustables via la ligne de commande
- **Rapport détaillé** : Génère un fichier texte avec les statistiques de traitement
- **Gestion d'erreurs** : Continue le traitement même si un fichier échoue

### Structure du code

Le script est organisé en deux fonctions principales :

#### `process_single_fits()`

Traite un seul fichier FITS avec l'algorithme de réduction d'étoiles :

- **Chargement** : Ouvre le fichier FITS et gère les images couleur et monochrome
- **Phase 1 optionnelle** : Peut appliquer l'érosion/dilatation globale avant la Phase 2
- **Phase 2** : Applique la réduction sélective identique à `erosion.py`
  - Création du masque d'étoiles (seuillage, nettoyage, flou gaussien)
  - Érosion sélective des étoiles
  - Combinaison avec l'image originale
- **Sauvegarde** : Enregistre l'image traitée dans le dossier de sortie

## Phase 3 : `batch_process()(optionnel)`

Orchestre le traitement de tous les fichiers FITS d'un dossier :

- **Découverte automatique** : Trouve tous les fichiers `.fits` et `.FITS` dans le dossier d'entrée
- **Traitement séquentiel** : Traite chaque fichier un par un
- **Suivi des résultats** : Compte les succès et les erreurs
- **Génération de rapport** : Crée un fichier `batch_report.txt` avec les détails

### Utilisation

#### Commande de base

```bash
python batch_processing.py
```

Traite tous les fichiers FITS du dossier `./examples/` et sauvegarde les résultats dans `./results/batch_output/`.

#### Options disponibles

```bash
python batch_processing.py --input ./examples/ --output ./results/batch_output/
```

#### Exemples d'utilisation

```bash
# Traitement simple avec paramètres par défaut
python batch_processing.py

# Spécifier les dossiers d'entrée et de sortie
python batch_processing.py -i ./examples/ -o ./results/batch_output/

# Activer la Phase 1 avant la Phase 2
python batch_processing.py --phase1

# Personnaliser tous les paramètres
python batch_processing.py \
  --input ./examples/ \
  --output ./results/batch_output/ \
  --phase1 \
  --kernel 5 \
  --iterations 1 \
  --threshold 88
```

### Fichiers générés

Pour chaque fichier FITS traité, le script génère :

- **`<nom_fichier>_processed.png`** : Image traitée avec réduction d'étoiles

Le script génère également :

- **`batch_report.txt`** : Rapport détaillé contenant :
  - Les paramètres utilisés
  - Le nombre de fichiers traités
  - Le nombre de succès et d'erreurs
  - La liste détaillée de chaque fichier avec son statut

### Paramètres par défaut

Les paramètres par défaut sont **identiques à ceux de `erosion.py`** pour garantir la cohérence :

- **Kernel** : `5x5` (même taille que dans `erosion.py`)
- **Itérations** : `1` (même nombre que dans `erosion.py`)
- **Seuil** : `88%` (même percentile que dans `erosion.py`)
- **Phase 1** : Désactivée par défaut (comme dans `erosion.py` où elle est toujours exécutée)

### Avantages

- **Efficacité** : Traite plusieurs images sans intervention manuelle
- **Cohérence** : Utilise exactement le même algorithme que `erosion.py`
- **Flexibilité** : Paramètres ajustables pour chaque exécution
- **Traçabilité** : Rapport détaillé pour suivre le traitement
- **Robustesse** : Continue même si un fichier échoue

### Limitations

- **Traitement séquentiel** : Les fichiers sont traités un par un (pas de parallélisation)
- **Même algorithme pour tous** : Tous les fichiers utilisent les mêmes paramètres
- **Pas de prévisualisation** : Les résultats sont générés directement sans aperçu

### Cas d'usage

Le batch processing est particulièrement utile pour :

- Traiter un grand nombre d'images astronomiques
- Appliquer le même traitement à plusieurs observations
- Automatiser le workflow de réduction d'étoiles
- Générer des résultats pour une analyse comparative

## État du projet

- [x] Phase 1 : Érosion et dilatation globale (ouverture morphologique)
- [x] Phase 2 - Étape A : Création du masque d'étoiles
- [x] Phase 2 - Étape B : Réduction localisée
- [x] Phase 2 - Étape C : Combinaison avec l'image originale
- [x] Phase 3 : Comparateur Avant/Après (optionnel)
- [x] Phase 3 : Batch Processing : Traitement en lot de plusieurs fichiers FITS (optionnel)

## Références

- Documentation OpenCV : https://docs.opencv.org/3.4/db/df6/tutorial_erosion_dilatation.html
- Documentation Astropy : https://docs.astropy.org/
