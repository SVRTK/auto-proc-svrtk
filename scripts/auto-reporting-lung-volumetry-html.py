
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


#========================================================================
#========================================================================

def compute_volume(input_lab_matrix, label1, label2, label3, label4, label5, voxel_dims):

    landmark1_coords = np.count_nonzero(input_lab_matrix == label1)
    landmark2_coords = np.count_nonzero(input_lab_matrix == label2)
    landmark3_coords = np.count_nonzero(input_lab_matrix == label3)
    landmark4_coords = np.count_nonzero(input_lab_matrix == label4)
    landmark5_coords = np.count_nonzero(input_lab_matrix == label5)

    volume_cc = (landmark1_coords + landmark2_coords + landmark3_coords + landmark4_coords + landmark5_coords) * voxel_dims[0] * voxel_dims[1] * voxel_dims[2]  # Assuming isotropic voxels

    volume_cc = volume_cc / 1000

    return volume_cc
    

def plot_body_image(t2w_data, mask_data):


    fig, axs = plt.subplots(2, 5, figsize=(20, 10))
    axs = axs.flatten()

    x, y, z = t2w_data.shape
    a = 0.4

    coronal_t2w_slice1 = t2w_data[:, round(y*0.4), :]
    coronal_t2w_slice2 = t2w_data[:, round(y*0.45), :]
    coronal_t2w_slice3 = t2w_data[:, round(y*0.5), :]
    coronal_t2w_slice4 = t2w_data[:, round(y*0.55), :]
    coronal_t2w_slice5 = t2w_data[:, round(y*0.6), :]

    coronal_lab_slice1 = mask_data[:, round(y*0.4), :]
    coronal_lab_slice2 = mask_data[:, round(y*0.45), :]
    coronal_lab_slice3 = mask_data[:, round(y*0.5), :]
    coronal_lab_slice4 = mask_data[:, round(y*0.55), :]
    coronal_lab_slice5 = mask_data[:, round(y*0.6), :]


    i = 0
    axs[i].imshow(coronal_t2w_slice1.T, cmap='gray', origin='lower')
    # axs[i].imshow(coronal_lab_slice1.T, cmap='jet', origin='lower', alpha=a)
    axs[i].axis('off')

    i = 1
    axs[i].imshow(coronal_t2w_slice2.T, cmap='gray', origin='lower')
    # axs[i].imshow(coronal_lab_slice2.T, cmap='jet', origin='lower', alpha=a)
    axs[i].axis('off')

    i = 2
    axs[i].imshow(coronal_t2w_slice3.T, cmap='gray', origin='lower')
    # axs[i].imshow(coronal_lab_slice3.T, cmap='jet', origin='lower', alpha=a)
    axs[i].axis('off')

    i = 3
    axs[i].imshow(coronal_t2w_slice4.T, cmap='gray', origin='lower')
    # axs[i].imshow(coronal_lab_slice4.T, cmap='jet', origin='lower', alpha=a)
    axs[i].axis('off')

    i = 4
    axs[i].imshow(coronal_t2w_slice5.T, cmap='gray', origin='lower')
    # axs[i].imshow(coronal_lab_slice5.T, cmap='jet', origin='lower', alpha=a)
    axs[i].axis('off')

    i = 5
    axs[i].imshow(coronal_t2w_slice1.T, cmap='gray', origin='lower')
    axs[i].imshow(coronal_lab_slice1.T, cmap='jet', origin='lower', alpha=a)
    axs[i].axis('off')

    i = 6
    axs[i].imshow(coronal_t2w_slice2.T, cmap='gray', origin='lower')
    axs[i].imshow(coronal_lab_slice2.T, cmap='jet', origin='lower', alpha=a)
    axs[i].axis('off')

    i = 7
    axs[i].imshow(coronal_t2w_slice3.T, cmap='gray', origin='lower')
    axs[i].imshow(coronal_lab_slice3.T, cmap='jet', origin='lower', alpha=a)
    axs[i].axis('off')

    i = 8
    axs[i].imshow(coronal_t2w_slice4.T, cmap='gray', origin='lower')
    axs[i].imshow(coronal_lab_slice4.T, cmap='jet', origin='lower', alpha=a)
    axs[i].axis('off')

    i = 9
    axs[i].imshow(coronal_t2w_slice5.T, cmap='gray', origin='lower')
    axs[i].imshow(coronal_lab_slice5.T, cmap='jet', origin='lower', alpha=a)
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


def create_centile_graph(ga, computed_value, a, b, a5, b5, title):
    x = np.linspace(20, 40, 100)
    y = a * (x ** b)

    y5 = y - 1.645 * (a5 * (x ** b5))
    y95 = y + 1.645 * (a5 * (x ** b5))

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

def generate_all_measurements(input_lab_matrix, voxel_dims, ga):
    measurements = {
        "Lelf Lung": (1, 2, -1, -1, -1, 0.0002223,    3.3987223,    0.0000036,    4.0821588, "Lelf Lung"),
        "Right Lung": (3, 4, 5, -1, -1, 0.0002452,    3.442938,      0.0000066,    3.9458311, "Right Lung"),
        "Total Lungs": (1, 2, 3, 4, 5,  0.0004642,    3.4252335,    0.0000069,    4.1024115, "Total Lungs"),
    }

    results = []
    for name, (label1, label2, label3, label4, label5, a, b, a5, b5, title) in measurements.items():
        volume_cc = compute_volume(input_lab_matrix, label1, label2, label3, label4, label5, voxel_dims)
        mean = a * (ga ** b)
        std_dev = a5 * (ga ** b5)
        z_score = (volume_cc - mean) / std_dev
        percentile = norm.cdf(z_score) * 100
        centile_graph_html = create_centile_graph(ga, volume_cc, a, b, a5, b5, title)
        results.append((name, volume_cc, centile_graph_html))
    return results


def generate_table_measurements(input_lab_matrix, voxel_dims, ga):
    measurements = {
        "Lelf Lung": (1, 2, -1, -1, -1, 0.0002223,    3.3987223,    0.0000036,    4.0821588, "Lelf Lung"),
        "Right Lung": (3, 4, 5, -1, -1, 0.0002452,    3.442938,      0.0000066,    3.9458311, "Right Lung"),
        "Total Lungs": (1, 2, 3, 4, 5,  0.0004642,    3.4252335,    0.0000069,    4.1024115, "Total Lungs"),
    }

    results = []
    for name, (label1, label2, label3, label4, label5, a, b, a5, b5, title) in measurements.items():
        volume_cc = compute_volume(input_lab_matrix, label1, label2, label3, label4, label5, voxel_dims)
        mean = a * (ga ** b)
        std_dev = a5 * (ga ** b5)
        z_score = (volume_cc - mean) / std_dev
        percentile = norm.cdf(z_score) * 100
        results.append((name, volume_cc, percentile, z_score))
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
body_image_b64 = plot_body_image(input_img_matrix, input_lab_matrix)

measurements_table = "".join([f"<tr><td>{name}</td><td>{volume_cc:.2f}</td><td>{percentile:.2f}</td><td>{z_score:.2f}</td></tr>"
                              for name, volume_cc, percentile, z_score in table_measurements_results])


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
    <title>3D T2w Fetal Body MRI: Automated Lung Volumetry Report</title>
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
        .body-image {{
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
    <h1>3D T2w Fetal Body MRI: Automated Lung Volumetry Report</h1>
    <div class="container">
        <div class="left-column">
            <table class="info-table" border="1">
                <tr><td>Case ID:</td><td>{input_id}</td></tr>
                <tr><td>GA:</td><td>{input_ga} weeks</td></tr>
                <tr><td>Scan date:</td><td>{input_scan_date}</td></tr>
            </table>

            <img src="data:image/png;base64,{body_image_b64}" alt="3D segmentation volumes" class="body-image">

            <table class="info-table" border="1">
                <tr><th>Measurement</th><th>Volume [cc]</th><th>Percentile</th><th>Z-score</th></tr>
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
