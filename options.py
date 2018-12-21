# -*- coding: utf-8 -*-
"""
Created on Fri Dec 21 01:52:51 2018

@author: maaya
"""

import argparse
import torch



class Options():
    def __init__(self):
        self.initialized = False
 
    def initialize(self, parser):
        
        #paths
        parser.add_argument('--img_path',type=str, default="sandstorm.png", help='path to input image')
        parser.add_argument('--work_dir', type=str, default="./", help='path the dir which will include the project dir')
        parser.add_argument('--binary_map_path', type=str, default='binarymaps/sandstorm_bin.png', help='path binary map of the input image')        
        parser.add_argument('--storkes_txt_path', type=str, default='strokes.txt', help='path to txt which include strokes om motion')
        parser.add_argument('--project_name', type=str, default="sandstorm_animation", help='name of project')
        
        parser.add_argument('--updatebinarymap', action='store_false', help='if specified, add edges to binary map in field calculation')        
        parser.add_argument('--H', type=int, default=153, help='scale input image to this height')
        parser.add_argument('--W', type=int, default=360, help='scale input image to this width')
        
        parser.add_argument('--warping_field_alpha', type=float, default=0.5, help='controls the interpolation in field generation')
        parser.add_argument('--th', type=int, default=0.5, help='Binarymap threshold for input binarymap (RGB to binary image)')                            
        parser.add_argument('--alpha_exp', type=float, default=0.001, help='value of hallucination coefficients')                            
        parser.add_argument('--no_original_vid', action='store_true', help='if specified, dont create a video of frames without hallucination')    

        parser.add_argument('--nSegments', type=int, default=20, help='number of frames in output video')
        parser.add_argument('--fps', type=int, default=15, help='frames per sec. of output video')
        parser.add_argument('--plot_step', type=int, default=5, help='number of steps between field plot samples')

        return parser

    def gather_options(self):
        # initialize parser with basic options
        if not self.initialized:
            parser = argparse.ArgumentParser(
                formatter_class=argparse.ArgumentDefaultsHelpFormatter)
            parser = self.initialize(parser)

        # get the basic options
        opt, _ = parser.parse_known_args()
        # modify dataset-related parser options
        self.parser = parser
        return parser.parse_args()

    def print_options(self, opt):
        message = ''
        message += '----------------- Options ---------------\n'
        for k, v in sorted(vars(opt).items()):
            comment = ''
            default = self.parser.get_default(k)
            if v != default:
                comment = '\t[default: %s]' % str(default)
            message += '{:>25}: {:<30}{}\n'.format(str(k), str(v), comment)
        message += '----------------- End -------------------'
        print(message)
        return


    def parse(self):

        opt = self.gather_options()
        # process opt.suffix        
        self.print_options(opt)

        self.opt = opt
        return self.opt