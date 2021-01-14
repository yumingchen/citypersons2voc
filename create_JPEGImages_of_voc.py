import glob
import os
import shutil
root = '/home/cym/CYM/dataset/citypersons/'
'''
create VOC
move resource images to JPEGImages
'''
def move_img_to_JPEGIMages(dataset='train'):
    root_path = os.path.join(root, 'leftImg8bit', dataset)
    target_dir = os.listdir(root_path)
    img_list = []
    for line in target_dir:
        img_path = os.path.join(root_path, line,'*.png')
        imgs = glob.glob(img_path)
        img_list.extend(imgs)
    print(len(img_list))
    save_path = os.path.join(root, 'VOC_citypersons/JPEGImages/')
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    for line in img_list:
        name = line.split('/')[-1]
        target_path = os.path.join(save_path, name)   
        shutil.copyfile(line, target_path)
    return img_list
img_list = move_img_to_JPEGIMages(dataset = 'train')
img_list = move_img_to_JPEGIMages(dataset = 'val')