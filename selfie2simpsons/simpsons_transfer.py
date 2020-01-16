from networks import ResnetGenerator as RG
from utils import *
import torch
import cv2
import argparse
import os
from torchvision import transforms
from PIL import Image

def simpsons_transfer(content_imgs, content_paths):
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    genA2B = RG(input_nc=3, output_nc=3, ngf=64, n_blocks=4, img_size=256, light=True).to(device)

    genA2B.eval()

    params = torch.load('./results_default/people2simpson/model/people2simpson_params_0143000.pt')
    genA2B.load_state_dict(params['genA2B'])

    output_imgs = []
    i = 0
    for content, content_path in zip(content_imgs, content_paths):
        imgname = content_path.split('/')[-1].split('.')[0]
        print(imgname)
        content = content.to(device).unsqueeze(0)
        print(content.size())
        with torch.no_grad():
            fake_A2B, _, fake_A2B_heatmap = genA2B(content)

        output = RGB2BGR(tensor2numpy(denorm(fake_A2B[0]))) * 255.0
        output_imgs.append(output)
        i += 1
        outdir = './' + imgname + '.png'
        print(outdir)
        cv2.imwrite(outdir,output)

def test_transform():
    transform_list = []
#     transform_list.append(transforms.Resize(512))
#     transform_list.append(transforms.CenterCrop(512))
    transform_list.append(transforms.ToTensor())
    transform = transforms.Compose(transform_list)
    return transform

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--content_dir', type=str, default='./dataset/people2simpson/testA', help='Directory path to a batch of content images')
    
    args = parser.parse_args()

    content_tf = test_transform()

    content_paths = [os.path.join(args.content_dir, f) for f in os.listdir(args.content_dir)]
    
    content_imgs = torch.stack([content_tf(Image.open(p)) for p in content_paths])
    
    output_imgs = simpsons_transfer(content_imgs, content_paths)