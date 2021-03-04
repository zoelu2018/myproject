import os
import tifffile as tiff
import cv2
import numpy.ma as npm

def pre(path):
    for root, dirs, files in os.walk(path):
        for name in files:
            if '_pre.tif' in name:
                # basename = os.path.basename(name)
                basename = os.path.splitext(name)[0]
                file__ = os.path.join(root, name)
                img = tiff.imread(file__)
                ignore_idx = img==255

                idx1 = img == 1
                idx2 = img == 2
                idx3 = img == 3
                idx4 = img == 4
                idx5 = img == 5

                img_v = img.copy()

                img_v[idx1] = 5
                img_v[idx2] = 50
                img_v[idx3] = 100
                img_v[idx4] = 150
                img_v[idx5] = 200
                mask = img_v == 255
                img_v = npm.array(img_v, mask=mask)
                
                img_v1 = cv2.blur(img_v, (3, 3))

                img_v1 = cv2.blur(img_v1, (3, 3))
                img_v1 = cv2.blur(img_v1, (3, 3))
                img_v1 = cv2.blur(img_v1, (3, 3))
                img_v1 = cv2.blur(img_v1, (3, 3))
                
                v1 = (img_v1 <5) & (img_v1 >=0)
                v2 = (img_v1 <50) & (img_v1 >=5)
                v3 = (img_v1 <100) & (img_v1 >=50)
                v4 = (img_v1 <150) & (img_v1 >=100)
                v5 = (img_v1 <200) & (img_v1 >=150)
                v6 = (img_v1 <255) & (img_v1 >=200)
                img_v1[v1] = 0
                img_v1[v2] = 1 
                img_v1[v3] = 2 
                img_v1[v4] = 3
                img_v1[v5] = 4  
                img_v1[v6] = 5 
                # plt.imshow(img_v1)
                result = tiff.imsave("D:/work/pre/test_result/"+basename+'smooth111.tif', img_v1)
                print(result)
                # print(result)
if __name__ == '__main__':
     pre("D:/work/pre/97_result")
    