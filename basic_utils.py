# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 08:30:32 2018

@author: maaya
"""

import torch
import math
import torchvision.transforms as transforms
import numpy as np
import os
import imageio
import pathlib
import matplotlib.pyplot as plt


# Read vectors from txt
def read_points_from_txt(txt_file, H, W):
    # strokes of motion are defined from p to q in motion field
    # in txt file should be written as : p1_x, p1_y, q1_x, q1_y
    # The values p1_x, p1_y, q1_x, q1_y should be < 1, such that:
    # p1_x_final = p1_x * H
    p_lst = []
    q_lst = []
    
    with open(txt_file) as points_file:
        line = points_file.readline()
        cnt = 1
        while line:
            point = line.strip().split(',')
            p_cur = torch.tensor([int(float(point[0])*H), int(float(point[1])*W)])
            q_cur = torch.tensor([int(float(point[2])*H), int(float(point[3])*W)])
            p_lst.append(p_cur)
            q_lst.append(q_cur)
            line = points_file.readline()
            cnt += 1
            
    return p_lst, q_lst



# MAPS
def identity_map(size):
    idnty_map = torch.Tensor(size[0],2,size[2],size[3])
    idnty_map[0,0,:,:].copy_(torch.arange(0,size[2]).repeat(size[3],1).transpose(0,1))
    idnty_map[0,1,:,:].copy_(torch.arange(0,size[3]).repeat(size[2],1))
    
    return idnty_map


def update_binary_map(binary_map, anchor_list=[]): #binary map : [1,1,H,W] , anchor_lst = list of tensor size2
    H = binary_map.size(2)
    W = binary_map.size(3)

    if len(anchor_list)>0:
        for item in anchor_list:
            binary_map[:,:,item[0],item[1]] = 0

    # Add edges:
    binary_map[:,:,0,:] = 0
    binary_map[:,:,H - 1,:] = 0

    binary_map[:,:,:,0] = 0
    binary_map[:,:,:,W - 1] = 0

    return binary_map


# FOLDERS
def create_project_folders(in_path, project_name, N,use_binarymap=False):

    project_dir = os.path.join(in_path, project_name)
    print(project_dir)
    pathlib.Path(project_dir).mkdir(parents=True, exist_ok=True)

    if use_binarymap:
        frames_path = 'wbinarymap_frames_' + str(N)
    else:
        frames_path = 'frames_{0}'.format(N)

    frames_dir = os.path.join(project_dir, frames_path)
    pathlib.Path(frames_dir).mkdir(parents=True, exist_ok=True)

    videos_dir = os.path.join(frames_dir, "Videos")
    pathlib.Path(videos_dir).mkdir(parents=True, exist_ok=True)

    mixedframes_dir = os.path.join(project_dir, "Mixed_frames_" + str(N))
    pathlib.Path(mixedframes_dir).mkdir(parents=True, exist_ok=True)

    mixed_frames_video_dir = os.path.join(mixedframes_dir, "Videos")
    pathlib.Path(mixed_frames_video_dir).mkdir(parents=True, exist_ok=True)


    return  frames_dir, videos_dir, mixedframes_dir, mixed_frames_video_dir, project_dir


# PLOT
def plot_grid(field, step, plot_path, plot_image_ratio = 0.2):
#    field (1,2,H,W)
    print(field.size())
#    field = -1 * field
    n_x = field.size(2) # related to W
    n_y = field.size(3) # related to H
    
    print("plot size: (%d, %d) " % (n_y, n_x))
    
    X, Y = np.mgrid[0:n_x:step ,0:n_y:step]

    V = field[:,1,0:n_x:step,0:n_y:step].squeeze(0).numpy()
    U = field[:,0,0:n_x:step,0:n_y:step].squeeze(0).numpy()
    C = (V**2 + U**2)**(0.5)

    fig, fieldplot = plt.subplots(1, 1, figsize=(n_x * plot_image_ratio, n_y * plot_image_ratio))

    fieldplot.quiver(X, Y, U, V, C, edgecolor='k',linewidth=.5)

    fig.savefig(plot_path)
    return


def save_plot_grid(project_name, project_dir, warping_field, plot_step):
    plot_name = project_name + "_plot.png"
    plot_path = os.path.join(project_dir, plot_name)
    plot_grid(warping_field, plot_step, plot_path)


# COEFFICIANTS FUNCTION
def mu_function_exp(n, N, alpha):
    n = n % (2 * N + 1)
    exponent_func = math.exp(-1 * alpha * ((n-N) ** 2))
    beta = math.exp(-1 * alpha *(N ** 2))
    output = exponent_func - beta

    if output < 0 :
        output = 0
    return output


def plot_function(N, alpha):
    y_list = []

    for i in range(-N, N + 1):

        y = mu_function_exp(i, N, alpha)
        y_list.append(y)

    x_list = np.linspace(-N, N, 2*N + 1)
    plt.plot(x_list , y_list)
    plt.ylabel('exp function')
    print(y_list)
    plt.show()
 
    
# IMGS    
def preprocess_img(img):  # input PILimg ,output processed img
    tranformer = transforms.ToTensor()
    final_img = tranformer(img).unsqueeze(0)
#    print(final_img.size())
#    final_img = torch.transpose(final_img , 2 , 3)
    return final_img


def postprocess_img(image_tensor, imtype=np.uint8, index=0):
    image_numpy = image_tensor[index].cpu().float().numpy()
    image_numpy = np.transpose(image_numpy, (1, 2, 0))
    if image_numpy.shape[2] == 1:
        image_numpy = np.tile(image_numpy, [1,1,3])

    return image_numpy


def save_image_to_dir(img_tensor, file_path, i):
    img = postprocess_img(img_tensor)
    img_path = os.path.join(file_path, "frame_{0}.png".format(i))
    plt.imsave(img_path, img)
    if i%10 == 0:
        print("Img #%d  was saved!" % (i))
    return


#VIDEO
def make_video(folder_in, folder_out, N, name="warping_vid",fps=15):
    print("*** make_video *** \n")
    writer = imageio.get_writer(os.path.join(folder_out, name+'.mp4'), fps=fps)

    for i in range(2 * N + 1):
        image = imageio.imread(os.path.join(folder_in, "frame_{0}.png".format(i)))
        writer.append_data(image)

    writer.close()
    print("Video " + name + " was saved!")
    return


def make_looped_video(folder_in, folder_out, N, loops_num,name="looped_video",fps=15):
    print("*** make_video *** \n")
    writer = imageio.get_writer(os.path.join(folder_out, name+'.mp4'), fps=fps)

    for i in range(loops_num):
        for i in range(2 * N + 1):
            image = imageio.imread(os.path.join(folder_in, "frame_{0}.png".format(i)))
            writer.append_data(image)

    writer.close()
    print("Video " + name + " was saved!")
    return