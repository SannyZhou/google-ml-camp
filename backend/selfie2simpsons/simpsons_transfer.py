from networks import ResnetGenerator as RG
from utils import *
import torch
import cv2
import argparse
import os
from torchvision import transforms
from PIL import Image

def simpsons_transfer(content_imgs):
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    genA2B = RG(input_nc=3, output_nc=3, ngf=64, n_blocks=4, img_size=256, light=True).to(device)

    genA2B.eval()

    params = torch.load('./results_default/people2simpson/model/people2simpson_params_0143000.pt')
    genA2B.load_state_dict(params['genA2B'])
    
    output_imgs = []
    i = 0
    for content in content_imgs:
        content = content.to(device).unsqueeze(0)
        print(content.size())
        with torch.no_grad():
            fake_A2B, _, fake_A2B_heatmap = genA2B(content)

        output = RGB2BGR(tensor2numpy(denorm(fake_A2B[0]))) * 255.0
        output_imgs.append(output)
        i += 1
        outdir = './' + str(i) + '.png'
        cv2.imwrite(outdir,output)
    return output_imgs