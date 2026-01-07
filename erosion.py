from astropy.io import fits    #pour lire les fichier .fits
import matplotlib.pyplot as plt  #pour sauvegarder les images
import cv2 as cv   #pour l'erosion
import numpy as np   #pour les calculs

# Chargement du fichier FITS
fichier_fits = './examples/test_M31_linear.fits'
hdul = fits.open(fichier_fits)

# Afficher les infos du fichier
hdul.info()

# Récupérer les données de l'image
donnees = hdul[0].data

# Récupérer l'en-tête (pas vraiment utilisé mais bon à avoir)
en_tete = hdul[0].header

# Gérer les images couleur et noir et blanc
if donnees.ndim == 3:  #verifier si l'image est en couleur 3 dimensions (height, width, channels)
    # Image couleur - besoin de transposer si les canaux sont en premier
    if donnees.shape[0] == 3:  # Si les canaux sont en premier: (3, height, width)
        donnees = np.transpose(donnees, (1, 2, 0))
    
    # Normaliser l'image entière pour matplotlib [0, 1]
    donnees_normalisees = (donnees - donnees.min()) / (donnees.max() - donnees.min())
    
    # Sauvegarder l'image originale
    plt.imsave('./results/original.png', donnees_normalisees)
    
    # Normaliser chaque canal séparément pour OpenCV [0, 255]
    image = np.zeros_like(donnees, dtype='uint8')
    for i in range(donnees.shape[2]):
        canal = donnees[:, :, i]
        image[:, :, i] = ((canal - canal.min()) / (canal.max() - canal.min()) * 255).astype('uint8')
else:
    # Image monochrome
    plt.imsave('./results/original.png', donnees, cmap='gray')
    
    # Convertir en uint8 pour OpenCV
    image = ((donnees - donnees.min()) / (donnees.max() - donnees.min()) * 255).astype('uint8')



# =========================
# PHASE 1 : ÉROSION/DILATATION GLOBALE
# =========================

# Définir le noyau pour l'érosion et la dilatation
noyau = np.ones((5,5), np.uint8)

# Érosion : réduit la taille des étoiles
image_erodee = cv.erode(image, noyau, iterations=1)
cv.imwrite('./results/eroded.png', image_erodee)

# Dilatation : restaure les structures étendues (ouverture = érosion puis dilatation)
image_dilatee = cv.dilate(image_erodee, noyau, iterations=1)
cv.imwrite('./results/dilated.png', image_dilatee)

# =========================
# PHASE 2 : REDUCTION SELECTIVE
# =========================

# A. Création du masque d'étoiles
# On convertit en niveaux de gris pour détecter les étoiles
if image.ndim == 3:
    gris = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
else:
    gris = image.copy()

# On utilise un seuil basé sur le percentile pour détecter les pixels les plus brillants
# J'ai testé avec 95 mais ça capturait pas assez d'étoiles, 88 c'est mieux
valeur_seuil = np.percentile(gris, 88)
_, masque_binaire = cv.threshold(gris, valeur_seuil, 255, cv.THRESH_BINARY)

# Nettoyage morphologique : ouverture pour enlever le bruit puis fermeture pour boucher les trous
noyau_nettoyage = np.ones((3, 3), np.uint8)
masque_ouvert = cv.morphologyEx(masque_binaire, cv.MORPH_OPEN, noyau_nettoyage, iterations=1)
masque_nettoye = cv.morphologyEx(masque_ouvert, cv.MORPH_CLOSE, noyau_nettoyage, iterations=1)

# Dilatation pour s'assurer de couvrir toute l'étoile (y compris les halos)
# 2 itérations ça marche bien, 1 c'était pas assez
masque_dilate = cv.dilate(masque_nettoye, noyau_nettoyage, iterations=2)

# Flou gaussien pour adoucir les transitions (évite les halos)
masque_floute = cv.GaussianBlur(masque_dilate.astype(np.float32), (9, 9), sigmaX=1.5, sigmaY=1.5)
masque_normalise = masque_floute / 255.0
# Renforcer le masque pour un effet plus visible
# J'ai essayé avec 1.8 mais ça faisait des trous, 1.4 c'est un bon compromis
masque_normalise = np.clip(masque_normalise * 1.4, 0, 1)

# Sauvegarde du masque pour vérification
plt.imsave('./results/masque.png', masque_normalise, cmap='gray')

# B. Réduction des étoiles
# On applique une ouverture morphologique (érosion puis dilatation)
# pour réduire les étoiles sans affecter la nébuleuse
noyau_erosion = np.ones((5, 5), np.uint8)
image_erodee_selective = cv.erode(image, noyau_erosion, iterations=1)
image_ouverte_selective = cv.dilate(image_erodee_selective, noyau_erosion, iterations=1)

# C. Combinaison avec l'image originale
# On convertit en float pour les calculs
image_float = image.astype(np.float32)
image_ouverte_float = image_ouverte_selective.astype(np.float32)

# Adapter le masque aux dimensions de l'image (couleur ou noir et blanc)
if image.ndim == 3:
    masque_3d = np.stack([masque_normalise]*3, axis=2)
else:
    masque_3d = masque_normalise

# Formule de combinaison : I_final = M * I_erode + (1-M) * I_original
image_finale = masque_3d * image_ouverte_float + (1 - masque_3d) * image_float

# Conversion et sauvegarde
image_finale_uint8 = np.clip(image_finale, 0, 255).astype(np.uint8)

# Sauvegarder le résultat final
cv.imwrite('./results/resultat.png', image_finale_uint8)

# Sauvegarder aussi avec matplotlib pour avoir les mêmes couleurs que l'original
if image.ndim == 3:
    image_finale_normalisee = (image_finale - image_finale.min()) / (image_finale.max() - image_finale.min())
    plt.imsave('./results/resultat_normal.png', image_finale_normalisee)
else:
    image_finale_normalisee = (image_finale - image_finale.min()) / (image_finale.max() - image_finale.min())
    plt.imsave('./results/resultat_normal.png', image_finale_normalisee, cmap='gray')

# Fermer le fichier
hdul.close()
