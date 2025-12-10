
import os
import warnings
warnings.filterwarnings("ignore")
import sys
import nibabel as nib
import numpy as np
import plotly.graph_objs as go
import matplotlib.pyplot as plt
from nilearn.plotting import plot_roi
import base64
from io import BytesIO
from scipy.spatial.distance import euclidean
import scipy.stats as stats
from scipy.stats import norm
import matplotlib.cm as cm
from matplotlib.colors import ListedColormap


jet = cm.get_cmap('jet', 256)
jet_colors = jet(np.linspace(0, 1, 256))
jet_colors[0, -1] = 0  # Set alpha of the first color (usually label 0) to 0
jet_transparent = ListedColormap(jet_colors)


#========================================================================
#========================================================================

def compute_volume(input_lab_matrix, label1, label2, label3, label4, label5, voxel_dims):

    landmark1_coords = np.count_nonzero(input_lab_matrix == label1)
    landmark2_coords = np.count_nonzero(input_lab_matrix == label2)
    landmark3_coords = np.count_nonzero(input_lab_matrix == label3)
    landmark4_coords = np.count_nonzero(input_lab_matrix == label4)
    landmark5_coords = np.count_nonzero(input_lab_matrix == label5)

    volume_cc = (landmark1_coords + landmark2_coords + landmark3_coords + landmark4_coords + landmark5_coords) * voxel_dims[0] * voxel_dims[1] * voxel_dims[2]

    volume_cc = volume_cc / 1000

    return volume_cc
    


def compute_weight(input_lab_matrix, voxel_dims):

    label1 = 3
    label2 = 4

    landmark1_coords = np.count_nonzero(input_lab_matrix == label1)
    landmark2_coords = np.count_nonzero(input_lab_matrix == label2)

    volume_cc = (landmark1_coords + landmark2_coords) * voxel_dims[0] * voxel_dims[1] * voxel_dims[2]

#    volume_cc = volume_cc / 1000
    
    weight_kg = 1.06 * 0.001 * volume_cc + 0.12

    return weight_kg


#($EFW_{Baker}(kg) = 1.06 \cdot V_{fetus} + 0.12$) \cite{Baker1994}


def compute_head_body_ratio(input_lab_matrix, voxel_dims):

    label1 = 3
    label2 = 4
    
    landmark1_coords = np.count_nonzero(input_lab_matrix == label1)
    landmark2_coords = np.count_nonzero(input_lab_matrix == label2)

    head_volume_cc = (landmark2_coords) * voxel_dims[0] * voxel_dims[1] * voxel_dims[2]
    body_volume_cc = (landmark1_coords) * voxel_dims[0] * voxel_dims[1] * voxel_dims[2]

    head_body_ratio = head_volume_cc / body_volume_cc

    return head_body_ratio



def plot_uterus_image(t2w_data, mask_data):


    fig, axs = plt.subplots(2, 3, figsize=(20, 15))
    fig, axs = plt.subplots(2, 3, figsize=(20, 15))
    axs = axs.flatten()

    x, y, z = t2w_data.shape
    a = 0.4

#    coronal_t2w_slice1 = t2w_data[:, round(y*0.4), :]
#    coronal_t2w_slice2 = t2w_data[:, round(y*0.45), :]
#    coronal_t2w_slice3 = t2w_data[:, round(y*0.5), :]
#    coronal_t2w_slice4 = t2w_data[:, round(y*0.55), :]
#    coronal_t2w_slice5 = t2w_data[:, round(y*0.6), :]
#
#    coronal_lab_slice1 = mask_data[:, round(y*0.4), :]
#    coronal_lab_slice2 = mask_data[:, round(y*0.45), :]
#    coronal_lab_slice3 = mask_data[:, round(y*0.5), :]
#    coronal_lab_slice4 = mask_data[:, round(y*0.55), :]
#    coronal_lab_slice5 = mask_data[:, round(y*0.6), :]


    coronal_t2w_slice1 = t2w_data[round(x*0.5), :, :]
    coronal_t2w_slice3 = t2w_data[:, round(y*0.5), :]
    coronal_t2w_slice5 = t2w_data[:, :, round(z*0.5)]

    coronal_lab_slice1 = mask_data[round(x*0.5), :, :]
    coronal_lab_slice3 = mask_data[:, round(y*0.5), :]
    coronal_lab_slice5 = mask_data[:, :, round(z*0.5)]



    min_label=0
    max_label=4
    
    min_img=0
    max_img=0.6*np.max(t2w_data)
    
    
    i = 0
    axs[i].imshow(np.rot90(coronal_t2w_slice1.T, k=1), cmap='gray', origin='lower', vmin=min_img, vmax=max_img)
    # axs[i].imshow(np.rot90(coronal_lab_slice1.T, k=1), cmap='jet', origin='lower', alpha=a)
    axs[i].axis('off')

#    i = 1
#    axs[i].imshow(np.rot90(coronal_t2w_slice2.T, k=1), cmap='gray', origin='lower', vmin=min_img, vmax=max_img)
#    # axs[i].imshow(np.rot90(coronal_lab_slice2.T, k=1), cmap='jet', origin='lower', alpha=a)
#    axs[i].axis('off')

    i = 1
    axs[i].imshow(np.rot90(coronal_t2w_slice3.T, k=1), cmap='gray', origin='lower', vmin=min_img, vmax=max_img)
    # axs[i].imshow(np.rot90(coronal_lab_slice3.T, k=1), cmap='jet', origin='lower', alpha=a)
    axs[i].axis('off')

#    i = 3
#    axs[i].imshow(np.rot90(coronal_t2w_slice4.T, k=1), cmap='gray', origin='lower', vmin=min_img, vmax=max_img)
#    # axs[i].imshow(np.rot90(coronal_lab_slice4.T, k=1), cmap='jet', origin='lower', alpha=a)
#    axs[i].axis('off')

    i = 2
    axs[i].imshow(np.rot90(coronal_t2w_slice5.T, k=1), cmap='gray', origin='lower', vmin=min_img, vmax=max_img)
    # axs[i].imshow(np.rot90(coronal_lab_slice5.T, k=1), cmap='jet', origin='lower', alpha=a)
    axs[i].axis('off')

    i = 3
    axs[i].imshow(np.rot90(coronal_t2w_slice1.T, k=1), cmap='gray', origin='lower', vmin=min_img, vmax=max_img)
    axs[i].imshow(np.rot90(coronal_lab_slice1.T, k=1), cmap=jet_transparent, origin='lower', alpha=a, vmin=min_label, vmax=max_label)
    axs[i].axis('off')

#    i = 6
#    axs[i].imshow(np.rot90(coronal_t2w_slice2.T, k=1), cmap='gray', origin='lower', vmin=min_img, vmax=max_img)
#    axs[i].imshow(np.rot90(coronal_lab_slice2.T, k=1), cmap=jet_transparent, origin='lower', alpha=a, vmin=min_label, vmax=max_label)
#    axs[i].axis('off')

    i = 4
    axs[i].imshow(np.rot90(coronal_t2w_slice3.T, k=1), cmap='gray', origin='lower', vmin=min_img, vmax=max_img)
    axs[i].imshow(np.rot90(coronal_lab_slice3.T, k=1), cmap=jet_transparent, origin='lower', alpha=a, vmin=min_label, vmax=max_label)
    axs[i].axis('off')

#    i = 8
#    axs[i].imshow(np.rot90(coronal_t2w_slice4.T, k=1), cmap='gray', origin='lower', vmin=min_img, vmax=max_img)
#    axs[i].imshow(np.rot90(coronal_lab_slice4.T, k=1), cmap=jet_transparent, origin='lower', alpha=a, vmin=min_label, vmax=max_label)
#    axs[i].axis('off')

    i = 5
    axs[i].imshow(np.rot90(coronal_t2w_slice5.T, k=1), cmap='gray', origin='lower', vmin=min_img, vmax=max_img)
    axs[i].imshow(np.rot90(coronal_lab_slice5.T, k=1), cmap=jet_transparent, origin='lower', alpha=a, vmin=min_label, vmax=max_label)
    axs[i].axis('off')


    # Adjust layout
    plt.tight_layout()

    # Save the figure to a BytesIO object
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_b64 = base64.b64encode(buf.read()).decode('utf-8')  # Encode to base64
    plt.close(fig)  # Close the figure to avoid display

    return image_b64


def create_centile_graph(ga, computed_value, a, b, c, a5, b5, c5, title):
    x = np.linspace(20, 40, 100)
    y = a * x * x + b * x + c

    y5 = y - 1.645 * (a5 * x * x + b5 * x + c5)
    y95 = y + 1.645 * (a5 * x * x + b5 * x + c5)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line_color='black'))
    fig.add_trace(go.Scatter(x=x, y=y5, mode='lines', line_color='grey'))
    fig.add_trace(go.Scatter(x=x, y=y95, mode='lines', line_color='grey'))
    fig.add_trace(go.Scatter(x=[ga], y=[computed_value], mode='markers', marker_color='red',
                             marker_size=10, marker_symbol='x'))
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="GA [weeks]",
        yaxis_title="volume [cc]",
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(gridcolor='lightgrey'),
        yaxis=dict(gridcolor='lightgrey'),
        showlegend=False
    )
    return fig.to_html(full_html=False)



def create_centile_graph_ratio(ga, computed_value, a, b, c, a5, b5, c5, title):
    x = np.linspace(20, 40, 100)
    y = a * x * x + b * x + c

    y5 = y - 1.645 * (a5 * x * x + b5 * x + c5)
    y95 = y + 1.645 * (a5 * x * x + b5 * x + c5)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line_color='black'))
    fig.add_trace(go.Scatter(x=x, y=y5, mode='lines', line_color='grey'))
    fig.add_trace(go.Scatter(x=x, y=y95, mode='lines', line_color='grey'))
    fig.add_trace(go.Scatter(x=[ga], y=[computed_value], mode='markers', marker_color='red',
                             marker_size=10, marker_symbol='x'))
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="GA [weeks]",
        yaxis_title="ratio",
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(gridcolor='lightgrey'),
        yaxis=dict(gridcolor='lightgrey'),
        showlegend=False
    )
    return fig.to_html(full_html=False)


def create_centile_graph_weight(ga, computed_value, a, b, c, a5, b5, c5, title):
    x = np.linspace(20, 40, 100)
    y = a * x * x + b * x + c

    y5 = y - 1.645 * (a5 * x * x + b5 * x + c5)
    y95 = y + 1.645 * (a5 * x * x + b5 * x + c5)
    
    y = 1.06 * y + 0.12
    y5 = 1.06 * y5 + 0.12
    y95 = 1.06 * y95 + 0.12
     

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='lines', line_color='black'))
    fig.add_trace(go.Scatter(x=x, y=y5, mode='lines', line_color='grey'))
    fig.add_trace(go.Scatter(x=x, y=y95, mode='lines', line_color='grey'))
    fig.add_trace(go.Scatter(x=[ga], y=[computed_value], mode='markers', marker_color='red',
                             marker_size=10, marker_symbol='x'))
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center'
        },
        xaxis_title="GA [weeks]",
        yaxis_title="weight [g]",
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(gridcolor='lightgrey'),
        yaxis=dict(gridcolor='lightgrey'),
        showlegend=False
    )
    return fig.to_html(full_html=False)






def generate_all_measurements(input_lab_matrix, voxel_dims, ga):
    measurements = {
        "Amniotic Fluid Volume [cc]": (1, -1, -1, -1, -1, -1.6525,  98.534, -851.15, -0.5451, 38.784, -430.84, "Amniotic Fluid Volume"),
        "Placenta Volume [cc]": (2, -1, -1, -1, -1, -0.091, 41.116, -507.49, -0.2115, 16.766, -178.57, "Placenta Volume"),
        "Fetal Volume [cc]": (3, 4, -1, -1, -1,  4.4677, -107.26, 614.58, 0.6207, -20.43, 194.32, "Fetal Volume")
    }

    results = []
    for name, (label1, label2, label3, label4, label5, a, b, c, a5, b5, c5, title) in measurements.items():
        volume_cc = compute_volume(input_lab_matrix, label1, label2, label3, label4, label5, voxel_dims)
        mean = a * ga * ga + b * ga + c
        std_dev = a5 * ga * ga + b5 * ga + c5
        z_score = (volume_cc - mean) / std_dev
        percentile = norm.cdf(z_score) * 100
        centile_graph_html = create_centile_graph(ga, volume_cc, a, b, c, a5, b5, c5, title)
        results.append((name, volume_cc, centile_graph_html))
        
#    head / body ratio
    a = 0.0007
    b = -0.0568
    c = 1.5164
    a5 = 0.000043
    b5 = -0.003207
    c5 = 0.092266
    head_body_ratio = compute_head_body_ratio(input_lab_matrix, voxel_dims)
    mean = a * ga * ga + b * ga + c
    std_dev = a5 * ga * ga + b5 * ga + c5
    z_score = (head_body_ratio - mean) / std_dev
    percentile = norm.cdf(z_score) * 100
    oe_val = head_body_ratio / mean
    centile_graph_html = create_centile_graph_ratio(ga, head_body_ratio, a, b, c, a5, b5, c5, "Fetal Head/Body Ratio")
    results.append(("Fetal Head/Body Ratio", head_body_ratio, centile_graph_html))

#   fetal weight
    a = 4.4677
    b = -107.26
    c = 614.58
    a5 = 0.6207
    b5 = -20.43
    c5 = 194.32
    fetal_weight = compute_weight(input_lab_matrix, voxel_dims)
    mean = a * ga * ga + b * ga + c
    std_dev = a5 * ga * ga + b5 * ga + c5
    mean = 1.06 * mean + 0.12
    std_dev = 1.06 * std_dev + 0.12
    z_score = (fetal_weight - mean) / std_dev
    percentile = norm.cdf(z_score) * 100
    oe_val = fetal_weight / mean
    centile_graph_html = create_centile_graph_weight(ga, fetal_weight, a, b, c, a5, b5, c5, "Estimated Fetal Weight")
    results.append(("Estimated Fetal Weight [g]", fetal_weight, centile_graph_html))
        
    return results


def generate_table_measurements(input_lab_matrix, voxel_dims, ga):
    measurements = {
        "Amniotic Fluid Volume [cc]": (1, -1, -1, -1, -1, -1.6525,  98.534, -851.15, -0.5451, 38.784, -430.84, "Amniotic Fluid Volume"),
        "Placenta Volume [cc]": (2, -1, -1, -1, -1, -0.091, 41.116, -507.49, -0.2115, 16.766, -178.57, "Placenta Volume"),
        "Fetal Volume [cc]": (3, 4, -1, -1, -1,  4.4677, -107.26, 614.58, 0.6207, -20.43, 194.32, "Fetal Volume")
    }

    results = []
    for name, (label1, label2, label3, label4, label5, a, b, c, a5, b5, c5, title) in measurements.items():
        volume_cc = compute_volume(input_lab_matrix, label1, label2, label3, label4, label5, voxel_dims)
        mean = a * ga * ga + b * ga + c
        oe_val = volume_cc / mean
        std_dev = a5 * ga * ga + b5 * ga + c5
        z_score = (volume_cc - mean) / std_dev
        percentile = norm.cdf(z_score) * 100
        results.append((name, volume_cc, oe_val, percentile, z_score))
        
    #    head / body ratio
    a = 0.0007
    b = -0.0568
    c = 1.5164
    a5 = 0.000043
    b5 = -0.003207
    c5 = 0.092266
    head_body_ratio = compute_head_body_ratio(input_lab_matrix, voxel_dims)
    mean = a * ga * ga + b * ga + c
    std_dev = a5 * ga * ga + b5 * ga + c5
    z_score = (head_body_ratio - mean) / std_dev
    percentile = norm.cdf(z_score) * 100
    oe_val = head_body_ratio / mean
    results.append(("Fetal Head/Body Ratio", head_body_ratio, oe_val, percentile, z_score))

#   fetal weight
    a = 4.4677
    b = -107.26
    c = 614.58
    a5 = 0.6207
    b5 = -20.43
    c5 = 194.32
    fetal_weight = compute_weight(input_lab_matrix, voxel_dims)
    mean = a * ga * ga + b * ga + c
    std_dev = a5 * ga * ga + b5 * ga + c5
    mean = 1.06 * mean + 0.12
    std_dev = 1.06 * std_dev + 0.12
    z_score = (fetal_weight - mean) / std_dev
    percentile = norm.cdf(z_score) * 100
    oe_val = fetal_weight / mean
    results.append(("Estimated Fetal Weight [g]", fetal_weight, oe_val, percentile, z_score))
        
    return results



#========================================================================
#========================================================================


input_id = sys.argv[1]
input_ga = float(sys.argv[2])
input_scan_date = sys.argv[3]

input_img_nii_name = sys.argv[4]
input_lab_nii_name = sys.argv[5]

output_report_name_html = sys.argv[6]

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

voxel_dims = input_img_nii.header.get_zooms()


plot_measurements_results = generate_all_measurements(input_lab_matrix, voxel_dims, input_ga)
table_measurements_results = generate_table_measurements(input_lab_matrix, voxel_dims, input_ga)
uterus_image_b64 = plot_uterus_image(input_img_matrix, input_lab_matrix)

measurements_table = "".join([f"<tr><td>{name}</td><td>{volume_cc:.2f}</td><td>{oe_val:.2f}</td><td>{percentile:.2f}</td><td>{z_score:.2f}</td></tr>"
                              for name, volume_cc, oe_val, percentile, z_score in table_measurements_results])


print()
print("--------------------------------------------------------------")
print()
print(" ... ")
print()

# HTML content
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3-D T2W Fetal MRI: Automated Uterus Volumetry Report</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        .container {{
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            margin: 20px;
        }}
        .left-column {{
            flex: 1;
            padding: 20px;
        }}
        .right-column {{
            flex: 1;
            padding: 20px;
        }}
        .info-table {{
            width: 80%;
            margin-bottom: 20px;
        }}
        .info-table td, .info-table th {{
            padding: 5px;
        }}
        .uterus-image {{
            width: 100%;
            height: auto;
        }}
        .graph-container {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            grid-gap: 5px;
            margin-top: 10px;
        }}
        .graph {{
            width: 100%;
            height: auto;
        }}
    </style>
</head>
<body>
    <h1>3-D T2W Fetal MRI: Automated Uterus Volumetry Report</h1>
    <div class="container">
        <div class="left-column">
            <table class="info-table" border="1">
                <tr><td>Case ID:</td><td>{input_id}</td></tr>
                <tr><td>GA:</td><td>{input_ga} weeks</td></tr>
                <tr><td>Scan date:</td><td>{input_scan_date}</td></tr>
            </table>

            <img src="data:image/png;base64,{uterus_image_b64}" alt="3-D segmentation volumes" class="uterus-image">

            <table class="info-table" border="1">
                <tr><th>Measurement</th><th>Value</th><th>O/E</th><th>Percentile</th><th>Z-score</th></tr>
                {measurements_table}
            </table>
        </div>
        <div class="right-column graph-container">
            {"".join([f"<div id='plot_{i}'>{graph}</div>" for i, (_, _, graph) in enumerate(plot_measurements_results)])}
        </div>
    </div>
</body>
</html>
"""

# Save the HTML content to a file
with open(output_report_name_html, "w") as f:
    f.write(html_content)


print()
print("Output :",output_report_name_html)
print()
print("--------------------------------------------------------------")
print()
