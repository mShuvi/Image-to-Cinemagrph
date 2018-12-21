# Image-to-Cinemagrph
The goal of this work is to generate a Cinemagraph, a short animation which contains natural subtle motion, out of your input RGB image. This repository is still under active development.

The code was written by [Ma'ayan Shuvi](https://mShuvi.github.io/) under the supervision of [Kfir Aberman](https://kfiraberman.github.io/).

- Given input image and its binary map:<br />
    <img src="./imgs/sandstorm.png" width="400"/> <img src="./imgs/sandstorm_bin.png" width="400" />



- The output video:<br />
    <p align="center">
      <img src=imgs/sandstorm_vidtogif.gif width="400"/>
    </p>
       
- The original output filel is in .mp4 format, can be found [here](https://github.com/mShuvi/Image-to-Cinemagrph/blob/master/imgs/looped_video.mp4).       

## Prerequisites
- Python 2 or 3


### Run Demo
- Run the algorithm (demo example) in order to get Sandstorm animation
```bash
#!./script.sh
python3 main.py
```    


### Run on your own Image
- Binary map: '1' - defines the motion region and '0' defines the static region. (tip: can be created even with Paint)
- Strokes: A txt file, where each line represents the start and end points of one strokes. Example: start_x, start_y, end_x, end_y Attention: in images x - top to bottom, y - left to right.
- You can edit more of the parameters in the configuration file in PATH.

```bash
#!./script.sh
python3 main.py --project_name XXX --img_path PPP --work_dir YYY --binary_map_path ZZZ --storkes_txt_path SSS
```  


### Examples:
- Tower exmple, its input image and binary map is attached. You can create you own motion strokes and animate the image!<br />
    <p align="center">
      <img src=examples/ezgif-2-3b462a632393.gif width="400"/>
    </p>
    
- Water motion, we tried to imitate a motion of a given video, given its first frame only. (right: original, left: our animation)<br />
    <p align="center">
      <img src=examples/ezgif-2-27d9578b6a3c.gif width="500"/>
    </p>
