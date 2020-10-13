import prodigy
from prodigy.components.loaders import JSON
from prodigy.util import split_string, log

import os

from pycocotools.coco import COCO

from util import img_to_data

def transform_label(label):
    ''' downcase and underscore category names '''
    return label.upper().replace(' ', '_')

def process_coco_json(coco_dataset, image_directory):    
    categories = coco_dataset.cats
    for img_id, img in coco_dataset.imgs.items():
        image_filename =  os.path.join(image_directory, img['file_name']) 
        image_encoded = img_to_data(image_filename)

        # add all the spans (polygons)
        # for the image_manual UI view
        spans = []
        labels = []
        for annotation in coco_dataset.imgToAnns[img_id]:
            category_id = annotation['category_id']
            category = categories[category_id]
            annotation_label = category['name']
            assert(len(annotation['segmentation']) == 1)
            polygon_points = annotation['segmentation'][0]
            # turn a flat list of [x, y, x, y, ...]
            # into a list of pairs: [[x,y], [x,y], ...]
            polygon_points_pairs = [[x,y] for (x,y) in zip(polygon_points[::2], polygon_points[1::2])]
            span = {
                'label': annotation_label,
                'type': "polygon",
                'points': polygon_points_pairs
            }
            spans.append(span)

        yield {'image': image_encoded, 
            'width': img['width'], 'height': img['height'], 
            'spans': spans,
            }

@prodigy.recipe('coco-polygon',
    dataset=("The dataset to use", "positional", None, str),
    annotations=("Path to a COCO format JSON annotation", "positional", None, str),
    image_directory=("Path to a directory of images", "positional", None, str),
)
def coco_polygon(dataset, annotations, image_directory):
    """
    Stream images from directory and apply first label among the ones in input 
    """
    coco_filename = annotations
    coco_dataset = COCO(coco_filename)

    stream = process_coco_json(coco_dataset, image_directory)

    config = {
        ## XXX (mtourne): there are way too many labels possible here.
        'labels': [cat['name'] for cat in coco_dataset.cats.values()],
    }
    return {
        ### XXX labels disabled for now
        #'config': config,
        'dataset': dataset,        # Name of dataset to save annotations
        'stream': stream,          # Incoming stream of examples
        'view_id': 'image_manual',
    }

# Example usage (works in prodigy 1.8.5): 
# prodigy coco-polygon your-dataset-name coco-annotations.json coco-images/ -F coco_polygon.py