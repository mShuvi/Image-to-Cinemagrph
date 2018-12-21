# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 08:39:14 2018

@author: maaya
"""

import torch
import math


def calculate_iteration_mindist(Px, Py, reshaped_Sx, reshaped_Sy, start_ind, end_ind, W, H):    
    if end_ind == -1: #for iteration with length smaller than segment size 
        cur_Sx = reshaped_Sx[start_ind:reshaped_Sx.size(0)]
        cur_Sy = reshaped_Sy[start_ind:reshaped_Sy.size(0)]
    else:
        cur_Sx = reshaped_Sx[start_ind:end_ind]
        cur_Sy = reshaped_Sy[start_ind:end_ind]
    
    repeat_Sx = cur_Sx.repeat(1, 1, H , W)
    repeat_Sy = cur_Sy.repeat(1, 1, H , W)
    subx = (Px - repeat_Sx).pow(2) / H
    suby = (Py - repeat_Sy).pow(2) / W
    cur_dist = (subx  + suby).pow(0.5)
    min_dist_tensor = cur_dist.min(1)[0].unsqueeze_(0)
    
    return min_dist_tensor


def seperated_distance_from_freezepoints(binarymap, identitymap, segment_size = 5):
    infi = 1e7
    print("segment size ", segment_size)
    binarymap = binarymap.float()
    identitymap = identitymap.float()
    
    H = identitymap.size(2)
    W = identitymap.size(3)
    
    identity_x = identitymap[:,0,:,:]
    identity_y = identitymap[:,1,:,:]
    
    Sx = identity_x * (1 - binarymap) + binarymap * infi
    Sy = identity_y * (1 - binarymap) + binarymap * infi
    
    reshaped_Sx = Sx.reshape([-1,1,1])
    reshaped_Sy = Sy.reshape([-1,1,1])

    Px = identity_x.repeat(1, segment_size, 1, 1)  # maps of indices
    Py = identity_y.repeat(1, segment_size, 1, 1)
    
    i = 0
    
    dist = torch.zeros([1, 1, H, W])
    dist.fill_(1e7)
    
    num_of_iterations = math.ceil(H * W / segment_size)
    
    while(i + segment_size - 1 <= reshaped_Sx.size(0) - 1):
        print("iteration: %d / %d" % ((i / segment_size) + 1, num_of_iterations))
        
        min_dist_tensor = calculate_iteration_mindist(Px, Py, reshaped_Sx, reshaped_Sy, i, i + segment_size, W, H)      
        expanded_dist = torch.cat((dist, min_dist_tensor), 1)
        dist = expanded_dist.min(1)[0].unsqueeze_(0)

        i += segment_size

    # last iteration
    if reshaped_Sx.size(0) % segment_size != 0:
        print("one extra iteration")
        Px = identity_x.repeat(1, reshaped_Sx.size(0) % segment_size, 1, 1)
        Py = identity_y.repeat(1, reshaped_Sx.size(0) % segment_size, 1, 1)
        
        min_dist_tensor = calculate_iteration_mindist(Px, Py, reshaped_Sx, reshaped_Sy, i, -1, W, H)
        expanded_dist = torch.cat((dist, min_dist_tensor), 1)
        dist = expanded_dist.min(1)[0].unsqueeze_(0)

        dist = dist.min(1)[0].unsqueeze_(0)

    return dist


def subtract_pq(p_list, q_list):
    sub_list = []
    list_len = len(p_list)

    for i in range(list_len):
        p = p_list[i]
        q = q_list[i]
        curr = torch.Tensor([q[0]-p[0], q[1]-p[1]])
        sub_list.append(curr)

    return sub_list


def normalized_subtract_pq(p_list, q_list, size_x, size_y):
    eps = 1e-7
    factor = min(size_x, size_y) / 4
    sub_list = []
    list_len = len(p_list)

    for i in range(list_len):
        p = p_list[i]
        q = q_list[i]

        dy = (q[1]-p[1])
        dx = (q[0]-p[0])

        norm = math.sqrt( dx ** 2 + dy ** 2 ) + eps

        curr = torch.Tensor([ dx / norm, dy / norm])
        sub_list.append(curr * factor)

    return sub_list


def weight_function(p, identitymap, alpha, eps = 1e-7):
    px = p[0]
    py = p[1]

    stroke_vlaue_map = torch.zeros(identitymap.size(0), 2, identitymap.size(2), identitymap.size(3))
    stroke_vlaue_map[0,0,:,:].fill_(px)
    stroke_vlaue_map[0,1,:,:].fill_(py)

    norm = torch.zeros(identitymap.size(0), 2, identitymap.size(2), identitymap.size(3))
    norm[0,0,:,:].fill_(identitymap.size(2))
    norm[0,1,:,:].fill_(identitymap.size(3))

    dist = torch.ones(identitymap.size(0), 1,identitymap.size(2), identitymap.size(3))
#    dist.copy_(((identitymap-new_map) / (norm + eps)).pow(2).sum(1, keepdim=True).pow(0.5).mul_(-1 * alpha))
#    dist.copy_(dist.exp_())
    dist.copy_(((identitymap-stroke_vlaue_map) / (norm + eps)).pow(2).sum(1, keepdim=True).pow(0.5))
    weight = 1 / (dist + eps)

    return weight


def warping_field_generator(identitymap, q_list, p_list, img_xsize, img_ysize, alpha, binarymap_tensor, segment_size=10, beta = 0.05, eps = 1e-7):
    
    sub_lst = normalized_subtract_pq(p_list, q_list, img_xsize, img_ysize) 
    
    warping_field = torch.zeros(identitymap.size(0), 2, identitymap.size(2), identitymap.size(3))   
    tot_weight = torch.zeros(identitymap.size(0), 1, identitymap.size(2), identitymap.size(3))
    num_storkes = len(sub_lst)

    for i in range(num_storkes):
        weight = weight_function(p_list[i], identitymap, alpha)
        warping_field[0,0,:,:] += (weight[0,0,:,:]) * (sub_lst[i][0].item())
        warping_field[0,1,:,:] += (weight[0,0,:,:]) * (sub_lst[i][1].item())
        tot_weight += weight

    dist_value = seperated_distance_from_freezepoints(binarymap_tensor, identitymap, segment_size)
    tot_weight = tot_weight + 1/(beta * dist_value + eps)
    warping_field = warping_field * (1 / tot_weight )

    return warping_field, dist_value
