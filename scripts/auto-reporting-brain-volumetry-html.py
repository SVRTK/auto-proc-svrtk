
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

def compute_volume(input_lab_matrix, label1, label2, label3, label4, voxel_dims):

    landmark1_coords = np.count_nonzero(input_lab_matrix == label1)
    landmark2_coords = np.count_nonzero(input_lab_matrix == label2)
    landmark3_coords = np.count_nonzero(input_lab_matrix == label3)
    landmark4_coords = np.count_nonzero(input_lab_matrix == label4)

    volume_cc = (landmark1_coords + landmark2_coords + landmark3_coords + landmark4_coords) * voxel_dims[0] * voxel_dims[1] * voxel_dims[2]  # Assuming isotropic voxels

    volume_cc = volume_cc / 1000

    return volume_cc

def plot_brain_image(t2w_data, mask_data):


    fig, axs = plt.subplots(2, 5, figsize=(20, 10))
    axs = axs.flatten()

    x, y, z = t2w_data.shape
    a = 0.4

    axial_t2w_slice1 = t2w_data[:, :, round(z*0.3)]
    axial_t2w_slice2 = t2w_data[:, :, round(z*0.4)]
    axial_t2w_slice3 = t2w_data[:, :, round(z*0.5)]
    axial_t2w_slice4 = t2w_data[:, :, round(z*0.6)]
    axial_t2w_slice5 = t2w_data[:, :, round(z*0.7)]

    axial_lab_slice1 = mask_data[:, :, round(z*0.3)]
    axial_lab_slice2 = mask_data[:, :, round(z*0.4)]
    axial_lab_slice3 = mask_data[:, :, round(z*0.5)]
    axial_lab_slice4 = mask_data[:, :, round(z*0.6)]
    axial_lab_slice5 = mask_data[:, :, round(z*0.7)]

    i = 0
    axs[i].imshow(axial_t2w_slice1.T, cmap='gray', origin='lower')
    # axs[i].imshow(axial_lab_slice1.T, cmap='jet', origin='lower', alpha=a)
    axs[i].axis('off')

    i = 1
    axs[i].imshow(axial_t2w_slice2.T, cmap='gray', origin='lower')
    # axs[i].imshow(axial_lab_slice2.T, cmap='jet', origin='lower', alpha=a)
    axs[i].axis('off')

    i = 2
    axs[i].imshow(axial_t2w_slice3.T, cmap='gray', origin='lower')
    # axs[i].imshow(axial_lab_slice3.T, cmap='jet', origin='lower', alpha=a)
    axs[i].axis('off')

    i = 3
    axs[i].imshow(axial_t2w_slice4.T, cmap='gray', origin='lower')
    # axs[i].imshow(axial_lab_slice4.T, cmap='jet', origin='lower', alpha=a)
    axs[i].axis('off')

    i = 4
    axs[i].imshow(axial_t2w_slice5.T, cmap='gray', origin='lower')
    # axs[i].imshow(axial_lab_slice5.T, cmap='jet', origin='lower', alpha=a)
    axs[i].axis('off')

    i = 5
    axs[i].imshow(axial_t2w_slice1.T, cmap='gray', origin='lower')
    axs[i].imshow(axial_lab_slice1.T, cmap='jet', origin='lower', alpha=a)
    axs[i].axis('off')

    i = 6
    axs[i].imshow(axial_t2w_slice2.T, cmap='gray', origin='lower')
    axs[i].imshow(axial_lab_slice2.T, cmap='jet', origin='lower', alpha=a)
    axs[i].axis('off')

    i = 7
    axs[i].imshow(axial_t2w_slice3.T, cmap='gray', origin='lower')
    axs[i].imshow(axial_lab_slice3.T, cmap='jet', origin='lower', alpha=a)
    axs[i].axis('off')

    i = 8
    axs[i].imshow(axial_t2w_slice4.T, cmap='gray', origin='lower')
    axs[i].imshow(axial_lab_slice4.T, cmap='jet', origin='lower', alpha=a)
    axs[i].axis('off')

    i = 9
    axs[i].imshow(axial_t2w_slice5.T, cmap='gray', origin='lower')
    axs[i].imshow(axial_lab_slice5.T, cmap='jet', origin='lower', alpha=a)
    axs[i].axis('off')


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

def generate_all_measurements(input_lab_matrix, voxel_dims, ga):
    measurements = {
        "External CSF": (1, 2, -1, -1, -0.23580, 17.9930, -250.0000, 0.01105, -0.00364, 0.92868, "External CSF"),
        "Cortical GM": (3, 4, -1, -1, 0.30520, -11.82800, 123.0000, 0.01647, -0.47701, 3.76905, "Cortical GM"),
        "Fetal WM": (5, 6, -1, -1, 0.02230, 7.34710, -145.28000, 0.0098622, 0.10410, -3.9009446, "Fetal WM"),
        "Deep GM": (14, 15, 16, 17, 0.0149, -0.0475, -3.5148, -0.0005329, 0.0765574, -1.1757984, "Deep GM"),
        "Lateral ventricle Left": (7, -1, -1, -1, -0.00329, 0.31120, -3.99901, -0.00451, 0.29420, -3.99013, "Lateral ventricle Left"),
        "Lateral ventricle Right": (8, -1, -1, -1, -0.00329, 0.31120, -3.99901, -0.00451, 0.29420, -3.99013, "Lateral ventricle Right"),
        "Cavum": (9, -1, -1, -1, -0.0044, 0.2808, -3.76, 0.00014, 0.00304, 0.001, "Cavum"),
        "Brainstem": (10, -1, -1, -1, 0.0038, 0.086, -2.1428, -0.0002952, 0.0340193, -0.4995123, "Brainstem"),
        "Cerebellum and vermis": (11, 12, 13, -1, 0.0451, -1.6575, 16.314, 0.0011411, 0.0112348, -0.5235345, "Cerebellum and vermis"),
        "Third ventricle": (18, -1, -1, -1, -0.00016, 0.02617, -0.45036, 0.000144, -0.0054636, 0.06618816, "Third ventricle"),
        "Fourth ventricle": (19, -1, -1, -1, 0.00044, -0.01590, 0.18471, 0.000117, -0.004439175, 0.05377788, "Fourth ventricle")
    }

    results = []
    for name, (label1, label2, label3, label4, a, b, c, a5, b5, c5, title) in measurements.items():
        volume_cc = compute_volume(input_lab_matrix, label1, label2, label3, label4, voxel_dims)
        mean = np.polyval([a, b, c], ga)
        std_dev = np.polyval([a5, b5, c5], ga)
        z_score = (volume_cc - mean) / std_dev
        percentile = norm.cdf(z_score) * 100
        centile_graph_html = create_centile_graph(ga, volume_cc, a, b, c, a5, b5, c5, title)
        results.append((name, volume_cc, centile_graph_html))
    return results


def generate_table_measurements(input_lab_matrix, voxel_dims, ga):
    measurements = {
        "External CSF": (1, 2, -1, -1, -0.23580, 17.9930, -250.0000, 0.01105, -0.00364, 0.92868, "External CSF"),
        "Cortical GM": (3, 4, -1, -1, 0.30520, -11.82800, 123.0000, 0.01647, -0.47701, 3.76905, "Cortical GM"),
        "Fetal WM": (5, 6, -1, -1, 0.02230, 7.34710, -145.28000, 0.0098622, 0.10410, -3.9009446, "Fetal WM"),
        "Deep GM": (14, 15, 16, 17, 0.0149, -0.0475, -3.5148, -0.0005329, 0.0765574, -1.1757984, "Deep GM"),
        "Lateral ventricle Left": (7, -1, -1, -1, -0.00329, 0.31120, -3.99901, -0.00451, 0.29420, -3.99013, "Lateral ventricle Left"),
        "Lateral ventricle Right": (8, -1, -1, -1, -0.00329, 0.31120, -3.99901, -0.00451, 0.29420, -3.99013, "Lateral ventricle Right"),
        "Cavum": (9, -1, -1, -1, -0.0044, 0.2808, -3.76, 0.00014, 0.00304, 0.001, "Cavum"),
        "Brainstem": (10, -1, -1, -1, 0.0038, 0.086, -2.1428, -0.0002952, 0.0340193, -0.4995123, "Brainstem"),
        "Cerebellum and vermis": (11, 12, 13, -1, 0.0451, -1.6575, 16.314, 0.0011411, 0.0112348, -0.5235345, "Cerebellum and vermis"),
        "Third ventricle": (18, -1, -1, -1, -0.00016, 0.02617, -0.45036, 0.000144, -0.0054636, 0.06618816, "Third ventricle"),
        "Fourth ventricle": (19, -1, -1, -1, 0.00044, -0.01590, 0.18471, 0.000117, -0.004439175, 0.05377788, "Fourth ventricle")
    }

    results = []
    for name, (label1, label2, label3, label4, a, b, c, a5, b5, c5, title) in measurements.items():
        volume_cc = compute_volume(input_lab_matrix, label1, label2, label3, label4, voxel_dims)
        mean = np.polyval([a, b, c], ga)
        std_dev = np.polyval([a5, b5, c5], ga)
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
brain_image_b64 = plot_brain_image(input_img_matrix, input_lab_matrix)

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
    <title>3D T2w Fetal Brain MRI: Automated Volumetry Report</title>
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
        .brain-image {{
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
    <h1>3D T2w Fetal Brain MRI: Automated Volumetry Report</h1>
    <div class="container">
        <div class="left-column">
            <table class="info-table" border="1">
                <tr><td>Case ID:</td><td>{input_id}</td></tr>
                <tr><td>GA:</td><td>{input_ga} weeks</td></tr>
                <tr><td>Scan date:</td><td>{input_scan_date}</td></tr>
            </table>

            <img src="data:image/png;base64,{brain_image_b64}" alt="3D segmentation volumes" class="brain-image">

            <table class="info-table" border="1">
                <tr><th>Measurement</th><th>Distance [mm]</th><th>Percentile</th><th>Z-score</th></tr>
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
