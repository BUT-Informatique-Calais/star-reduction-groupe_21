import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import cv2 as cv

# ============================================
# Comparateur Avant/Après - Animation de Superposition
# ============================================

def load_image_from_png(png_path):
    """Charge une image depuis un fichier PNG"""
    img = plt.imread(png_path)
    # Si l'image a un canal alpha (RGBA), on le supprime
    if img.ndim == 3 and img.shape[2] == 4:
        img = img[:, :, :3]  # Garder seulement RGB
    return img

def normalize_to_grayscale(img):
    """Convertit une image en niveaux de gris si nécessaire"""
    if img.ndim == 3:
        # Image couleur : convertir en niveaux de gris
        if img.shape[2] == 3:
            # RGB : moyenne pondérée
            gray = 0.299 * img[:, :, 0] + 0.587 * img[:, :, 1] + 0.114 * img[:, :, 2]
        else:
            # Autre format : moyenne simple
            gray = np.mean(img, axis=2)
        return gray
    else:
        # Déjà en niveaux de gris
        return img

def prepare_images_for_comparison(img1, img2):
    """Prépare les deux images pour la comparaison (même taille, même format)"""
    # Convertir en niveaux de gris si nécessaire
    img1_gray = normalize_to_grayscale(img1)
    img2_gray = normalize_to_grayscale(img2)
    
    # S'assurer que les images ont la même taille
    if img1_gray.shape != img2_gray.shape:
        # Redimensionner img2 pour correspondre à img1
        img2_gray = cv.resize(img2_gray, (img1_gray.shape[1], img1_gray.shape[0]))
    
    # Normaliser entre 0 et 1
    img1_norm = (img1_gray - img1_gray.min()) / (img1_gray.max() - img1_gray.min() + 1e-10)
    img2_norm = (img2_gray - img2_gray.min()) / (img2_gray.max() - img2_gray.min() + 1e-10)
    
    return img1_norm, img2_norm

def create_blending_animation(original, processed, output_path, duration=3, fps=10):
    """
    Crée une animation où l'image originale et traitée se superposent
    avec un effet de fondu (fade in/fade out)
    """
    # Préparer les images
    img1, img2 = prepare_images_for_comparison(original, processed)
    
    # Créer la figure
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.axis('off')
    ax.set_title('Comparaison Avant/Après - Animation de Superposition', 
                 fontsize=16, fontweight='bold', pad=20)
    
    # Afficher l'image originale en premier
    im = ax.imshow(img1, cmap='gray', animated=True)
    
    # Nombre de frames pour l'animation
    num_frames = duration * fps
    
    def animate(frame):
        # Calculer l'alpha (transparence) pour le fondu
        # Va de 0 à 1 puis de 1 à 0 (cycle complet)
        cycle = (frame % (num_frames * 2)) / num_frames
        
        if cycle <= 1.0:
            # Transition : Originale vers Traitée (Phase 2)
            alpha = cycle
            blended = (1 - alpha) * img1 + alpha * img2
            label = "Image Originale → Image Traitée (Phase 2)"
        else:
            # Transition : Traitée vers Originale (Phase 2)
            alpha = 2.0 - cycle
            blended = (1 - alpha) * img1 + alpha * img2
            label = "Image Traitée (Phase 2) → Image Originale"
        
        im.set_array(blended)
        ax.set_title(f'{label} ({int(alpha*100)}%)', 
                    fontsize=14, fontweight='bold')
        return [im]
    
    # Créer l'animation
    anim = animation.FuncAnimation(
        fig, animate, frames=num_frames * 2, 
        interval=1000/fps, blit=True, repeat=True
    )
    
    # Sauvegarder l'animation
    print(f"Génération de l'animation (cela peut prendre quelques secondes)...")
    anim.save(output_path, writer='pillow', fps=fps)
    print(f"✓ Animation sauvegardée : {output_path}")
    plt.close()

def create_simple_comparison(original, processed, output_path):
    """Crée une image simple côte à côte pour référence"""
    img1, img2 = prepare_images_for_comparison(original, processed)
    
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))
    
    axes[0].imshow(img1, cmap='gray')
    axes[0].set_title('Image Originale', fontsize=14, fontweight='bold')
    axes[0].axis('off')
    
    axes[1].imshow(img2, cmap='gray')
    axes[1].set_title('Image Traitée (Phase 2)', fontsize=14, fontweight='bold')
    axes[1].axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Comparaison côte à côte sauvegardée : {output_path}")
    plt.close()

# ============================================
# MAIN
# ============================================

print("="*60)
print("Comparateur Avant/Après - Phase 2")
print("Animation de Superposition")
print("="*60)

# Comparaison Phase 2 uniquement
original_path = './results/original.png'

# Chercher l'image Phase 2 (priorité : resultat_normal.png > resultat.png > phase2_final.png)
phase2_paths = [
    './results/resultat_normal.png',  # Meilleure qualité (normalisée)
    './results/resultat.png',         # Version uint8
    './results/phase2_final.png'      # Ancien nom (compatibilité)
]

phase2_path = None
for path in phase2_paths:
    import os
    if os.path.exists(path):
        phase2_path = path
        break

try:
    # Charger l'image originale
    original = load_image_from_png(original_path)
    print(f"✓ Image originale chargée : {original.shape}")
    
    if phase2_path is None:
        raise FileNotFoundError("Aucune image Phase 2 trouvée (resultat_normal.png, resultat.png ou phase2_final.png)")
    
    # Charger l'image Phase 2
    processed_phase2 = load_image_from_png(phase2_path)
    print(f"✓ Image Phase 2 chargée : {processed_phase2.shape} (depuis {phase2_path})")
    
    print("\nGénération de l'animation...")
    # Créer l'animation
    create_blending_animation(
        original, processed_phase2,
        './results/comparison_animation_phase2.gif',
        duration=2, fps=8
    )
    
    # Créer aussi une image côte à côte
    create_simple_comparison(
        original, processed_phase2,
        './results/comparison_side_phase2.png'
    )
    
    print("\n" + "="*60)
    print("Comparaison terminée avec succès !")
    print("="*60)
    print("\nFichiers générés :")
    print("- results/comparison_animation_phase2.gif : Animation de superposition")
    print("- results/comparison_side_phase2.png : Comparaison côte à côte")
    
except FileNotFoundError as e:
    print(f"\n  Fichier non trouvé : {e}")
    print("\n" + "="*60)
    print("Instructions :")
    print("="*60)
    print("1. Assurez-vous que 'results/original.png' existe")
    print("2. Exécutez d'abord : python erosion.py")
    print("   Cela générera 'results/resultat_normal.png' (Phase 2)")
    print("3. Ou placez manuellement une image Phase 2 dans results/")
    print("   (resultat_normal.png, resultat.png ou phase2_final.png)")
    print("4. Relancez : python comparator.py")
    print("\nLe comparateur fonctionnera automatiquement une fois le fichier présent !")
