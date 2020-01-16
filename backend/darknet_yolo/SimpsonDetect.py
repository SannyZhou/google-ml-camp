# Stupid python path shit.
# Instead just add darknet.py to somewhere in your python path
# OK actually that might not be a great idea, idk, work in progress
# Use at your own risk. or don't, i don't care

import sys, os
sys.path.append(os.path.join(os.getcwd(),'python/'))

import darknet as dn
import pdb
import cv2

dn.set_gpu(0)
net = dn.load_net(b"simpsons_test.cfg", b"../../dataset/New_Simpsons/checkpoint/simpsons_5000.weights", 0)
meta = dn.load_meta(b"simpsons.data")
#The result directory of the style transfer process
input_path = '/home/aprilpear1996/dataset/New_Simpsons/test/stylish/'
#The result directory of the boxed picture
out_path = '/home/aprilpear1996/dataset/New_Simpsons/test/result/'
files = os.listdir(input_path)

#res in the r is the detection result of the model
#the classname is the only required result of our application 

with open(out_path + "result.txt",'w') as fwrite:

    for imgfile in files:
        imgfilename = imgfile[:-4]
        imgfilepath = input_path+imgfile
        outpath = out_path + imgfile
        r = dn.detect(net, meta, imgfilepath.encode('utf-8'))
        print (r)
        img = cv2.imread(imgfilepath)

        for res in r:
            classname,score,bbox = res
            classname = classname.decode()

            # x,y,w,h = bbox
            # cv2.rectangle(img,(int(x-w/2),int(y-h/2)),(int(x+w/2),int(y+h/2)),(18,127,15),thickness=2)
            # font = cv2.FONT_HERSHEY_SIMPLEX
            # txt = classname + " " + (str(score))[:5]
            # cv2.putText(img, txt, (int(x-w/2+5),int(y-h/2+5)), font, 0.6, (255,255,255), lineType=cv2.LINE_AA)
            # cv2.imwrite(outpath,img)
            # newline = "current picname is: " + imgfilename + ", he/she is " + classname + '/n'
            # fwrite.write(newline)
        
    


