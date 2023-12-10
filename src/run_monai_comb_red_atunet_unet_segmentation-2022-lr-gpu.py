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
    #AddChanneld,
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
    Flip,
    
)


from monai.config import print_config
from monai.metrics import DiceMetric
from monai.networks.nets import UNet, AttentionUnet

from monai.data import (
    DataLoader,
    CacheDataset,
    load_decathlon_datalist,
    decollate_batch,
)


import torch


#############################################################################################################
#############################################################################################################


flp_run = Flip(1)

def replace_dhcp(fl_val_outputs):
  org_fl_val_outputs = fl_val_outputs.clone();

  i_org = 1 ; i_fl = 2 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
  i_org = 2 ; i_fl = 1 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;

  i_org = 3 ; i_fl = 4 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
  i_org = 4 ; i_fl = 3 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;

  i_org = 5 ; i_fl = 6 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
  i_org = 6 ; i_fl = 5 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;

  i_org = 7 ; i_fl = 8 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
  i_org = 8 ; i_fl = 7 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;

  i_org = 9 ; i_fl = 9 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
  i_org = 10 ; i_fl = 10 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;

  i_org = 11 ; i_fl = 12 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
  i_org = 12 ; i_fl = 11 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;

  i_org = 13 ; i_fl = 13 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;

  i_org = 14 ; i_fl = 15 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
  i_org = 15 ; i_fl = 14 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;

  i_org = 16 ; i_fl = 17 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
  i_org = 17 ; i_fl = 16 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;

  i_org = 18 ; i_fl = 18 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;
  i_org = 19 ; i_fl = 19 ; org_fl_val_outputs[0,i_org,:,:,:] = fl_val_outputs[0,i_fl,:,:,:] ;

  return org_fl_val_outputs


#############################################################################################################
#############################################################################################################



files_path = sys.argv[1]
check_path = sys.argv[2]
check_path2 = sys.argv[3]
json_file = sys.argv[4]
results_path = sys.argv[5]

res = int(sys.argv[6])
cl_num = int(sys.argv[7])




#res=160
#cl_num=17


#############################################################################################################
#############################################################################################################


directory = os.environ.get("MONAI_DATA_DIRECTORY")
root_dir = tempfile.mkdtemp() if directory is None else directory

root_dir=files_path
os.chdir(root_dir)

run_transforms = Compose(
    [
        LoadImaged(keys=["image"]),
        #AddChanneld(keys=["image"]),
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
    run_ds, batch_size=1, shuffle=False, num_workers=8, pin_memory=True
)

#############################################################################################################
#############################################################################################################

os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"

#os.environ["CUDA_VISIBLE_DEVICES"] = "1" 

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


#device = "cpu"


# model = UNet(spatial_dims=3,
#     in_channels=1,
#     out_channels=cl_num+1,
#     channels=(32, 64, 128, 256, 512),
#     strides=(2,2,2,2),
#     kernel_size=3,
#     up_kernel_size=3,
#     num_res_units=1,
#     act='PRELU',
#     norm='INSTANCE',
#     dropout=0.5
# ).to(device)


# model = AttentionUnet(spatial_dims=3,
#                        in_channels=1,
#                        out_channels=cl_num+1,
#                        channels=(32, 64, 128, 256, 512),
#                        strides=(2,2,2,2),
#                        kernel_size=3,
#                        up_kernel_size=3,
#                        dropout=0.5).to(device)


model = AttentionUnet(spatial_dims=3,
                     in_channels=1,
                     out_channels=cl_num+1,
                     channels=(16, 32, 64, 128, 256),
                     strides=(2,2,2,2),
                     kernel_size=3,
                     up_kernel_size=3,
                     dropout=0.5).to(device)


model2 = UNet(spatial_dims=3,
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
                    ).to(device)



loss_function = DiceCELoss(to_onehot_y=True, softmax=True)
torch.backends.cudnn.benchmark = True
optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-5)

#############################################################################################################
#############################################################################################################


#checkpoint_pth_path = os.path.join(check_path, "best_metric_model.pth")
#print("----------------------------------------------")
#print(checkpoint_pth_path)
#print("----------------------------------------------")

#model.load_state_dict(checkpoint_pth_path)


#model = torch.nn.DataParallel(model).to(device)

model.load_state_dict(torch.load(os.path.join(check_path, "best_metric_model.pth")), strict=False)
model.eval()


model2.load_state_dict(torch.load(os.path.join(check_path2, "best_metric_model.pth")), strict=False)
model2.eval()


for x in range(len(run_datalist)):
  # print(x)

  case_num = x
  img_name = run_datalist[case_num]["image"]
  case_name = os.path.split(img_name)[1]
  out_name = results_path + "/cnn-lab-" + case_name

  print(case_num, out_name)

  img_tmp_info = nib.load(img_name)

  with torch.no_grad():
      #img_name = os.path.split(run_ds[case_num]["image_meta_dict"]["filename_or_obj"])[1]
      img = run_ds[case_num]["image"]
      
      run_inputs = torch.unsqueeze(img.unsqueeze(0), 1).cuda()
      fl_run_inputs = torch.unsqueeze(img.unsqueeze(0), 1).cuda()
      fl_run_inputs = flp_run(fl_run_inputs)
      
      run_outputs = sliding_window_inference(
          run_inputs, (res, res, res), 4, model, overlap=0.8
      )
      
      run_outputs2 = sliding_window_inference(
          run_inputs, (res, res, res), 4, model2, overlap=0.8
      )
      
      fl_run_outputs = sliding_window_inference(
          fl_run_inputs, (res, res, res), 4, model, overlap=0.8
      )
      
      fl_run_outputs2 = sliding_window_inference(
          fl_run_inputs, (res, res, res), 4, model2, overlap=0.8
      )
      
      fl_run_outputs_tmp = flp_run(fl_run_outputs.clone())
      fl_run_outputs_fin = replace_dhcp(fl_run_outputs_tmp.clone())
      
      fl_run_outputs_tmp2 = flp_run(fl_run_outputs2.clone())
      fl_run_outputs_fin2 = replace_dhcp(fl_run_outputs_tmp2.clone())
      
      sum_run_outputs = (run_outputs.clone() + run_outputs2.clone() + fl_run_outputs_fin.clone() + fl_run_outputs_fin2.clone()) / 4.0


      out_label = torch.argmax(sum_run_outputs, dim=1).detach().cpu()[0, :, :, :]
      out_lab_nii = nib.Nifti1Image(out_label, img_tmp_info.affine, img_tmp_info.header)
      nib.save(out_lab_nii, out_name)



#############################################################################################################
#############################################################################################################




#############################################################################################################
#############################################################################################################





