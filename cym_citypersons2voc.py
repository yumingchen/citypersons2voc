import pdb
import os
import json
import argparse
from lxml.etree import Element, SubElement, tostring, ElementTree
from xml.dom.minidom import parseString

def get_parser():
    parser = argparse.ArgumentParser(description='manual to this script')                            
    parser.add_argument('--input_dir', type=str, default = 'training_labels')                     
    parser.add_argument('--output_dir', type=str, default = 'Annotations')
    parser.add_argument('--mode', type=str, default = 'mode1', 
                        help = 'mode1 mode2 or mode3: diffirent defination about pedestrian')
    parser.add_argument('--dataset', type=str, default='train', help='train or test')
    args = parser.parse_args()
    return args

def main():
    
    args = get_parser()
    
    # args.input_dir: the path saved the json annotations file.
    # eg. /home/cym/CYM/dataset/citypersons/Annotations_json/train/
    input_files = sorted(os.listdir(args.input_dir))
    print('numbers of images:  ' + str(len(input_files)))

    #the total number of pedestrian labels
    num_ped=0
    #the total number of ignore labels
    num_ignore=0
    #the max number of labels in single image
    max_num=0
    #the numer of images with zero labels
    num_zero=0
    #the min width of pedestrian labels
    min_width=float('inf')
    #the min height of pedestrian labels
    min_height=float('inf')
    #the max width of pedestrian labels
    max_width=0
    #the max height of pedetrian labels
    max_height=0
    #the mean ratio of pdestrian labels
    mean_ratio=0
    #the number of heavy occlusion pedestrian cases(occ>0.35)
    num_truncated=0
    #the number of small pedestrian cases(30<height<80)
    num_small=0
    # the number of heavy and small
    num_t_and_s=0
    #the max ratio of pedestrian labels
    max_ratio=0
    #the min ratio of pedestrian labels
    min_ratio=float('inf')

    ############################################CYM################################################
    img_list = []
    classes = ['pedestrian', 'rider', 'ignore', 'sitting person', 'person (other)', 'person group']
    ############################################CYM################################################

    for json_name in input_files:

        img_list.append(json_name[:-22]+'leftImg8bit\n')

        json_file=os.path.join(args.input_dir, json_name)
        with open(json_file, 'r') as f:
            data=json.load(f)

        # build the xml structure
        file_name=json_name[:-22]+'leftImg8bit.png'
        node_root = Element('annotation')
        node_folder = SubElement(node_root, 'folder')
        node_folder.text = 'VOC2007'
        node_filename = SubElement(node_root, 'filename')
        node_filename.text = file_name
        node_size = SubElement(node_root, 'size')  
        node_width = SubElement(node_size, 'width')  
        node_width.text = str(data['imgWidth'])   
        node_height = SubElement(node_size, 'height')  
        node_height.text = str(data['imgHeight'])  
        node_depth = SubElement(node_size, 'depth')  
        node_depth.text = '3'
        
        img_width = int(node_width.text)
        img_height = int(node_height.text)
        
        if len(data['objects'])==0:
            num_zero+=1
        if len(data['objects'])>max_num:
            max_num=len(data['objects'])

        for j in range(len(data['objects'])):

            node_object = SubElement(node_root, 'object')    
            node_name = SubElement(node_object, 'name')  
            
            if data['objects'][j]['label'] not in classes:
                classes.append(data['objects'][j]['label'])

            if args.mode == 'mode1':
                if data['objects'][j]['label']=='pedestrian':                
                    node_name.text = 'ped'                                   
                    num_ped+=1                                               
                else:                                                        
                    node_name.text = 'ignore'                                
                    num_ignore+=1
            elif args.mode == 'mode2':
                if data['objects'][j]['label'] in ['pedestrian', 'rider', 'sitting person', 'person (other)']:
                    node_name.text = 'ped'
                    num_ped+=1
                else:
                    node_name.text = 'ignore'        
                    num_ignore+=1
            elif args.mode == 'mode3':
                node_name.text = data['objects'][j]['label']
            elif args.mode == 'mode4':
                if data['objects'][j]['label'] in ['pedestrian', 'rider']:
                    node_name.text = 'ped'
                    num_ped+=1
                else:
                    node_name.text = 'ignore'        
                    num_ignore+=1

            node_difficult = SubElement(node_object, 'pose')
            node_difficult.text = 'Unspecified'
            
            # difficult = area_bboxVis / area_bbox
            difficult = (float(data['objects'][j]['bboxVis'][2])*float(data['objects'][j]['bboxVis'][3]))/(float(data['objects'][j]['bbox'][2])*float(data['objects'][j]['bbox'][3]))
            node_difficult = SubElement(node_object, 'truncated')
            node_difficult.text = str(difficult)
          
            node_difficult = SubElement(node_object, 'difficult')
            node_difficult.text = str(difficult)

            if difficult<0.65 and data['objects'][j]['label']=='pedestrian':
                num_truncated+=1
                if float(data['objects'][j]['bbox'][3])<50:
                    num_t_and_s+=1
            if float(data['objects'][j]['bbox'][3])<50 and data['objects'][j]['label']=='pedestrian':
                num_small+=1   


            node_bndbox = SubElement(node_object, 'bndbox')  
            node_xmin = SubElement(node_bndbox, 'xmin')  
            node_xmin.text = str(float(data['objects'][j]['bbox'][0]))  
            node_ymin = SubElement(node_bndbox, 'ymin')  
            node_ymin.text = str(float(data['objects'][j]['bbox'][1]))
            node_xmax = SubElement(node_bndbox, 'xmax')  
            node_xmax.text = str(float(data['objects'][j]['bbox'][0])+float(data['objects'][j]['bbox'][2])-1)
            node_ymax = SubElement(node_bndbox, 'ymax')  
            node_ymax.text = str(float(data['objects'][j]['bbox'][1])+float(data['objects'][j]['bbox'][3])-1)

            # Prevent the bbox from overflowing the image boundary
            if float(node_ymax.text)>=img_height:
                node_ymax.text = '1023'
            if float(node_xmax.text)>=img_width:
                node_xmax.text = '2047'
            if float(node_ymin.text)<0: 
                node_ymin.text = '0'
            if float(node_xmin.text)<0:
                node_xmin.text = '0'
            if float(node_ymax.text)>=img_height or float(node_xmax.text)>=img_width or float(node_ymin.text)<0 or float(node_xmin.text)<0:
                print(data['objects'][j]['bbox'])
                print(json_name, j)
                raise ValueError('out of bounds of images')
            if float(node_ymax.text) < float(node_ymin.text) or float(node_xmax.text) < float(node_xmin.text):
                print(data['objects'][j]['bbox'])
                print(json_name, j)
                raise ValueError('The bounding box is not rectangle!')

            if float(data['objects'][j]['bbox'][2])<min_width and data['objects'][j]['label']=='pedestrian':
                min_width=float(data['objects'][j]['bbox'][2])
            if float(data['objects'][j]['bbox'][3])<min_height and data['objects'][j]['label']=='pedestrian':
                min_height=float(data['objects'][j]['bbox'][3])
            if float(data['objects'][j]['bbox'][2])>max_width and data['objects'][j]['label']=='pedestrian':
                max_width=float(data['objects'][j]['bbox'][2])
            if float(data['objects'][j]['bbox'][3])>max_height and data['objects'][j]['label']=='pedestrian':
                max_height=float(data['objects'][j]['bbox'][3])
            if data['objects'][j]['label']=='pedestrian':
                mean_ratio+=(float(data['objects'][j]['bbox'][2]))/float(data['objects'][j]['bbox'][3])
            if data['objects'][j]['label']=='pedestrian':
                max_ratio=max(float(data['objects'][j]['bbox'][2])/float(data['objects'][j]['bbox'][3]), max_ratio)
                min_ratio=min(float(data['objects'][j]['bbox'][2])/float(data['objects'][j]['bbox'][3]), min_ratio)

        xml_dir=args.output_dir
        if not os.path.exists(xml_dir):
            os.makedirs(xml_dir)
        xml_file = os.path.join(xml_dir, json_name[:-22]+'leftImg8bit.xml')
        xml = tostring(node_root, pretty_print=True) 
        dom = parseString(xml)  
        ElementTree(node_root).write(xml_file, pretty_print=True)

    print('number of ped:  ' + str(num_ped))
    print('number of ignore:  ' + str(num_ignore))
    print('number of images with 0 labels :  ' + str(num_zero))
    print('max number of labels in single images:  ' + str(max_num))
    print('number of heavy:  ' + str(num_truncated))
    print('number of small:  ' + str(num_small))
    print('number of heavy and small:  ' + str(num_t_and_s))
    print('min width of ped:   ' + str(min_width))
    print('min height of ped:  ' + str(min_height))
    print('max width of ped:   ' + str(max_width))
    print('max height of ped:  ' + str(max_height))
    print('mean ratio pf ped:  ' + str(mean_ratio/num_ped))
    print('max ratio of ped:  ' + str(max_ratio))
    print('min ratio of ped:  ' + str(min_ratio))

    ###########################CYM#################################
    with open(os.path.join(args.dataset+'.txt'), 'w') as f:
        f.writelines(img_list)

    print(classes)
    ###########################CYM#################################
    
    
if __name__ == '__main__':
    main()
    
# python cym_citypersons2voc.py --input_dir /home/cym/CYM/dataset/citypersons/Annotations_json/train/ --output_dir /home/cym/CYM/dataset/citypersons/VOC_citypersons/Annotations_mode4/ --dataset train --mode mode4

# python cym_citypersons2voc.py --input_dir /home/cym/CYM/dataset/citypersons/Annotations_json/val/ --output_dir /home/cym/CYM/dataset/citypersons/VOC_citypersons/Annotations_mode4/ --dataset val --mode mode4