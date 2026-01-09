from astropy.io import fits    # pour lire les fichiers .fits
import matplotlib.pyplot as plt  # pour sauvegarder les images
import cv2 as cv               # pour les operations morphologiques
import numpy as np             # pour les calculs

# ouverture du fichier fits
fichier_fits = './examples/HorseHead.fits'
hdul = fits.open(fichier_fits)

# affichage des infos (juste pour verifier)
hdul.info()

# recuperation de l'image
donnees = hdul[0].data

# en-tete (pas utilise mais garde au cas ou)
en_tete = hdul[0].header

# ==================================================
# gestion image couleur / noir et blanc
# ==================================================

if donnees.ndim == 3:  # image couleur

    # certains fits ont les canaux en premier
    if donnees.shape[0] == 3:
        donnees = np.transpose(donnees, (1, 2, 0))

    # normalisation pour sauvegarder l'original
    donnees_normalisees = (donnees - donnees.min()) / (donnees.max() - donnees.min())
    plt.imsave('./results/original.png', donnees_normalisees)

    # conversion en uint8 pour opencv (par canal)
    image = np.zeros_like(donnees, dtype='uint8')
    for i in range(donnees.shape[2]):
        canal = donnees[:, :, i]
        image[:, :, i] = ((canal - canal.min()) /
                          (canal.max() - canal.min()) * 255).astype('uint8')

    # opencv travaille en BGR au lieu de RGB
    image = cv.cvtColor(image, cv.COLOR_RGB2BGR)

else:
    # image noir et blanc
    plt.imsave('./results/original.png', donnees, cmap='gray')

    image = ((donnees - donnees.min()) /
             (donnees.max() - donnees.min()) * 255).astype('uint8')

# ==================================================
# phase 1 : erosion / dilatation globale
# ==================================================

noyau = np.ones((5, 5), np.uint8)

# erosion : reduit surtout les etoiles
image_erodee = cv.erode(image, noyau, iterations=1)
cv.imwrite('./results/eroded.png', image_erodee)

# dilatation : permet de garder les structures etendues
image_dilatee = cv.dilate(image_erodee, noyau, iterations=1)
cv.imwrite('./results/dilated.png', image_dilatee)

# ==================================================
# phase 2 : reduction selective des etoiles
# ==================================================

# creation du masque d'etoiles
if image.ndim == 3:
    gris = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
else:
    gris = image.copy()

# seuil base sur la luminosite
# j'ai testé avec 90, 85, 88... 88 ça marche bien pour capturer assez d'étoiles
valeur_seuil = np.percentile(gris, 88)
_, masque_binaire = cv.threshold(gris, valeur_seuil, 255, cv.THRESH_BINARY)

# nettoyage du masque
noyau_nettoyage = np.ones((3, 3), np.uint8)
masque_ouvert = cv.morphologyEx(masque_binaire, cv.MORPH_OPEN,
                                noyau_nettoyage, iterations=1)
masque_nettoye = cv.morphologyEx(masque_ouvert, cv.MORPH_CLOSE,
                                 noyau_nettoyage, iterations=1)

# on dilate pour bien couvrir les halos
# 2 itérations, 1 n'est pas suffisante
masque_dilate = cv.dilate(masque_nettoye, noyau_nettoyage, iterations=2)

# flou pour eviter les transitions trop dures
masque_floute = cv.GaussianBlur(masque_dilate.astype(np.float32),
                                (9, 9), sigmaX=1.5, sigmaY=1.5)

masque_normalise = masque_floute / 255.0
# j'ai essayé avec 1.8 mais ça faisait des trous, 1.4 c'est mieux
masque_normalise = np.clip(masque_normalise * 1.4, 0, 1)

plt.imsave('./results/masque.png', masque_normalise, cmap='gray')

# reduction des etoiles
noyau_erosion = np.ones((5, 5), np.uint8)
image_erodee_selective = cv.erode(image, noyau_erosion, iterations=1)

# ==================================================
# combinaison finale
# ==================================================

# on convertit en float pour les calculs
image_float = image.astype(np.float32)
image_erodee_float = image_erodee_selective.astype(np.float32)

if image.ndim == 3:
    masque_3d = np.stack([masque_normalise] * 3, axis=2)
else:
    masque_3d = masque_normalise

# on applique la formule
image_finale = masque_3d * image_erodee_float + (1 - masque_3d) * image_float

image_finale_uint8 = np.clip(image_finale, 0, 255).astype(np.uint8)

cv.imwrite('./results/resultat.png', image_finale_uint8)

# fermeture du fits
hdul.close()
