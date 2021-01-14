# Convert Cityperson Json Annotations to PASCAL VOC Format

### requirement
* python3.6
* numpy
* xml
* json

### How to Run
* target：Convert Cityperson Json Annotations to PASCAL VOC Format
* step 1：Copy all the Json Annotation file into one directory. (train/val)
```
/home/cym/CYM/dataset/citypersons/Annotations_json/train/
/home/cym/CYM/dataset/citypersons/Annotations_json/val/
```
* step 2：Convert json annotations to voc's xml format by **run citypersons2voc.py**
```
python citypersons2voc.py --input_dir /home/cym/CYM/dataset/citypersons/Annotations_json/train/ --output_dir /home/cym/CYM/dataset/citypersons/VOC_citypersons/Annotations_mode4/ --dataset train --mode mode4
```
```
python citypersons2voc.py --input_dir /home/cym/CYM/dataset/citypersons/Annotations_json/val/ --output_dir /home/cym/CYM/dataset/citypersons/VOC_citypersons/Annotations_mode4/ --dataset val --mode mode4
```
> > * input_dir: the path saved the json annotations file.
> > * dataset: train/test corresponds to train/val folder of step 1. train-->train.txt  test-->test.txt
> > * output_dir: saving the xml file into output_dir.
> > * mode: represents different ways of defining pedestrian. See **citypersons.py** for a detailed definition.
* step 3: Copy all the image file into **VOCcitypersons/JPEGImages** folder. 
```
python create_JPEGImages_of_voc.py
```


#### reference:
[1] dongdonghy/citypersons2voc(https://github.com/dongdonghy/citypersons2voc)





