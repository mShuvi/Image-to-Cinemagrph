# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 01:52:51 2018

@author: maaya
"""

import argparse
import torch
import os


class Options():
    def __init__(self):
        self.initialized = False
        self.parser = argparse.ArgumentParser()
 
    def initialize(self):
        
        #paths
        self.parser.add_argument('--img_path',type=str, default="sandstorm.png", help='path to input image')
        self.parser.add_argument('--work_dir', type=str, default="./", help='path the dir which will include the project dir')
        self.parser.add_argument('--binary_map_path', type=str, default='binarymaps/sandstorm_bin.png', help='path binary map of the input image')        
        self.parser.add_argument('--storkes_txt_path', type=str, default='strokes.txt', help='path to txt which include strokes om motion')
        self.parser.add_argument('--project_name', type=str, default="sandstorm_animation", help='name of project')
        
        self.parser.add_argument('--updatebinarymap', action='store_true', help='if specified, add static edges to binary map in field calculation')        
        self.parser.add_argument('--H', type=int, default=153, help='scale input image to this height')
        self.parser.add_argument('--W', type=int, default=360, help='scale input image to this width')
        
        self.parser.add_argument('--warping_field_alpha', type=float, default=0.5, help='controls the interpolation in field generation')
        self.parser.add_argument('--th', type=int, default=0.5, help='Binarymap threshold for input binarymap (RGB to binary image)')                            
        self.parser.add_argument('--alpha_exp', type=float, default=0.001, help='value of hallucination coefficients')                            
        self.parser.add_argument('--no_original_vid', action='store_true', help='if specified, dont create a video of frames without hallucination')    

        self.parser.add_argument('--nSegments', type=int, default=20, help='number of frames in output video')
        self.parser.add_argument('--fps', type=int, default=15, help='frames per sec. of output video')
        self.parser.add_argument('--plot_step', type=int, default=5, help='number of steps between field plot samples')
        self.initialized = True

    def parse(self):
        if not self.initialized:
            self.initialize()
        self.opt = self.parser.parse_args()


        args = vars(self.opt)

        print('------------ Options -------------')
        for k, v in sorted(args.items()):
            print('%s: %s' % (str(k), str(v)))
        print('-------------- End ----------------')

        # save to the disk
        expr_dir = os.path.join(self.opt.work_dir, self.opt.project_name)
        if not os.path.exists(expr_dir):
            os.makedirs(expr_dir)
        file_name = os.path.join(expr_dir, 'opt.txt')
        with open(file_name, 'wt') as opt_file:
            opt_file.write('------------ Options -------------\n')
            for k, v in sorted(args.items()):
                opt_file.write('%s: %s\n' % (str(k), str(v)))
            opt_file.write('-------------- End ----------------\n')
        return self.opt