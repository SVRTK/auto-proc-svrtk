
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

def compute_distance(input_lab_matrix, label1, label2, voxel_dims):
    landmark1_coords = np.array(np.where(input_lab_matrix == label1)).mean(axis=1)
    landmark2_coords = np.array(np.where(input_lab_matrix == label2)).mean(axis=1)
    distance_voxels = euclidean(landmark1_coords, landmark2_coords)
    distance_mm = distance_voxels * voxel_dims[0]  # Assuming isotropic voxels
    return distance_mm

def plot_brain_image(t2w_data, mask_data):

    landmarks = {}

    landmark_labels = {
        "skull_bpd": [1, 2],  # Labels for skull BPD
        "brain_bpd": [3, 4],  # Labels for brain BPD
        "left_atrial_diameter": [21, 22],  # Labels for left atrial diameter
        "right_atrial_diameter": [35, 36],  # Labels for right atrial diameter
        "cavum_diameter": [19, 20],  # Labels for cavum diameter
        "cerebellum_diameter": [9, 10],  # Labels for cerebellum diameter
        "skull_ofd": [5, 6],  # Labels for skull OFD
        "cc": [17, 18],  # Labels for CC
        "brain_ofd_right": [32, 33],  # Labels for brain OFD right
        "brain_ofd_left": [7, 8],  # Labels for brain OFD left
        "pons_width": [15, 16],  # Labels for pons width
        "vermian_width": [13, 14],  # Labels for vermian width
        "vermian_height": [11, 12]  # Labels for vermian height
    }

    for landmark, labels in landmark_labels.items():
        landmark_coords = [np.argwhere(mask_data == label) for label in labels]

        if any(coord.size == 0 for coord in landmark_coords):
            print(f"Landmarks {landmark} not found in the mask.")
            continue

        avg_coords = [np.mean(coords, axis=0) for coords in landmark_coords]
        landmarks[landmark] = avg_coords

    fig, axs = plt.subplots(2, 4, figsize=(16, 8))
    axs = axs.flatten()

    l_w = 3
    l_d = 20

    # Plot Axial Slices
    # 1. Skull BPD and Brain BPD
    axial_slice1 = t2w_data[:, :, int(landmarks['skull_bpd'][0][2])]
    axs[0].imshow(axial_slice1.T, cmap='gray', origin='lower')
    axs[0].scatter(landmarks['skull_bpd'][0][0], landmarks['skull_bpd'][0][1], c='red', s=l_d)
    axs[0].scatter(landmarks['skull_bpd'][1][0], landmarks['skull_bpd'][1][1], c='red', s=l_d)
    axs[0].plot([landmarks['skull_bpd'][0][0], landmarks['skull_bpd'][1][0]],
                [landmarks['skull_bpd'][0][1], landmarks['skull_bpd'][1][1]], 'r-', lw=l_w)
    axs[0].plot([landmarks['brain_bpd'][0][0], landmarks['brain_bpd'][1][0]],
                [landmarks['brain_bpd'][0][1], landmarks['brain_bpd'][1][1]], 'r-', lw=l_w)
    axs[0].set_title('Skull BPD & Maximal brain width')
    axs[0].axis('off')

    # 2. Left and Right Atrial Diameter
    axial_slice2 = t2w_data[:, :, int(landmarks['left_atrial_diameter'][0][2])]
    axs[1].imshow(axial_slice2.T, cmap='gray', origin='lower')
    axs[1].scatter(landmarks['left_atrial_diameter'][0][0], landmarks['left_atrial_diameter'][0][1], c='red', s=l_d)
    axs[1].scatter(landmarks['right_atrial_diameter'][0][0], landmarks['right_atrial_diameter'][0][1], c='red', s=l_d)
    axs[1].plot([landmarks['left_atrial_diameter'][0][0], landmarks['left_atrial_diameter'][1][0]],
                [landmarks['left_atrial_diameter'][0][1], landmarks['left_atrial_diameter'][1][1]], 'r-', lw=l_w)
    axs[1].plot([landmarks['right_atrial_diameter'][0][0], landmarks['right_atrial_diameter'][1][0]],
                [landmarks['right_atrial_diameter'][0][1], landmarks['right_atrial_diameter'][1][1]], 'r-', lw=l_w)
    axs[1].set_title('Right & Left Atrial Diameter')
    axs[1].axis('off')

    # 3. Cavum Diameter
    axial_slice3 = t2w_data[:, :, int(landmarks['cavum_diameter'][0][2])]
    axs[2].imshow(axial_slice3.T, cmap='gray', origin='lower')
    axs[2].scatter(landmarks['cavum_diameter'][0][0], landmarks['cavum_diameter'][0][1], c='red', s=l_d)
    axs[2].scatter(landmarks['cavum_diameter'][1][0], landmarks['cavum_diameter'][1][1], c='red', s=l_d)
    axs[2].plot([landmarks['cavum_diameter'][0][0], landmarks['cavum_diameter'][1][0]],
                [landmarks['cavum_diameter'][0][1], landmarks['cavum_diameter'][1][1]], 'r-', lw=l_w)
    axs[2].set_title('Cavum Diameter')
    axs[2].axis('off')

    # 4. Cerebellum Diameter
    axial_slice4 = t2w_data[:, :, int(landmarks['cerebellum_diameter'][0][2])]
    axs[3].imshow(axial_slice4.T, cmap='gray', origin='lower')
    axs[3].scatter(landmarks['cerebellum_diameter'][0][0], landmarks['cerebellum_diameter'][0][1], c='red', s=l_d)
    axs[3].scatter(landmarks['cerebellum_diameter'][1][0], landmarks['cerebellum_diameter'][1][1], c='red', s=l_d)
    axs[3].plot([landmarks['cerebellum_diameter'][0][0], landmarks['cerebellum_diameter'][1][0]],
                [landmarks['cerebellum_diameter'][0][1], landmarks['cerebellum_diameter'][1][1]], 'r-', lw=l_w)
    axs[3].set_title('Transcerebellar Diameter')
    axs[3].axis('off')

    # Plot Sagittal Slices
    # 5. Skull OFD and CC
    sagittal_slice1 = t2w_data[int(landmarks['skull_ofd'][0][0]), :, :]
    axs[4].imshow(sagittal_slice1.T, cmap='gray', origin='lower')
    axs[4].scatter(landmarks['skull_ofd'][0][1], landmarks['skull_ofd'][0][2], c='red', s=l_d)
    axs[4].scatter(landmarks['cc'][0][1], landmarks['cc'][0][2], c='red', s=30)
    axs[4].plot([landmarks['skull_ofd'][0][1], landmarks['skull_ofd'][1][1]],
                [landmarks['skull_ofd'][0][2], landmarks['skull_ofd'][1][2]], 'r-', lw=l_w)
    axs[4].plot([landmarks['cc'][0][1], landmarks['cc'][1][1]],
                [landmarks['cc'][0][2], landmarks['cc'][1][2]], 'r-', lw=l_w)
    axs[4].set_title('Skull OFD & CC')
    axs[4].axis('off')

    # 6. Brain OFD Right
    sagittal_slice2 = t2w_data[int(landmarks['brain_ofd_right'][0][0]), :, :]
    axs[5].imshow(sagittal_slice2.T, cmap='gray', origin='lower')
    axs[5].scatter(landmarks['brain_ofd_right'][0][1], landmarks['brain_ofd_right'][0][2], c='red', s=l_d)
    axs[5].scatter(landmarks['brain_ofd_right'][1][1], landmarks['brain_ofd_right'][1][2], c='red', s=l_d)
    axs[5].plot([landmarks['brain_ofd_right'][0][1], landmarks['brain_ofd_right'][1][1]],
                [landmarks['brain_ofd_right'][0][2], landmarks['brain_ofd_right'][1][2]], 'r-', lw=l_w)
    axs[5].set_title('Brain OFD Right')
    axs[5].axis('off')

    # 7. Brain OFD Left
    sagittal_slice3 = t2w_data[int(landmarks['brain_ofd_left'][0][0]), :, :]
    axs[6].imshow(sagittal_slice3.T, cmap='gray', origin='lower')
    axs[6].scatter(landmarks['brain_ofd_left'][0][1], landmarks['brain_ofd_left'][0][2], c='red', s=l_d)
    axs[6].scatter(landmarks['brain_ofd_left'][1][1], landmarks['brain_ofd_left'][1][2], c='red', s=l_d)
    axs[6].plot([landmarks['brain_ofd_left'][0][1], landmarks['brain_ofd_left'][1][1]],
                [landmarks['brain_ofd_left'][0][2], landmarks['brain_ofd_left'][1][2]], 'r-', lw=l_w)
    axs[6].set_title('Brain OFD Left')
    axs[6].axis('off')

    # 8. Pons Width, Vermian Width & Height
    sagittal_slice4 = t2w_data[int(landmarks['pons_width'][0][0]), :, :]
    axs[7].imshow(sagittal_slice4.T, cmap='gray', origin='lower')
    axs[7].scatter(landmarks['pons_width'][0][1], landmarks['pons_width'][0][2], c='red', s=l_d)
    axs[7].scatter(landmarks['vermian_width'][0][1], landmarks['vermian_width'][0][2], c='red', s=l_d)
    axs[7].scatter(landmarks['vermian_height'][0][1], landmarks['vermian_height'][0][2], c='red', s=l_d)
    axs[7].plot([landmarks['pons_width'][0][1], landmarks['pons_width'][1][1]],
                [landmarks['pons_width'][0][2], landmarks['pons_width'][1][2]], 'r-', lw=l_w)
    axs[7].plot([landmarks['vermian_width'][0][1], landmarks['vermian_width'][1][1]],
                [landmarks['vermian_width'][0][2], landmarks['vermian_width'][1][2]], 'r-', lw=l_w)
    axs[7].plot([landmarks['vermian_height'][0][1], landmarks['vermian_height'][1][1]],
                [landmarks['vermian_height'][0][2], landmarks['vermian_height'][1][2]], 'r-', lw=l_w)
    axs[7].set_title('Pons Width, Vermian Width & Height')
    axs[7].axis('off')

    # Adjust layout
    plt.tight_layout()

    # Save the figure to a BytesIO object
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_b64 = base64.b64encode(buf.read()).decode('utf-8')  # Encode to base64
    plt.close(fig)  # Close the figure to avoid display

    return image_b64

def create_centile_graph(ga, computed_value, a, b, c, a5, b5, title):
    x = np.linspace(20, 40, 100)
    y = a * x * x + b * x + c
    y5 = y - 1.645 * (a5 * x + b5)
    y95 = y + 1.645 * (a5 * x + b5)

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
        yaxis_title="distance [mm]",
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(gridcolor='lightgrey'),
        yaxis=dict(gridcolor='lightgrey'),
        showlegend=False
    )
    return fig.to_html(full_html=False)

def generate_all_measurements(input_lab_matrix, voxel_dims, ga):
    measurements = {
        "Skull BPD": (1, 2, -0.0527, 5.7605, -46.436, 0.0895, 0.1414, "Skull BPD"),
        "Skull OFD": (5, 6, -0.0984, 8.8526, -81.605, 0.1511, -1.3192, "Skull OFD"),
        "Maximal brain width": (3, 4, 0.016, 1.763, -0.9597, 0.1308, -1.32, "Maximal brain width"),
        "Brain OFD Right": (32, 33, -0.0781, 7.7234, -75.3, 0.1277, -0.9298, "Brain OFD Right"),
        "Brain OFD Left": (7, 8, -0.0781, 7.7234, -75.3, 0.1277, -0.9298, "Brain OFD Left"),
        "Transcerebellar Diameter": (9, 10, 0.0051, 1.5165, -14.584, 0.0343, 0.415, "Transcerebellar Diameter"),
        "Vermian Height": (11, 12, -0.0138, 1.6136, -20.065, 0.0354, -0.1869, "Vermian Height"),
        "Vermian Width": (13, 14, -0.0089, 1.1119, -14.637, 0.0447, -0.5126, "Vermian Width"),
        "Pons Width": (15, 16, 0.002, 0.3144, -1.2147, 0.0124, 0.261, "Pons Width"),
        "Corpus Callosum Length": (17, 18, -0.0687, 5.1529, -57.904, 0.0274, 0.4763, "Corpus Callosum Length"),
        "Cavum Septum Pellucidum Width": (19, 20, -0.0156, 0.9472, -6.6953, 0.053, -0.4388, "Cavum Septum Pellucidum Width"),
        "Atrial Diameter Right": (35, 36, 0.0078, -0.5216, 15.374, 0.0264, 0.5152, "Atrial Diameter Right"),
        "Atrial Diameter Left": (21, 22, 0.0078, -0.5216, 15.374, 0.0264, 0.5152, "Atrial Diameter Left")
    }

    results = []
    for name, (label1, label2, a, b, c, a5, b5, title) in measurements.items():
        distance_mm = compute_distance(input_lab_matrix, label1, label2, voxel_dims)
        # percentile = compute_percentile(distance_mm, a, b, c)
        mean = np.polyval([a, b, c], ga)
        std_dev = np.polyval([a5, b5], ga)
        z_score = (distance_mm - mean) / std_dev
        percentile = norm.cdf(z_score) * 100
        centile_graph_html = create_centile_graph(ga, distance_mm, a, b, c, a5, b5, title)
        results.append((name, distance_mm, centile_graph_html))
    return results


def generate_table_measurements(input_lab_matrix, voxel_dims, ga):
    measurements = {
        "Skull BPD": (1, 2, -0.0527, 5.7605, -46.436, 0.0895, 0.1414, "Skull BPD"),
        "Skull OFD": (5, 6, -0.0984, 8.8526, -81.605, 0.1511, -1.3192, "Skull OFD"),
        "Maximal brain width": (3, 4, 0.016, 1.763, -0.9597, 0.1308, -1.32, "Maximal brain width"),
        "Brain OFD Right": (32, 33, -0.0781, 7.7234, -75.3, 0.1277, -0.9298, "Brain OFD Right"),
        "Brain OFD Left": (7, 8, -0.0781, 7.7234, -75.3, 0.1277, -0.9298, "Brain OFD Left"),
        "Transcerebellar Diameter": (9, 10, 0.0051, 1.5165, -14.584, 0.0343, 0.415, "Transcerebellar Diameter"),
        "Vermian Height": (11, 12, -0.0138, 1.6136, -20.065, 0.0354, -0.1869, "Vermian Height"),
        "Vermian Width": (13, 14, -0.0089, 1.1119, -14.637, 0.0447, -0.5126, "Vermian Width"),
        "Pons Width": (15, 16, 0.002, 0.3144, -1.2147, 0.0124, 0.261, "Pons Width"),
        "Corpus Callosum Length": (17, 18, -0.0687, 5.1529, -57.904, 0.0274, 0.4763, "Corpus Callosum Length"),
        "Cavum Septum Pellucidum Width": (19, 20, -0.0156, 0.9472, -6.6953, 0.053, -0.4388, "Cavum Septum Pellucidum Width"),
        "Atrial Diameter Right": (35, 36, 0.0078, -0.5216, 15.374, 0.0264, 0.5152, "Atrial Diameter Right"),
        "Atrial Diameter Left": (21, 22, 0.0078, -0.5216, 15.374, 0.0264, 0.5152, "Atrial Diameter Left")
    }

    results = []
    for name, (label1, label2, a, b, c, a5, b5, title) in measurements.items():
        distance_mm = compute_distance(input_lab_matrix, label1, label2, voxel_dims)
        # percentile = compute_percentile(distance_mm, a, b, c)  # Ensure you implement this function
        mean = np.polyval([a, b, c], ga)
        std_dev = np.polyval([0, a5, b5], ga)
        z_score = (distance_mm - mean) / std_dev
        percentile = norm.cdf(z_score) * 100
        results.append((name, distance_mm, percentile, z_score))
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

measurements_table = "".join([f"<tr><td>{name}</td><td>{distance_mm:.2f}</td><td>{percentile:.2f}</td><td>{z_score:.2f}</td></tr>"
                              for name, distance_mm, percentile, z_score in table_measurements_results])


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
    <title>3D T2w Fetal Brain MRI: Automated Biometry Report</title>
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
    <h1>3D T2w Fetal Brain MRI: Automated Biometry Report</h1>
    <div class="container">
        <div class="left-column">
            <table class="info-table" border="1">
                <tr><td>Case ID:</td><td>{input_id}</td></tr>
                <tr><td>GA:</td><td>{input_ga} weeks</td></tr>
                <tr><td>Scan date:</td><td>{input_scan_date}</td></tr>
            </table>

            <img src="data:image/png;base64,{brain_image_b64}" alt="3D landmark measurements" class="brain-image">

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
