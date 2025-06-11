import os
import numpy as np
from PIL import Image


def dilate(image: np.ndarray, struct: np.ndarray) -> np.ndarray:
    """
    Dilatação manual de uma imagem em níveis de cinza.
    """
    h, w = image.shape
    sh, sw = struct.shape
    pad_h, pad_w = sh // 2, sw // 2
    padded = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='constant', constant_values=0)
    result = np.zeros_like(image)
    offsets = [(i - pad_h, j - pad_w) for i in range(sh) for j in range(sw) if struct[i, j]]
    for i in range(h):
        for j in range(w):
            vals = [padded[i + pad_h + di, j + pad_w + dj] for di, dj in offsets]
            result[i, j] = max(vals)
    return result


def erode(image: np.ndarray, struct: np.ndarray) -> np.ndarray:
    """
    Erosão manual de uma imagem em níveis de cinza.
    """
    h, w = image.shape
    sh, sw = struct.shape
    pad_h, pad_w = sh // 2, sw // 2
    padded = np.pad(image, ((pad_h, pad_h), (pad_w, pad_w)), mode='constant', constant_values=255)
    result = np.zeros_like(image)
    offsets = [(i - pad_h, j - pad_w) for i in range(sh) for j in range(sw) if struct[i, j]]
    for i in range(h):
        for j in range(w):
            vals = [padded[i + pad_h + di, j + pad_w + dj] for di, dj in offsets]
            result[i, j] = min(vals)
    return result


def geodesic_dilation(marker: np.ndarray, mask: np.ndarray, struct: np.ndarray) -> np.ndarray:
    """
    Dilatação condicional geodésica: dilate(marker) restrita a mask.
    """
    dil = dilate(marker, struct)
    return np.minimum(dil, mask)


def morphological_reconstruction(marker: np.ndarray, mask: np.ndarray, struct: np.ndarray) -> np.ndarray:
    """
    Reconstrução morfológica por dilatação geodésica até convergência.
    """
    prev = marker.copy()
    while True:
        curr = geodesic_dilation(prev, mask, struct)
        if np.array_equal(curr, prev):
            break
        prev = curr
    return curr


def synthetic_image_removal(size=(200,200), seed=0):
    img = np.zeros(size, dtype=np.uint8)
    img[20:80, 20:80] = 255
    img[120:180, 120:180] = 255
    np.random.seed(seed)
    coords = np.random.randint(0, size[0], (50,2))
    for y, x in coords:
        img[y, x] = 255
    return img


def synthetic_image_hole(size=(200,200), center=(100,100), outer_r=60, inner_r=30):
    img = np.zeros(size, dtype=np.uint8)
    yy, xx = np.ogrid[:size[0], :size[1]]
    mask = (xx-center[0])**2 + (yy-center[1])**2 <= outer_r**2
    img[mask] = 255
    hole = (xx-center[0])**2 + (yy-center[1])**2 <= inner_r**2
    img[hole] = 0
    return img


# ---- Processamento ----

def remove_small_objects(img: np.ndarray, struct: np.ndarray) -> np.ndarray:
    marker = erode(img, struct)
    return morphological_reconstruction(marker, img, struct)


def fill_holes(img: np.ndarray, struct: np.ndarray) -> np.ndarray:
    inv = 255 - img
    marker = np.zeros_like(inv)
    marker[0, :] = inv[0, :]
    marker[-1, :] = inv[-1, :]
    marker[:, 0] = inv[:, 0]
    marker[:, -1] = inv[:, -1]
    rec = morphological_reconstruction(marker, inv, struct)
    return 255 - rec



def main():
    os.makedirs('outputs', exist_ok=True)
    struct = np.ones((3,3), dtype=bool)

    # Caso 1: remoção de pequenos objetos
    img1 = synthetic_image_removal()
    res1 = remove_small_objects(img1, struct)
    Image.fromarray(img1).save('outputs/ex1_original.png')
    Image.fromarray(res1).save('outputs/ex1_result.png')

    # Caso 2: preenchimento de buracos
    img2 = synthetic_image_hole()
    res2 = fill_holes(img2, struct)
    Image.fromarray(img2).save('outputs/ex2_original.png')
    Image.fromarray(res2).save('outputs/ex2_result.png')


    print('Processamento concluído. Imagens salvas em outputs/')

if __name__ == '__main__':
    main()
