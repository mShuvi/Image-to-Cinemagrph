# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 12:18:01 2018

@author: maaya
"""

import torch
import torchvision.transforms as transforms
from PIL import Image
import matplotlib.pyplot as plt

from basic_utils import *
from field_functions import *
from frames_functions import *
from options import Options


opt = Options().parse()

#Project Parameters
project_name = opt.project_name
img_path = opt.img_path
in_path = opt.work_dir
binary_map_path = opt.binary_map_path

updatebinarymap = opt.updatebinarymap
N=opt.nSegments

warping_field_alpha = opt.warping_field_alpha
th = opt.th # binary map threshold
alpha_exp = opt.alpha_exp
section_size = int(1e3)
H= opt.H
W= opt.W


#Create prpject's dirs
frames_dir, videos_dir, mixedframes_dir, mixed_frames_video_dir, project_dir = create_project_folders(in_path, project_name, N,use_binarymap=False)

#Load input image
input_img_orig = Image.open(img_path).convert('RGB')
trans = transforms.Scale((H,W))
input_img_orig = trans(input_img_orig)

#transform input image to tensor
img_tensor = preprocess_img(input_img_orig)
img_xsize = img_tensor.size(2)
img_ysize = img_tensor.size(3)

#Load binary map and update
binary_map = Image.open(binary_map_path).convert('RGB')
binary_map = trans(binary_map)
binary_map_tensor = preprocess_img(binary_map)[:,0:1,:,:].gt(th)

if updatebinarymap:
    binary_map_tensor = update_binary_map(binary_map_tensor)
    
#Create identity map with correspondig size
identitymap = identity_map((1, 2, img_xsize, img_ysize))


print("--------------\nImport strokes of motion")
txt_file = opt.storkes_txt_path
p_list, q_list = read_points_from_txt(txt_file, H, W)

print("start points: p_list\n ", p_list)
print("end points: q_list\n ", q_list)
#Generate warpinf field
print("--------------\nGenerating warp field")  
warping_field, dist_map = warping_field_generator(identitymap, q_list, p_list, img_xsize, img_ysize, warping_field_alpha, binary_map_tensor, section_size)
#Save plot of warping field
save_plot_grid(project_name, project_dir, warping_field, opt.plot_step)


warpped_img_tensor = img_warping(img_tensor, warping_field, identitymap)
warpped_img = postprocess_img(warpped_img_tensor)

#plt.imshow(warpped_img)
#plt.imsave("warpped.png",warpped_img)

#make initial video
print("--------------\nGenerating frames") 
frames_list = generate_deformed_frames(img_tensor, warping_field, identitymap, N, frames_dir)

if not opt.no_original_vid:
    make_video(frames_dir, videos_dir, N, name="warping_vid",fps=opt.fps)

#make halluciated video
print("Generating looped video\n") 
mixed_frames_list = generate_mixed_frames(frames_list, mixedframes_dir, N, alpha_exp)
make_looped_video(mixedframes_dir, mixed_frames_video_dir, N, 4, name="looped_video",fps=opt.fps)
