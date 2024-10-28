

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

with torch.no_grad():

    # segmentation_output = sliding_window_inference(segmentation_inputs, (128, 128, 128), 4, segmentation_model, overlap=0.8)
    segmentation_output = segmentation_model(segmentation_inputs)


label_output = torch.argmax(segmentation_output, dim=1).detach().cpu()[0, :, :, :]
label_matrix = label_output.cpu().numpy()

#print(" - saving results")

img_tmp_info = nib.load(input_img_name)
out_lab_nii = nib.Nifti1Image(label_matrix, img_tmp_info.affine, img_tmp_info.header)
nib.save(out_lab_nii, output_lab_name)


