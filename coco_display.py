import prodigy
from prodigy.components.loaders import JSON
from prodigy.util import split_string, log

import os
import base64
import mimetypes

from pycocotools.coco import COCO

ADD_BOUNDING_BOX_HARDCODED=True

if ADD_BOUNDING_BOX_HARDCODED:
    import PIL
    from PIL import ImageDraw

    def add_bounding_box(image_path, annotation):
        im = PIL.Image.open(image_path)
        [x, y, w, h] = annotation['bbox']
        draw = ImageDraw.Draw(im)
        draw.rectangle(((x, y), (x+w, y+h)), outline="red")
        return im


def img_to_data(path):
    """Convert a file (specified by a path) into a data URI."""
    if not os.path.exists(path):
        raise FileNotFoundError
    mime, _ = mimetypes.guess_type(path)
    with open(path, 'rb') as fp:
        data = fp.read()
        data64 = b''.join(base64.encodestring(data).splitlines())
        return 'data:{};base64,{}'.format(mime, data64.decode("utf-8"))

def process_coco_json(annotations, source):
    coco_filename = annotations
    coco_dataset = COCO(coco_filename)
    categories = coco_dataset.cats
    for img_id, img in coco_dataset.imgs.items():
        image_filename =  os.path.join(source, img['file_name'])
        image_encoded = img_to_data(image_filename)

        for annotation in coco_dataset.imgToAnns[img_id]:
            if ADD_BOUNDING_BOX_HARDCODED: 
                # overwrite image_encoded with one that has the rectangle
                # hardcoded on the img.
                TEMP_IMAGE_FILENAME = "temp_image"
                print("hardcoding bounding box")
                new_image = add_bounding_box(image_filename, annotation)
                new_image.save(TEMP_IMAGE_FILENAME, "JPEG")
                temp_filename = TEMP_IMAGE_FILENAME
                image_encoded = img_to_data(TEMP_IMAGE_FILENAME)
 
            category_id = annotation['category_id']
            category = categories[category_id]
            annotation_name = category['name']
            yield {"image": image_encoded, "label": annotation_name }

@prodigy.recipe('coco-display',
    dataset=("The dataset to use", "positional", None, str),
    annotations=("Path to a COCO format JSON annotation", "positional", None, str),
    source=("Path to a directory of images", "positional", None, str),
)
def coco_display(dataset, annotations, source):
    """
    Stream images from directory and apply first label among the ones in input 
    """

    stream = process_coco_json(annotations, source)
    return {
        'dataset': dataset,        # Name of dataset to save annotations
        'stream': stream,          # Incoming stream of examples
        'view_id': 'classification'
    }

# Example usage (works in prodigy 1.8.5): 
# prodigy coco-display your-dataset-name coco-annotations.json coco-images/ -F coco_display.py