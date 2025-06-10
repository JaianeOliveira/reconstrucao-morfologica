import os
import numpy as np
from skimage import morphology, util, draw, segmentation, measure
from skimage.morphology import erosion, reconstruction, disk
from skimage.io import imsave
from scipy import ndimage as ndi
from skimage.color import label2rgb

# Cria pasta de saída
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

# Funções de processamento
def eliminate_small_objects_reconstruction(image, selem, min_size):
    marker = erosion(image, selem)
    rec = reconstruction(marker, image, method='dilation')
    binary = rec > rec.mean()
    cleaned = morphology.remove_small_objects(binary, min_size)
    return cleaned

def fill_holes_reconstruction(image):
    inv = util.invert(image)
    marker = np.copy(inv)
    marker[1:-1, 1:-1] = inv.max()
    rec = reconstruction(marker, inv, method='erosion')
    filled = util.invert(rec)
    return filled

def separate_objects_watershed(image):
    binary = image > image.mean()
    distance = ndi.distance_transform_edt(binary)
    local_maxi = morphology.local_maxima(distance)
    markers = measure.label(local_maxi)
    labels = segmentation.watershed(-distance, markers, mask=binary)
    return labels

# Geradores de imagens de teste
def gen_small_objects_image():
    img = np.zeros((200, 200), dtype=np.uint8)
    rr, cc = draw.disk((100, 100), 60)
    img[rr, cc] = 255
    rng = np.random.RandomState(42)
    coords = rng.randint(0, 200, (200, 2))
    img[coords[:,0], coords[:,1]] = 255
    return img

def gen_holes_image():
    img = np.zeros((200, 200), dtype=np.uint8)
    rr, cc = draw.disk((100, 100), 80)
    img[rr, cc] = 255
    rng = np.random.RandomState(24)
    for center in [(80,80), (120,120), (80,120)]:
        r = rng.randint(5, 15)
        rr, cc = draw.disk(center, r)
        img[rr, cc] = 0
    return img

def gen_touching_objects_image():
    img = np.zeros((200, 200), dtype=np.uint8)
    rr, cc = draw.disk((100, 80), 50)
    img[rr, cc] = 255
    rr, cc = draw.disk((100, 120), 50)
    img[rr, cc] = 255
    return img

# Gera e salva originais
small_img = gen_small_objects_image()
imsave(os.path.join(output_dir, 'original_small_objects.png'), small_img)

holes_img = gen_holes_image()
imsave(os.path.join(output_dir, 'original_holes.png'), holes_img)

touch_img = gen_touching_objects_image()
imsave(os.path.join(output_dir, 'original_touching_objects.png'), touch_img)

# Processa e salva resultados
cleaned = eliminate_small_objects_reconstruction(small_img, disk(3), min_size=500)
imsave(os.path.join(output_dir, 'cleaned_objects.png'), (cleaned * 255).astype(np.uint8))

filled = fill_holes_reconstruction(holes_img)
imsave(os.path.join(output_dir, 'filled_holes.png'), (filled * 255).astype(np.uint8))

labels = separate_objects_watershed(touch_img)
colored = (label2rgb(labels, image=touch_img, bg_label=0) * 255).astype(np.uint8)
imsave(os.path.join(output_dir, 'separated_objects.png'), colored)

print(f"Arquivos salvos em '{output_dir}/':")
for fname in os.listdir(output_dir):
    print("- " + fname)
