# Prodi.gy recipes

##  <kbd>recipe</kbd> `coco-display`: show &review each object of a COCO dataset

![coco-display UI image](images/coco-display-tiny.png?raw=true)

each annoteded bounding box is hardcoded on the image and shown 
alongside the name of the category

can be used to quickly review your COCO dataset for correctness.

### Usage
example: `prodigy coco-display your-dataset-name coco-annotations.json coco-images/ -F coco_display.py`


# TODO
* create a `image_manual` stream with coco and the correct ui for reworking / adding bboxes
