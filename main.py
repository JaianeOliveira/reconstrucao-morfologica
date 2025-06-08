import cv2
import numpy as np

def eliminate_small_objects(img_bin, min_size):
    """
    Remove componentes conectados com área menor que min_size.
    img_bin: imagem binária (0 ou 255)
    min_size: área mínima em pixels para manter o objeto
    """
    # encontra componentes conectados
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(img_bin, connectivity=8)
    output = np.zeros_like(img_bin)
    # percorre cada componente (label 1..N)
    for label in range(1, num_labels):
        area = stats[label, cv2.CC_STAT_AREA]
        if area >= min_size:
            output[labels == label] = 255
    return output

def fill_holes(img_bin):
    """
    Preenche buracos (background interno) nos objetos.
    img_bin: imagem binária (0 ou 255)
    """
    # inverte para que buracos virem objetos
    inv = cv2.bitwise_not(img_bin)
    # flood fill do fundo
    h, w = inv.shape
    mask = np.zeros((h+2, w+2), np.uint8)
    cv2.floodFill(inv, mask, (0,0), 255)
    # inverte floodfilled e combina com original
    inv_flood = cv2.bitwise_not(inv)
    filled = cv2.bitwise_or(img_bin, inv_flood)
    return filled

def separate_connected_objects(img_bin):
    """
    Separa objetos conectados usando distância e watershed.
    img_bin: imagem binária (0 ou 255)
    """
    # distância ao fundo
    dist = cv2.distanceTransform(img_bin, cv2.DIST_L2, 5)
    # normaliza e limiariza para detectar "seeds"
    _, sure_fg = cv2.threshold(dist, 0.5*dist.max(), 255, 0)
    sure_fg = np.uint8(sure_fg)
    # região incerta
    sure_bg = cv2.dilate(img_bin, np.ones((3,3), np.uint8), iterations=3)
    unknown = cv2.subtract(sure_bg, sure_fg)
    # marcadores
    num_markers, markers = cv2.connectedComponents(sure_fg)
    markers = markers + 1  # para que o fundo seja 1, objetos comece em 2
    markers[unknown==255] = 0
    # watershed precisa de BGR
    img_color = cv2.cvtColor(img_bin, cv2.COLOR_GRAY2BGR)
    cv2.watershed(img_color, markers)
    # pixels marcados por watershed (bordas) viram 0
    separated = np.zeros_like(img_bin)
    separated[markers > 1] = 255
    return separated

if __name__ == "__main__":
    # exemplo de uso
    img = cv2.imread("assets/teste.png", cv2.IMREAD_GRAYSCALE)
    # binariza
    _, img_bin = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

    # 1) Elimina pequenos objetos (<500 pixels)
    no_small = eliminate_small_objects(img_bin, min_size=500)
    cv2.imwrite("assets/sem_pequenos.png", no_small)

    # 2) Preenche buracos em objetos
    filled = fill_holes(img_bin)
    cv2.imwrite("assets/buracos_preenchidos.png", filled)

    # 3) Separa objetos conectados
    separated = separate_connected_objects(img_bin)
    cv2.imwrite("assets/separados.png", separated)

    print("Processamento concluído!")
