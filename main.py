import cv2
import numpy as np
from scipy.ndimage import distance_transform_edt, label

# 1. Carregar imagem em binário
def preprocess_image(path, threshold=127):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    _, binary = cv2.threshold(img, threshold, 255, cv2.THRESH_BINARY)
    return (binary > 0).astype(np.uint8) * 255, img  # binária, original

# 2. Remover pequenos objetos
def remove_small_objects_numpy(binary, min_size=150):
    labeled, num = label(binary)
    output = np.zeros_like(binary)
    for i in range(1, num + 1):
        if np.sum(labeled == i) >= min_size:
            output[labeled == i] = 255
    return output

# 3. Preencher buracos
def fill_holes_numpy(binary):
    inv = 255 - binary
    h, w = inv.shape
    mask = np.zeros((h + 2, w + 2), np.uint8)
    filled = inv.copy()
    cv2.floodFill(filled, mask, (0, 0), 128)
    holes = (filled == 0).astype(np.uint8) * 255
    return cv2.bitwise_or(binary, holes)

# 4. Separar objetos conectados com watershed
def watershed_numpy(binary):
    dist = distance_transform_edt(binary)
    dist = cv2.normalize(dist, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    _, sure_fg = cv2.threshold(dist, 0.6 * dist.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)
    unknown = cv2.subtract(binary, sure_fg)

    # Marcadores
    markers, _ = label(sure_fg)
    markers = markers + 1
    markers[unknown == 255] = 0

    # Aplicar watershed
    color = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    markers = markers.astype(np.int32)
    cv2.watershed(color, markers)

    # Colorir regiões
    output = np.zeros_like(color)
    max_label = markers.max()
    for i in range(2, max_label + 1):
        mask = markers == i
        color_val = np.random.randint(0, 255, size=3)
        output[mask] = color_val
    return output

# 5. Salvar resultados
def salvar_imagens(caminho, tipo):
    arquivo = caminho.split('/')[1]
    nome = arquivo.split('.')[0]
    binaria, original = preprocess_image(caminho)

    limpos = remove_small_objects_numpy(binaria, min_size=150)
    preenchido = fill_holes_numpy(limpos)
    separados = watershed_numpy(preenchido)

    match tipo:
        case "limpos":
            cv2.imwrite(f"results/{nome}_objetos_limpos.png", limpos)
        case "preenchido":
            cv2.imwrite(f"results/{nome}_buracos_preeenchidos.png", preenchido)
        case "separados":
            cv2.imwrite(f"results/{nome}_objetos_separados.png", separados)

# 6. Executar
if __name__ == "__main__":
    caminho_limpos = "assets/space.png"
    caminho_preenchido = "assets/space.png"
    caminho_separados = "assets/space.png"

    salvar_imagens(caminho_limpos, "limpos")
    salvar_imagens(caminho_limpos, "preenchido")
    salvar_imagens(caminho_limpos, "sepados

