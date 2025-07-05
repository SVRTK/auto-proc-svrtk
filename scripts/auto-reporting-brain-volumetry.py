




from matplotlib import pyplot as plt

import os

import numpy as np
import matplotlib as mt
import math
import pandas as pd
import scipy
from skimage import io

from scipy.stats import norm

import img2pdf
from PIL import Image

import PyPDF2

from skimage import measure
import plotly
import plotly.graph_objs as go
import plotly.express as px
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import Axes3D

import nibabel as nib
from nilearn.plotting import view_img, plot_glass_brain, plot_anat, plot_img, plot_roi
from nilearn.image import resample_to_img, resample_img

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import skimage.io as sio

from plotly.subplots import make_subplots

import warnings
warnings.filterwarnings("ignore")

import sys



#========================================================================
#========================================================================


def compute_label_volume(lab_nii, lab_nii_raw, l_num):
  x_dim, y_dim, z_dim = lab_nii.shape
  dx, dy, dz = lab_nii.header.get_zooms()
  n = 0
  for x in range(1, x_dim, 1):
    for y in range(1, y_dim, 1):
      for z in range(1, z_dim, 1):
        if lab_nii_raw[x,y,z] == l_num:
          n = n + 1
  vol = n * dx * dy * dz / 1000
  return vol


def compute_bounti_label_volume(lab_nii, lab_nii_raw):

  # 1 + 2
  external_csf = compute_label_volume(lab_nii, lab_nii_raw, 1) + compute_label_volume(lab_nii, lab_nii_raw, 2)
  # 3 + 4
  cortical_gm = compute_label_volume(lab_nii, lab_nii_raw, 3) + compute_label_volume(lab_nii, lab_nii_raw, 4)
  # 5 + 6
  fetal_wm = compute_label_volume(lab_nii, lab_nii_raw, 5) + compute_label_volume(lab_nii, lab_nii_raw, 6)
  # 7 + 8
  lat_ventricles = compute_label_volume(lab_nii, lab_nii_raw, 7) + compute_label_volume(lab_nii, lab_nii_raw, 8)
  left_ventricle = compute_label_volume(lab_nii, lab_nii_raw, 7)
  right_ventricle = compute_label_volume(lab_nii, lab_nii_raw, 8) 
  # 9
  cavum = compute_label_volume(lab_nii, lab_nii_raw, 9)
  # 10
  brainstem = compute_label_volume(lab_nii, lab_nii_raw, 10)
  # 11 + 12 + 13
  cerebellum = compute_label_volume(lab_nii, lab_nii_raw, 11) + compute_label_volume(lab_nii, lab_nii_raw, 12) + compute_label_volume(lab_nii, lab_nii_raw, 13)
  # 14 + 15 + 16 + 17
  deep_gm = compute_label_volume(lab_nii, lab_nii_raw, 14) + compute_label_volume(lab_nii, lab_nii_raw, 15) + compute_label_volume(lab_nii, lab_nii_raw, 16) + compute_label_volume(lab_nii, lab_nii_raw, 17)
  # 18 + 19
  sm_ventriles = compute_label_volume(lab_nii, lab_nii_raw, 18) + compute_label_volume(lab_nii, lab_nii_raw, 19)
  third_ventrile = compute_label_volume(lab_nii, lab_nii_raw, 18)
  fourth_ventrile = compute_label_volume(lab_nii, lab_nii_raw, 19)

  rr = 4
  external_csf = round(external_csf, rr)
  cortical_gm = round(cortical_gm, rr)
  fetal_wm = round(fetal_wm, rr)
  lat_ventricles = round(lat_ventricles, rr)
  left_ventricle = round(left_ventricle, rr)
  right_ventricle = round(right_ventricle, rr)
  cavum = round(cavum, rr)
  brainstem = round(brainstem, rr)
  cerebellum = round(cerebellum, rr)
  deep_gm = round(deep_gm, rr)
  sm_ventriles = round(sm_ventriles, rr)
  third_ventrile = round(third_ventrile, rr)
  fourth_ventrile = round(fourth_ventrile, rr)

  # print (external_csf, cortical_gm, fetal_wm, lat_ventricles, cavum, brainstem, cerebellum, deep_gm, sm_ventriles)

  return external_csf, cortical_gm, fetal_wm, lat_ventricles, left_ventricle, right_ventricle, cavum, brainstem, cerebellum, deep_gm, sm_ventriles, third_ventrile, fourth_ventrile

#========================================================================
#========================================================================

def centile_graphs(roi):

  a = 0
  b = 0
  c = 0
  a5 = 0
  b5 = 0
  c5 = 0
  title = ""


  roi_cmp="external_csf"
  if roi == roi_cmp:
    a = -0.23580
    b = 17.9930
    c = -250.0000
    a5 = 0.01105
    b5 = -0.00364
    c5 = 0.92868
    title = "External CSF"


  roi_cmp="cortical_gm"
  if roi == roi_cmp:
    a = 0.30520
    b = -11.82800
    c = 123.0000
    a5 = 0.01647
    b5 = -0.47701
    c5 = 3.76905
    title = "Cortical GM"


  roi_cmp="fetal_wm"
  if roi == roi_cmp:
    a = 0.02230
    b = 7.34710
    c = -145.28000
    a5 = 0.0098622
    b5 = 0.10410
    c5 = -3.9009446
    title = "Fetal WM"


  roi_cmp="deep_gm"
  if roi == roi_cmp:
    a = 0.0149
    b = -0.0475
    c = -3.5148
    a5 = -0.0005329
    b5 = 0.0765574
    c5 = -1.1757984
    title = "Deep GM"


  roi_cmp="lat_ventricles"
  if roi == roi_cmp:
    a = -0.0033
    b = 0.4438
    c = -5.6119
    a5 = -0.0039848
    b5 = 0.2970984
    c5 = -4.0358433
    title = "Lateral Ventricles"


  roi_cmp="cavum"
  if roi == roi_cmp:
    a = -0.0044
    b = 0.2808
    c = -3.76
    a5 = 0.00014
    b5 = 0.00304
    c5 = 0.001
    title = "Cavum"

  roi_cmp="brainstem"
  if roi == roi_cmp:
    a = 0.0038
    b = 0.086
    c = -2.1428
    a5 = -0.0002952
    b5 = 0.0340193
    c5 = -0.4995123
    title = "Brainstem"

  roi_cmp="cerebellum"
  if roi == roi_cmp:
    a = 0.0451
    b = -1.6575
    c = 16.314
    a5 = 0.0011411
    b5 = 0.0112348
    c5 = -0.5235345
    title = "Cerebellum and Vermis"

  roi_cmp="sm_ventriles"
  if roi == roi_cmp:
    a = 0.00043
    b = 0.0021979
    c = -0.1606777
    a5 = 0.00018
    b5 = -0.0068295
    c5 = 0.0827352
    title = "3rd and 4th ventriles"




  x = np.linspace(20, 40, 100)
  y = a*x*x + b*x + c

  y5 = y - 1.645*(a5*x*x + b5*x + c5)
  y95 = y + 1.645*(a5*x*x + b5*x + c5)

  return x, y, y5, y95, title


def subject_percentile(roi, ga, y_subject):

  a = 0
  b = 0
  c = 0
  a5 = 0
  b5 = 0
  c5 = 0
  title = ""


  roi_cmp="external_csf"
  if roi == roi_cmp:
    a = -0.23580
    b = 17.9930
    c = -250.0000
    a5 = 0.01105
    b5 = -0.00364
    c5 = 0.92868
    title = "External CSF"


  roi_cmp="cortical_gm"
  if roi == roi_cmp:
    a = 0.30520
    b = -11.82800
    c = 123.0000
    a5 = 0.01647
    b5 = -0.47701
    c5 = 3.76905
    title = "Cortical GM"


  roi_cmp="fetal_wm"
  if roi == roi_cmp:
    a = 0.02230
    b = 7.34710
    c = -145.28000
    a5 = 0.0098622
    b5 = 0.10410
    c5 = -3.9009446
    title = "Fetal WM"


  roi_cmp="deep_gm"
  if roi == roi_cmp:
    a = 0.0149
    b = -0.0475
    c = -3.5148
    a5 = -0.0005329
    b5 = 0.0765574
    c5 = -1.1757984
    title = "Deep GM"


  roi_cmp="lat_ventricles"
  if roi == roi_cmp:
    a = -0.0033
    b = 0.4438
    c = -5.6119
    a5 = -0.0039848
    b5 = 0.2970984
    c5 = -4.0358433
    title = "Lateral Ventricles"


  roi_cmp="lr_ventricle"
  if roi == roi_cmp:
    a = -0.00329
    b = 0.31120
    c = -3.99901
    a5 = -0.00451
    b5 = 0.29420
    c5 = -3.99013
    title = "L/R Lateral Ventricles"


  roi_cmp="cavum"
  if roi == roi_cmp:
    a = -0.0044
    b = 0.2808
    c = -3.76
    a5 = 0.00014
    b5 = 0.00304
    c5 = 0.001
    title = "Cavum"

  roi_cmp="brainstem"
  if roi == roi_cmp:
    a = 0.0038
    b = 0.086
    c = -2.1428
    a5 = -0.0002952
    b5 = 0.0340193
    c5 = -0.4995123
    title = "Brainstem"

  roi_cmp="cerebellum"
  if roi == roi_cmp:
    a = 0.0451
    b = -1.6575
    c = 16.314
    a5 = 0.0011411
    b5 = 0.0112348
    c5 = -0.5235345
    title = "Cerebellum and Vermis"

  roi_cmp="sm_ventriles"
  if roi == roi_cmp:
    a = 0.00043
    b = 0.0021979
    c = -0.1606777
    a5 = 0.00018
    b5 = -0.0068295
    c5 = 0.0827352
    title = "3rd and 4th ventriles"

  roi_cmp="third_ventrile"
  if roi == roi_cmp:
    a = -0.00016
    b = 0.02617
    c = -0.45036
    a5 = 0.000
    b5 = 0.00277
    c5 = -0.05600
    title = "3rd ventrile"


  roi_cmp="fourth_ventrile"
  if roi == roi_cmp:
    a = 0.00044
    b = -0.01590
    c = 0.18471
    a5 = 0.000
    b5 = 0.00192
    c5 = -0.03908
    title = "4th ventrile"


  x = ga
  y_ga = a*x*x + b*x + c
  
  y5 = y_ga - 1.645*(a5*x*x + b5*x + c5)
  y95 = y_ga + 1.645*(a5*x*x + b5*x + c5)
  
  sd_ga = np.polyval([a5, b5, c5], ga)
  
  z_score = (y_subject - y_ga) / sd_ga
  
  percentile = norm.cdf(z_score) * 100
  
  return percentile

#  return z_score, percentile







def plot_vol_centiles4(id, scan_date, ga, external_csf, cortical_gm, fetal_wm, lat_ventricles, cavum, brainstem, cerebellum, deep_gm, sm_ventriles, plot_file_name):

  # roi="cortical_gm"

  fig = make_subplots(rows=5,
                      cols=2,
                      vertical_spacing=0.09,
                      subplot_titles=("Supratentorial brain", "Cortical GM", "Fetal WM", "Deep GM", "External CSF", "Lateral Ventricles", "Cavum", "Brainstem", "Cerebellum and Vermis", "3rd and 4th ventriles"))


  m_size = 9

  s_r = 1
  s_c = 2
  roi = "cortical_gm"
  vol = cortical_gm
  x, y, y5, y95, title = centile_graphs(roi)
  fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line_color='black'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=x, y=y5, mode='lines', line_color='grey'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=x, y=y95, mode='lines', line_color='grey'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=[ga], y=[vol], mode='markers', marker_color='red', marker_size=m_size, opacity=0.8, marker_symbol='x'), row = s_r, col = s_c)
  fig.update_xaxes(title_text="GA [weeks]", gridcolor='lightgrey', nticks=10, row = s_r, col = s_c)
  fig.update_yaxes(title_text="Volume [cc]", gridcolor='lightgrey', nticks=10, row = s_r, col = s_c)

  y_total = y
  y_total_5 = y5
  y_total_95 = y95
  vol_total = vol


  s_r = 2
  s_c = 1
  roi = "fetal_wm"
  vol = fetal_wm
  x, y, y5, y95, title = centile_graphs(roi)
  fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line_color='black'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=x, y=y5, mode='lines', line_color='grey'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=x, y=y95, mode='lines', line_color='grey'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=[ga], y=[vol], mode='markers', marker_color='red', marker_size=m_size, opacity=0.8, marker_symbol='x'), row = s_r, col = s_c)
  fig.update_xaxes(title_text="GA [weeks]", gridcolor='lightgrey', nticks=10, row = s_r, col = s_c)
  fig.update_yaxes(title_text="Volume [cc]", gridcolor='lightgrey', nticks=10, row = s_r, col = s_c)

  y_total = y_total + y
  y_total_5 = y_total_5 + y5
  y_total_95 = y_total_95 + y95
  vol_total = vol_total + vol

  s_r = 2
  s_c = 2
  roi = "deep_gm"
  vol = deep_gm
  x, y, y5, y95, title = centile_graphs(roi)
  fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line_color='black'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=x, y=y5, mode='lines', line_color='grey'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=x, y=y95, mode='lines', line_color='grey'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=[ga], y=[vol], mode='markers', marker_color='red', marker_size=m_size, opacity=0.8, marker_symbol='x'), row = s_r, col = s_c)
  fig.update_xaxes(title_text="GA [weeks]", gridcolor='lightgrey', nticks=10, row = s_r, col = s_c)
  fig.update_yaxes(title_text="Volume [cc]", gridcolor='lightgrey', nticks=10, row = s_r, col = s_c)

  y_total = y_total + y
  y_total_5 = y_total_5 + y5
  y_total_95 = y_total_95 + y95
  vol_total = vol_total + vol



  s_r = 1
  s_c = 1
  roi = "total"
  fig.add_trace(go.Scatter(x=x, y=y_total, mode='lines', line_color='black'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=x, y=y_total_5, mode='lines', line_color='grey'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=x, y=y_total_95, mode='lines', line_color='grey'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=[ga], y=[vol_total], mode='markers', marker_color='red', marker_size=m_size, opacity=0.8, marker_symbol='x'), row = s_r, col = s_c)
  fig.update_xaxes(title_text="GA [weeks]", gridcolor='lightgrey', nticks=10, row = s_r, col = s_c)
  fig.update_yaxes(title_text="Volume [cc]", gridcolor='lightgrey', nticks=10, row = s_r, col = s_c)


  s_r = 3
  s_c = 1
  roi = "external_csf"
  vol = external_csf
  x, y, y5, y95, title = centile_graphs(roi)
  fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line_color='black'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=x, y=y5, mode='lines', line_color='grey'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=x, y=y95, mode='lines', line_color='grey'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=[ga], y=[vol], mode='markers', marker_color='red', marker_size=m_size, opacity=0.8, marker_symbol='x'), row = s_r, col = s_c)
  fig.update_xaxes(title_text="GA [weeks]", gridcolor='lightgrey', nticks=10, row = s_r, col = s_c)
  fig.update_yaxes(title_text="Volume [cc]", gridcolor='lightgrey', nticks=10, row = s_r, col = s_c)

  s_r = 3
  s_c = 2
  roi = "lat_ventricles"
  vol = lat_ventricles
  x, y, y5, y95, title = centile_graphs(roi)
  fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line_color='black'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=x, y=y5, mode='lines', line_color='grey'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=x, y=y95, mode='lines', line_color='grey'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=[ga], y=[vol], mode='markers', marker_color='red', marker_size=m_size, opacity=0.8, marker_symbol='x'), row = s_r, col = s_c)
  fig.update_xaxes(title_text="GA [weeks]", gridcolor='lightgrey', nticks=10, row = s_r, col = s_c)
  fig.update_yaxes(title_text="Volume [cc]", gridcolor='lightgrey', nticks=10, row = s_r, col = s_c)


  s_r = 4
  s_c = 1
  roi = "cavum"
  vol = cavum
  x, y, y5, y95, title = centile_graphs(roi)
  fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line_color='black'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=x, y=y5, mode='lines', line_color='grey'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=x, y=y95, mode='lines', line_color='grey'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=[ga], y=[vol], mode='markers', marker_color='red', marker_size=m_size, opacity=0.8, marker_symbol='x'), row = s_r, col = s_c)
  fig.update_xaxes(title_text="GA [weeks]", gridcolor='lightgrey', nticks=10, row = s_r, col = s_c)
  fig.update_yaxes(title_text="Volume [cc]", gridcolor='lightgrey', nticks=10, row = s_r, col = s_c)


  s_r = 4
  s_c = 2
  roi = "brainstem"
  vol = brainstem
  x, y, y5, y95, title = centile_graphs(roi)
  fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line_color='black'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=x, y=y5, mode='lines', line_color='grey'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=x, y=y95, mode='lines', line_color='grey'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=[ga], y=[vol], mode='markers', marker_color='red', marker_size=m_size, opacity=0.8, marker_symbol='x'), row = s_r, col = s_c)
  fig.update_xaxes(title_text="GA [weeks]", gridcolor='lightgrey', nticks=10, row = s_r, col = s_c)
  fig.update_yaxes(title_text="Volume [cc]", gridcolor='lightgrey', nticks=10, row = s_r, col = s_c)

  s_r = 5
  s_c = 1
  roi = "cerebellum"
  vol = cerebellum
  x, y, y5, y95, title = centile_graphs(roi)
  fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line_color='black'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=x, y=y5, mode='lines', line_color='grey'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=x, y=y95, mode='lines', line_color='grey'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=[ga], y=[vol], mode='markers', marker_color='red', marker_size=m_size, opacity=0.8, marker_symbol='x'), row = s_r, col = s_c)
  fig.update_xaxes(title_text="GA [weeks]", gridcolor='lightgrey', nticks=10, row = s_r, col = s_c)
  fig.update_yaxes(title_text="Volume [cc]", gridcolor='lightgrey', nticks=10, row = s_r, col = s_c)

  s_r = 5
  s_c = 2
  roi = "sm_ventriles"
  vol = sm_ventriles
  x, y, y5, y95, title = centile_graphs(roi)
  fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line_color='black'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=x, y=y5, mode='lines', line_color='grey'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=x, y=y95, mode='lines', line_color='grey'), row = s_r, col = s_c)
  fig.add_trace(go.Scatter(x=[ga], y=[vol], mode='markers', marker_color='red', marker_size=m_size, opacity=0.8, marker_symbol='x'), row = s_r, col = s_c)
  fig.update_xaxes(title_text="GA [weeks]", gridcolor='lightgrey', nticks=10, row = s_r, col = s_c)
  fig.update_yaxes(title_text="Volume [cc]", gridcolor='lightgrey', nticks=10, row = s_r, col = s_c)


  title = "Brain volumetry: " + id + " / " + str(ga) + " weeks / " + scan_date


  fig.update_layout(height=1414,
                    width=1000,
                    showlegend=False,
                    plot_bgcolor='white',
                    title_text=title,
                    # title_font_family="Arial Black",
                    )

  fig.show()

  fig.write_image(plot_file_name)


def merge_pdfs(pdf1, pdf2, output):
    merger = PyPDF2.PdfMerger()
    
    with open(pdf1, 'rb') as f1, open(pdf2, 'rb') as f2:
        merger.append(f1)
        merger.append(f2)
    
    with open(output, 'wb') as fout:
        merger.write(fout)


#========================================================================
#========================================================================


input_id = sys.argv[1]
input_ga = float(sys.argv[2])
input_scan_date = sys.argv[3]

input_img_nii_name = sys.argv[4]
input_lab_nii_name = sys.argv[5]

proc_dir = sys.argv[6]

output_report_name_pdf = sys.argv[7]

print()
print("--------------------------------------------------------------")
print()

print("Inputs : ")
print(" - ", input_id, " ", input_ga)
print(" - ", input_img_nii_name)
print(" - ", input_lab_nii_name)

input_img_nii = nib.load(input_img_nii_name)
input_lab_nii = nib.load(input_lab_nii_name)

input_img_matrix = input_img_nii.get_fdata();
input_lab_matrix = input_lab_nii.get_fdata();



print(" - ", input_lab_nii.shape, ", ", input_lab_nii.header.get_zooms(), "mm")

print()
print("--------------------------------------------------------------")
print()

print("Extracting volumes ... ")

external_csf, cortical_gm, fetal_wm, lat_ventricles, left_ventricle, right_ventricle, cavum, brainstem, cerebellum, deep_gm, sm_ventriles, third_ventrile, fourth_ventrile = compute_bounti_label_volume(input_lab_nii, input_lab_matrix)

print()
print("--------------------------------------------------------------")
print()

print("Printing images ... ")


f = plt.figure(figsize=(12,4));
f_name_grey_ortho = proc_dir + '/out-rad-grey.png'

min_val_for_display = 0
max_val_for_display = input_img_matrix.max()*0.8

plot_roi(input_img_nii,
         bg_img=input_img_nii,
         dim=0,
         cmap='gray',
         vmin=0,
         figure=f,
         display_mode='ortho',
        #  vmax=1,
         black_bg=True);

plt.savefig(f_name_grey_ortho)


f = plt.figure(figsize=(20,4));
f_name_lab_axial = proc_dir + '/out-rad-with-lab-axial.png'

plot_roi(input_lab_nii,
         bg_img=input_img_nii,
         alpha=0.5,
         dim=-0.5,
         cmap='jet',
         resampling_interpolation='nearest',
         vmin=0,
        #  axes=(0,0, 8, 4),
         figure=f,
         annotate=False,
         display_mode='z',
         cut_coords=10,
        #  vmax=1,
        #  colorbar=True,
         black_bg=True);

plt.savefig(f_name_lab_axial)

f = plt.figure(figsize=(20,4));
f_name_lab_sag = proc_dir + '/out-rad-with-lab-sag.png'

plot_roi(input_lab_nii,
         bg_img=input_img_nii,
         alpha=0.5,
         dim=-0.5,
         cmap='jet',
         resampling_interpolation='nearest',
         vmin=0,
        #  axes=(0,0, 8, 4),
         figure=f,
         annotate=False,
         display_mode='x',
         cut_coords=10,
        #  vmax=1,
        #  colorbar=True,
         black_bg=True);

plt.savefig(f_name_lab_sag)



f = plt.figure(figsize=(20,4));
f_name_lab_coronal = proc_dir + '/out-rad-with-lab-coronal.png'

plot_roi(input_lab_nii,
         bg_img=input_img_nii,
         alpha=0.5,
         dim=-0.5,
         cmap='jet',
         resampling_interpolation='nearest',
         vmin=0,
        #  axes=(0,0, 8, 4),
         figure=f,
         annotate=False,
         display_mode='y',
         cut_coords=10,
        #  vmax=1,
        #  colorbar=True,
         black_bg=True);

plt.savefig(f_name_lab_coronal)



print()
print("--------------------------------------------------------------")
print()

print("Printing graphs ... ")

f_name_vol_centiles = proc_dir + '/out-volume-centiles.png'

plot_vol_centiles4(input_id, input_scan_date, input_ga,
               external_csf,
               cortical_gm,
               fetal_wm,
               lat_ventricles,
               cavum,
               brainstem,
               cerebellum,
               deep_gm,
               sm_ventriles,
               f_name_vol_centiles
               )

print()
print("--------------------------------------------------------------")
print()

print("Generating summary intro  ... ")


img = io.imread(f_name_grey_ortho)
figm1 = px.imshow(img)

img = io.imread(f_name_lab_axial)
figm2 = px.imshow(img)

img = io.imread(f_name_lab_coronal)
figm3 = px.imshow(img)

#img = io.imread(f_name_lab_sag)
#figm4 = px.imshow(img)

fig = make_subplots(
    rows=4, cols=1, horizontal_spacing=0.01,
    vertical_spacing=0.001,
    specs=[[{"type": "image"}],
           [{"type": "image"}],
#           [{"type": "image"}],
           [{"type": "table"}],
           [{"type": "table"}],
          #  [{"type": "image"}]
           ])


fig.add_trace(figm1.data[0], row=1, col=1)

#fig.add_trace(figm2.data[0], row=2, col=1)

fig.add_trace(figm2.data[0], row=2, col=1)

#fig.add_trace(figm4.data[0], row=4, col=1)

input_lab_nii_zooms = input_lab_nii.header.get_zooms()
dx = round(input_lab_nii_zooms[1],2)

#fig.add_trace(
#    go.Table(header=dict(font_size=14, values=['Segmentation ROI', 'Volume [cc]']),
#                 cells=dict(fill_color='white', font_size=14, line_color='lightgray',
#                            values=[["Supratentorial brain", "Cortical GM", "Fetal WM", "Deep GM",
#                                     "External CSF", "Lateral Ventricles", "Left Ventricle", "Right Ventricle",
#                                     "Cavum", "Brainstem", "Cerebellum", "3rd Ventrile", "4th Ventricle" ],
#                  [round((cortical_gm + fetal_wm + deep_gm),4), cortical_gm, fetal_wm, deep_gm,
#                   external_csf, lat_ventricles, left_ventricle, right_ventricle,
#                   cavum, brainstem, cerebellum, third_ventrile, fourth_ventrile]])),
#    row=3, col=1
#)


sup_brain = (cortical_gm + fetal_wm + deep_gm)

rr = 4



fig.add_trace(
    go.Table(header=dict(font_size=14, values=['Segmentation ROI', 'Volume [cc]', 'Percentile'], ),
                 cells=dict(fill_color='white', font_size=14, line_color='lightgray',
                            values=[["Supratentorial brain", "Cortical GM", "Fetal WM", "Deep GM",
                                     "External CSF", "Lateral Ventricles", "Left Ventricle", "Right Ventricle",
                                     "Cavum", "Brainstem", "Cerebellum and Vermis", "3rd Ventrile", "4th Ventricle" ],
                  [round(sup_brain,4), cortical_gm, fetal_wm, deep_gm,
                   external_csf, lat_ventricles, left_ventricle, right_ventricle,
                   cavum, brainstem, cerebellum, third_ventrile, fourth_ventrile],
                   ["-",
                    round(subject_percentile("cortical_gm", input_ga, cortical_gm),rr),
                    round(subject_percentile("fetal_wm", input_ga, fetal_wm),rr),
                    round(subject_percentile("deep_gm", input_ga, deep_gm),rr),
                    round(subject_percentile("external_csf", input_ga, external_csf),rr),
                    round(subject_percentile("lat_ventricles", input_ga, lat_ventricles),rr),
                    round(subject_percentile("lr_ventricle", input_ga, left_ventricle),rr),
                    round(subject_percentile("lr_ventricle", input_ga, right_ventricle),rr),
                    round(subject_percentile("cavum", input_ga, cavum),rr),
                    round(subject_percentile("brainstem", input_ga, brainstem),rr),
                    round(subject_percentile("cerebellum", input_ga, cerebellum),rr),
                    round(subject_percentile("third_ventrile", input_ga, third_ventrile),rr),
                    round(subject_percentile("fourth_ventrile", input_ga, fourth_ventrile),rr)
                    ]
                   ])),
    row=3, col=1
)




fig.add_trace(
    go.Table(header=dict(font_size=14, values=['Case info']),
                 cells=dict(fill_color='white', font_size=14, line_color='lightgray',
                            values=[[input_id, (str(input_ga) + " weeks"), (input_scan_date),
                                     ( str(dx) + " mm resolution") ]])),
    row=4, col=1
)


fig.update_xaxes(visible=False)
fig.update_yaxes(visible=False)

title = "Brain volumetry: " + input_id + " / " + str(input_ga) + " weeks / " + input_scan_date

fig.update_layout(
                    height=1414,
                    # height=1200,
                    width=1000,
                    showlegend=False,
                    plot_bgcolor='white',
                    title_text=title,
                    # title_font_family="Arial Black",
                    )
fig.show()

f_name_summary_intro = proc_dir + '/out-summary-intro.png'

fig.write_image(f_name_summary_intro)




print()
print("--------------------------------------------------------------")
print()


print("Combining and converting to .pdf ... ")


#f_name_summary_intro = proc_dir + '/out-summary-intro.png'
f_name_summary_intro_pdf = proc_dir + '/out-summary-intro.pdf'

image = Image.open(f_name_summary_intro)
pdf_bytes = img2pdf.convert(image.filename)
file = open(f_name_summary_intro_pdf, "wb")
file.write(pdf_bytes)
image.close()
file.close()

f_name_vol_centiles = proc_dir + '/out-volume-centiles.png'
f_name_vol_centiles_pdf = proc_dir + '/out-volume-centiles.pdf'

image = Image.open(f_name_vol_centiles)
pdf_bytes = img2pdf.convert(image.filename)
file = open(f_name_vol_centiles_pdf, "wb")
file.write(pdf_bytes)
image.close()
file.close()


#f_name_report_pdf = proc_dir + '/out-report-combined.pdf'

merge_pdfs(f_name_summary_intro_pdf, f_name_vol_centiles_pdf, output_report_name_pdf)

print()
print("--------------------------------------------------------------")
print()




