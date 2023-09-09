#!/usr/bin/python

from __future__ import print_function
import sys
import os
import shutil
import tempfile



import matplotlib.pyplot as plt
import numpy as np
#from tqdm import tqdm
import nibabel as nib 

from monai.losses import DiceCELoss
from monai.inferers import sliding_window_inference
from monai.transforms import (
    AsDiscrete,
    AddChanneld,
    Compose,
    CropForegroundd,
    LoadImaged,
    Orientationd,
    RandFlipd,
    RandCropByPosNegLabeld,
    RandShiftIntensityd,
    ScaleIntensityRanged,
    ScaleIntensityd,
    Spacingd,
    RandRotate90d,
    RandBiasFieldd,
    RandAdjustContrastd,
    RandGaussianNoised,
    RandGaussianSmoothd,
    RandGaussianSharpend,
    RandHistogramShiftd,
    RandAffined,
    ToTensord,  
)


from monai.config import print_config
from monai.metrics import DiceMetric
from monai.networks.nets import UNETR, UNet

from monai.data import (
    DataLoader,
    CacheDataset,
    load_decathlon_datalist,
    decollate_batch,
)


import torch
import warnings
warnings.filterwarnings("ignore")
warnings.simplefilter("ignore")


#############################################################################################################
#############################################################################################################



files_path = sys.argv[1]
check_path = sys.argv[2]
json_file = sys.argv[3]
results_path = sys.argv[4]

res = int(sys.argv[5])
cl_num = int(sys.argv[6])


#############################################################################################################
#############################################################################################################


directory = os.environ.get("MONAI_DATA_DIRECTORY")
root_dir = tempfile.mkdtemp() if directory is None else directory

root_dir=files_path
os.chdir(root_dir)

run_transforms = Compose(
    [
        LoadImaged(keys=["image"]),
        AddChanneld(keys=["image"]),
        ScaleIntensityd(
            keys=["image"], minv=0.0, maxv=1.0
        ),
        ToTensord(keys=["image"]),
    ]
)

#############################################################################################################
#############################################################################################################


datasets = files_path + json_file
run_datalist = load_decathlon_datalist(datasets, True, "running")
run_ds = CacheDataset(
    data=run_datalist, transform=run_transforms,
    cache_num=100, cache_rate=1.0, num_workers=4,
)
run_loader = DataLoader(
    run_ds, batch_size=1, shuffle=False, num_workers=4, pin_memory=True
)

#############################################################################################################
#############################################################################################################

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
#device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

device = torch.device('cpu')
map_location = torch.device('cpu')


model = UNet(spatial_dims=3,
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
#.to(device)




loss_function = DiceCELoss(to_onehot_y=True, softmax=True)
torch.backends.cudnn.benchmark = True
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-5)

#############################################################################################################
#############################################################################################################


#model.load_state_dict(torch.load(os.path.join(check_path, "best_metric_model.pth")), strict=False)

model.load_state_dict(torch.load(os.path.join(check_path, "best_metric_model.pth"), map_location=torch.device('cpu')), strict=False)
model.to(device)

#model.eval()

for x in range(len(run_datalist)):
  # print(x)

  case_num = x
  img_name = run_datalist[case_num]["image"]
  case_name = os.path.split(run_ds[case_num]["image_meta_dict"]["filename_or_obj"])[1]
  out_name = results_path + "/cnn-lab-" + case_name

  print(case_num, out_name)

  img_tmp_info = nib.load(img_name)

  with torch.no_grad():
      img_name = os.path.split(run_ds[case_num]["image_meta_dict"]["filename_or_obj"])[1]
      img = run_ds[case_num]["image"]
      run_inputs = torch.unsqueeze(img, 1)
#      .cuda()
      run_outputs = sliding_window_inference(
          run_inputs, (res, res, res), 4, model, overlap=0.8
      )

      out_label = torch.argmax(run_outputs, dim=1).detach().cpu()[0, :, :, :]
      out_lab_nii = nib.Nifti1Image(out_label, img_tmp_info.affine, img_tmp_info.header)
      nib.save(out_lab_nii, out_name)



#############################################################################################################
#############################################################################################################




#############################################################################################################
#############################################################################################################





