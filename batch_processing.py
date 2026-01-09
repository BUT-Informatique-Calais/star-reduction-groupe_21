from astropy.io import fits
import matplotlib.pyplot as plt
import cv2 as cv
import numpy as np
import os
import glob
from pathlib import Path

# ============================================
# Batch Processing : Traitement de plusieurs fichiers FITS
# ============================================

def process_single_fits(fits_path, output_dir, use_phase1=False, kernel_size=5, iterations=1, threshold_percentile=88):
    """
    Traite un seul fichier FITS avec l'algorithme identique à erosion.py
    
    Parameters:
    - fits_path : chemin vers le fichier FITS
    - output_dir : dossier de sortie
    - use_phase1 : si True, applique aussi la Phase 1 (érosion/dilatation globale)
    - kernel_size : taille du kernel d'érosion (défaut: 5 comme dans erosion.py)
    - iterations : nombre d'itérations d'érosion (défaut: 1 comme dans erosion.py)
    - threshold_percentile : percentile pour le seuillage (défaut: 88 comme dans erosion.py)
    """
    try:
        # Charger le fichier FITS
        hdul = fits.open(fits_path)
        data = hdul[0].data
        
        # Gérer les images monochrome et couleur (identique à erosion.py)
        if data.ndim == 3:
            if data.shape[0] == 3:
                data = np.transpose(data, (1, 2, 0))
            
            # Normaliser pour OpenCV (uint8)
            image = np.zeros_like(data, dtype='uint8')
            for i in range(data.shape[2]):
                channel = data[:, :, i]
                image[:, :, i] = ((channel - channel.min()) / (channel.max() - channel.min()) * 255).astype('uint8')
        else:
            # Image monochrome
            image = ((data - data.min()) / (data.max() - data.min()) * 255).astype('uint8')
        
        # =========================
        # PHASE 1 : ÉROSION/DILATATION GLOBALE 
        # =========================
        if use_phase1:
            noyau = np.ones((5, 5), np.uint8)
            image_erodee = cv.erode(image, noyau, iterations=1)
            image_dilatee = cv.dilate(image_erodee, noyau, iterations=1)
            # On continue avec l'image après Phase 1
            image = image_dilatee
        
        # =========================
        # PHASE 2 : REDUCTION SELECTIVE (identique à erosion.py)
        # =========================
        
        # A. Création du masque d'étoiles
        # On convertit en niveaux de gris pour détecter les étoiles
        if image.ndim == 3:
            gris = cv.cvtColor(image, cv.COLOR_RGB2GRAY)
        else:
            gris = image.copy()
        
        # On utilise un seuil basé sur le percentile pour détecter les pixels les plus brillants
        valeur_seuil = np.percentile(gris, threshold_percentile)
        _, masque_binaire = cv.threshold(gris, valeur_seuil, 255, cv.THRESH_BINARY)
        
        # Nettoyage morphologique : ouverture pour enlever le bruit puis fermeture pour boucher les trous
        noyau_nettoyage = np.ones((3, 3), np.uint8)
        masque_ouvert = cv.morphologyEx(masque_binaire, cv.MORPH_OPEN, noyau_nettoyage, iterations=1)
        masque_nettoye = cv.morphologyEx(masque_ouvert, cv.MORPH_CLOSE, noyau_nettoyage, iterations=1)
        
        # Dilatation pour s'assurer de couvrir toute l'étoile (y compris les halos)
        masque_dilate = cv.dilate(masque_nettoye, noyau_nettoyage, iterations=2)
        
        # Flou gaussien pour adoucir les transitions (évite les halos)
        masque_floute = cv.GaussianBlur(masque_dilate.astype(np.float32), (9, 9), sigmaX=1.5, sigmaY=1.5)
        masque_normalise = masque_floute / 255.0
        # Renforcer le masque pour un effet plus visible
        masque_normalise = np.clip(masque_normalise * 1.4, 0, 1)
        
        # B. Réduction des étoiles
        # On applique une érosion pour réduire les étoiles
        noyau_erosion = np.ones((kernel_size, kernel_size), np.uint8)
        image_erodee_selective = cv.erode(image, noyau_erosion, iterations=iterations)
        
        # C. Combinaison avec l'image originale
        # On convertit en float pour les calculs
        image_float = image.astype(np.float32)
        image_erodee_float = image_erodee_selective.astype(np.float32)
        
        # Adapter le masque aux dimensions de l'image (couleur ou noir et blanc)
        if image.ndim == 3:
            masque_3d = np.stack([masque_normalise]*3, axis=2)
        else:
            masque_3d = masque_normalise
        
        # Formule de combinaison : I_final = (M × I_erode) + ((1-M) × I_original)
        image_finale = masque_3d * image_erodee_float + (1 - masque_3d) * image_float
        
        # Conversion et sauvegarde
        image_finale_uint8 = np.clip(image_finale, 0, 255).astype(np.uint8)
        
        # Sauvegarder le résultat
        fits_name = Path(fits_path).stem  # Nom du fichier sans extension
        output_path = os.path.join(output_dir, f"{fits_name}_processed.png")
        
        # Sauvegarder avec matplotlib pour avoir les mêmes couleurs que l'original
        if image_finale.ndim == 3:
            image_finale_normalisee = (image_finale - image_finale.min()) / (image_finale.max() - image_finale.min())
            plt.imsave(output_path, image_finale_normalisee)
        else:
            image_finale_normalisee = (image_finale - image_finale.min()) / (image_finale.max() - image_finale.min())
            plt.imsave(output_path, image_finale_normalisee, cmap='gray')
        
        hdul.close()
        return True, output_path
        
    except Exception as e:
        return False, str(e)

def batch_process(input_dir, output_dir, use_phase1=False, kernel_size=5, iterations=1, threshold_percentile=88):
    """
    Traite tous les fichiers FITS d'un dossier avec l'algorithme identique à erosion.py
    
    Parameters:
    - input_dir : dossier contenant les fichiers FITS
    - output_dir : dossier où sauvegarder les résultats
    - use_phase1 : si True, applique aussi la Phase 1 (érosion/dilatation globale)
    - kernel_size : taille du kernel d'érosion (défaut: 5 comme dans erosion.py)
    - iterations : nombre d'itérations (défaut: 1 comme dans erosion.py)
    - threshold_percentile : percentile pour le seuillage (défaut: 88 comme dans erosion.py)
    """
    # Créer le dossier de sortie s'il n'existe pas
    os.makedirs(output_dir, exist_ok=True)
    
    # Trouver tous les fichiers FITS
    fits_files = glob.glob(os.path.join(input_dir, "*.fits"))
    fits_files.extend(glob.glob(os.path.join(input_dir, "*.FITS")))  # Extension en majuscules aussi
    
    if not fits_files:
        print(f" Aucun fichier FITS trouvé dans {input_dir}")
        return
    
    print("="*60)
    print("Batch Processing - Traitement de plusieurs fichiers FITS")
    print("="*60)
    print(f"\nDossier d'entrée : {input_dir}")
    print(f"Dossier de sortie : {output_dir}")
    print(f"Paramètres :")
    print(f"  - Phase 1 (érosion/dilatation globale) : {'Activée' if use_phase1 else 'Désactivée'}")
    print(f"  - Taille du kernel : {kernel_size}x{kernel_size}")
    print(f"  - Itérations : {iterations}")
    print(f"  - Seuil (percentile) : {threshold_percentile}")
    print(f"\nFichiers à traiter : {len(fits_files)}")
    print("-"*60)
    
    # Traiter chaque fichier
    success_count = 0
    error_count = 0
    results = []
    
    for i, fits_file in enumerate(fits_files, 1):
        filename = os.path.basename(fits_file)
        print(f"\n[{i}/{len(fits_files)}] Traitement de : {filename}")
        
        success, result = process_single_fits(
            fits_file, output_dir, use_phase1, kernel_size, iterations, threshold_percentile
        )
        
        if success:
            print(f"  ✓ Succès → {os.path.basename(result)}")
            success_count += 1
            results.append((filename, "Succès", result))
        else:
            print(f"  ✗ Erreur : {result}")
            error_count += 1
            results.append((filename, "Erreur", result))
    
    # Rapport final
    print("\n" + "="*60)
    print("Rapport de traitement")
    print("="*60)
    print(f"Total de fichiers : {len(fits_files)}")
    print(f"  ✓ Succès : {success_count}")
    print(f"  ✗ Erreurs : {error_count}")
    print(f"\nRésultats sauvegardés dans : {output_dir}")
    
    # Sauvegarder un rapport texte
    report_path = os.path.join(output_dir, "batch_report.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("Rapport de Batch Processing\n")
        f.write("="*60 + "\n\n")
        f.write(f"Paramètres utilisés :\n")
        f.write(f"  - Phase 1 : {'Activée' if use_phase1 else 'Désactivée'}\n")
        f.write(f"  - Kernel : {kernel_size}x{kernel_size}\n")
        f.write(f"  - Itérations : {iterations}\n")
        f.write(f"  - Seuil : {threshold_percentile}%\n\n")
        f.write(f"Résultats :\n")
        f.write(f"  - Total : {len(fits_files)}\n")
        f.write(f"  - Succès : {success_count}\n")
        f.write(f"  - Erreurs : {error_count}\n\n")
        f.write("Détails par fichier :\n")
        f.write("-"*60 + "\n")
        for filename, status, info in results:
            f.write(f"{filename} : {status}\n")
            if status == "Succès":
                f.write(f"  → {os.path.basename(info)}\n")
            else:
                f.write(f"  → {info}\n")
    
    print(f"\nRapport détaillé sauvegardé : {report_path}")

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Batch Processing pour réduction d\'étoiles')
    parser.add_argument('--input', '-i', default='./examples/', 
                       help='Dossier contenant les fichiers FITS (défaut: ./examples/)')
    parser.add_argument('--output', '-o', default='./results/batch_output/', 
                       help='Dossier de sortie (défaut: ./results/batch_output/)')
    parser.add_argument('--phase1', action='store_true',
                       help='Activer la Phase 1 (érosion/dilatation globale) avant la Phase 2')
    parser.add_argument('--kernel', '-k', type=int, default=5,
                       help='Taille du kernel d\'érosion (défaut: 5, comme dans erosion.py)')
    parser.add_argument('--iterations', '-it', type=int, default=1,
                       help='Nombre d\'itérations (défaut: 1, comme dans erosion.py)')
    parser.add_argument('--threshold', '-t', type=int, default=88,
                       help='Percentile pour le seuillage (défaut: 88, comme dans erosion.py)')
    
    args = parser.parse_args()
    
    # Lancer le traitement
    batch_process(
        args.input,
        args.output,
        use_phase1=args.phase1,
        kernel_size=args.kernel,
        iterations=args.iterations,
        threshold_percentile=args.threshold
    )

