# -*- coding: utf-8 -*-
"""
Created on Fri Sep 28 08:43:48 2018

@author: maaya
"""

import torch
import torch.nn.functional as func

from basic_utils import save_image_to_dir, mu_function_exp


def normalize_field_for_warping(field, identitymap, sum_with_original = True):
    field = -field
    if sum_with_original:
        normalized_field = field + identitymap
    else:
        normalized_field = field

    x_size = normalized_field.size(2) - 1
    y_size = normalized_field.size(3) - 1

    normalized_field[:,0,:,:] = normalized_field[:,0,:,:] / x_size
    normalized_field[:,1,:,:] = normalized_field[:,1,:,:] / y_size

    normalized_field[:,0,:,:] = normalized_field[:,0,:,:] - 0.5
    normalized_field[:,1,:,:] = normalized_field[:,1,:,:] - 0.5

    normalized_field[:,0,:,:] = normalized_field[:,0,:,:] * 2
    normalized_field[:,1,:,:] = normalized_field[:,1,:,:] * 2

    return normalized_field


def img_warping(img_tensor, warping_field, identitymap):
    normalized_grid = normalize_field_for_warping(warping_field, identitymap)
    normalized_grid = torch.transpose(normalized_grid , 1 , 3).float()
    img_tensor = torch.transpose(img_tensor , 2 , 3).float()

    output = func.grid_sample(img_tensor, normalized_grid, padding_mode='border')
    output =  torch.transpose(output, 2, 3)

    return output


def quantize_field(field, N, i): # N=number of segments
    step = ( i / N )
    field = field * step
    return field


def generate_deformed_frames(img_tensor, unnormalized_field, identitymap, N, file_path):
    frames_lst = []
    for i in range(-N, N + 1):
        quant_field = quantize_field(unnormalized_field, N, i)
        deformed_img = img_warping(img_tensor, quant_field, identitymap)
        save_image_to_dir(deformed_img, file_path, i+N)
        frames_lst.append(deformed_img)

    return frames_lst


def generate_mixed_frame(current_frame, transperant_frame , n, N, alpha, mu_function='exp'):
    if mu_function == "exp":
        cur_frame_coefficient = mu_function_exp(n, N, alpha)
        transperant_frame_coefficient = mu_function_exp((n + (N + 1)), N, alpha)
        mu_tot = cur_frame_coefficient + transperant_frame_coefficient

    mixed_frame = (cur_frame_coefficient / mu_tot) * current_frame + (transperant_frame_coefficient / mu_tot) * transperant_frame
    return mixed_frame


def generate_mixed_frames(frames_list, mixedframes_path, N, alpha, mu_function='exp'):
    mixed_frames = []
    seq_length = 2 * N + 1

    for n in range(-N, N+1):
        current_frame = frames_list[(n + N)]
        next_frame = frames_list[((n + N) + (N + 1)) % seq_length]
#        print("({0} , {1})".format((n + N) , ((n + N) + (N + 1)) % seq_length ))
        mixed_frame = generate_mixed_frame(current_frame, next_frame , n+N , N, alpha)
        save_image_to_dir(mixed_frame, mixedframes_path, n + N)
        mixed_frames.append(mixed_frame)
    return mixed_frames
