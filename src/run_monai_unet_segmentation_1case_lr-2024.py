

import numpy as np
from scipy.ndimage import zoom
import nibabel as nib

#import skimage
import matplotlib.pyplot as plt

from scipy import ndimage
#from skimage.measure import label, regionprops

import sys
import os

import torch
import monai
from monai.inferers import sliding_window_inference
from monai.networks.nets import UNet

import warnings
warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")


warnings.filterwarnings("ignore")
torch.cuda.empty_cache()

#to_tensor = ToTensor()
#to_numpy = ToNumpy()



res = int(sys.argv[1])

cl_num = int(sys.argv[2])

model_weights_path_unet = sys.argv[3]

input_img_name=sys.argv[4]

output_lab_name=sys.argv[5]


#print(" - loading image")

global_img = nib.load(input_img_name)

input_matrix_image_data = global_img.get_fdata()

input_image = torch.tensor(input_matrix_image_data).unsqueeze(0)

scaler = monai.transforms.ScaleIntensity(minv=0.0, maxv=1.0)
final_image = scaler(input_image)

flp_run = monai.transforms.Flip(1)
flipped_final_image = flp_run(final_image)


def replace_lr(fl_val_outputs):
    org_fl_val_outputs = fl_val_outputs.clone();

    i_org = 1 ; i_fl = 2 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    i_org = 2 ; i_fl = 1 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;

    i_org = 3 ; i_fl = 4 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    i_org = 4 ; i_fl = 3 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    
    i_org = 5 ; i_fl = 5 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    i_org = 6 ; i_fl = 6 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;

    i_org = 7 ; i_fl = 32 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    i_org = 32 ; i_fl = 7 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    
    i_org = 8 ; i_fl = 33 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    i_org = 33 ; i_fl = 8 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    
    i_org = 21 ; i_fl = 36 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    i_org = 36 ; i_fl = 21 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    
    i_org = 22 ; i_fl = 35 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    i_org = 35 ; i_fl = 22 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    
    i_org = 19 ; i_fl = 20 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    i_org = 20 ; i_fl = 19 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;

    i_org = 9 ; i_fl = 9 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    i_org = 10 ; i_fl = 10 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    i_org = 11 ; i_fl = 11 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    i_org = 12 ; i_fl = 12 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    i_org = 13 ; i_fl = 13 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    i_org = 14 ; i_fl = 14 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    i_org = 15 ; i_fl = 15 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    i_org = 16 ; i_fl = 16 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    i_org = 17 ; i_fl = 17 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    i_org = 18 ; i_fl = 18 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    i_org = 27 ; i_fl = 27 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    i_org = 28 ; i_fl = 28 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
    i_org = 29 ; i_fl = 29 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;


    return org_fl_val_outputs






os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
#device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

device = torch.device('cpu')
map_location = torch.device('cpu')


#print(" - defining the model")

segmentation_model = UNet(spatial_dims=3,
    in_channels=1,
    out_channels=cl_num+1,
    channels=(32, 64, 128, 256, 512),
    strides=(2,2,2,2),
    kernel_size=3,
    up_kernel_size=3,
    num_res_units=1,
    act='PRELU',
    norm='INSTANCE',
    dropout=0.5
)

#print(" - loading the model")

with torch.no_grad():
  segmentation_model.load_state_dict(torch.load(model_weights_path_unet, map_location=torch.device('cpu')), strict=False)
  segmentation_model.to(device)
  segmentation_model.eval()


print(" - running segmentation : ", output_lab_name)

segmentation_inputs = final_image.unsqueeze(0).to(device)

flipped_segmentation_inputs = flipped_final_image.unsqueeze(0).to(device)

with torch.no_grad():

    # segmentation_output = sliding_window_inference(segmentation_inputs, (128, 128, 128), 4, segmentation_model, overlap=0.8)
    segmentation_output = segmentation_model(segmentation_inputs)
    org_flipped_segmentation_output = segmentation_model(flipped_segmentation_inputs)
    
    fl_tmp = flp_run(org_flipped_segmentation_output.clone())
    lr_flipped_segmentation_output = replace_lr(fl_tmp.clone())
    
    sum_outputs = (segmentation_output.clone() + lr_flipped_segmentation_output.clone()) / 2.0
    
    


label_output = torch.argmax(sum_outputs, dim=1).detach().cpu()[0, :, :, :]
label_matrix = label_output.cpu().numpy()

#print(" - saving results")

img_tmp_info = nib.load(input_img_name)
out_lab_nii = nib.Nifti1Image(label_matrix, img_tmp_info.affine, img_tmp_info.header)
nib.save(out_lab_nii, output_lab_name)


