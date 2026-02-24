#!/usr/bin/env python3
"""
gyrification_metrics.py

Compute GI proxy + quick surface metrics from fetal cortical label segmentations
and output BOTH:
  1) wide CSV (1 row per subject, columns = "{roi}__{metric}")
  2) long CSV (QC-friendly, 21 rows per subject)

ROIs (21 total):
  - label_1 ... label_12
  - left_hemisphere_combined   (1,3,5,7,9,11)  [mask-merged]
  - right_hemisphere_combined  (2,4,6,8,10,12) [mask-merged]
  - full_cortex_combined       (1..12)         [mask-merged]
  - frontal_lobe_mean          mean of metrics from labels (1,2)
  - parietal_lobe_mean         mean of metrics from labels (3,4)
  - occipital_lobe_mean        mean of metrics from labels (5,6)
  - insular_lobe_mean          mean of metrics from labels (7,8)
  - temporal_lobe_mean         mean of metrics from labels (9,10)
  - cingulate_lobe_mean        mean of metrics from labels (11,12)

GI proxy:
  GI = pial_surface_area / outer_hull_surface_area

Where:
  - pial_surface_area: surface area of ROI mask (marching cubes)
  - outer_hull_surface_area: surface area after morphological closing
    (practical outer hull proxy smoothing sulci)

Usage:
  python3 gyrification_metrics.py OUT_WIDE.csv N file1.nii.gz file2.nii.gz ... fileN.nii.gz

Example:
  python3 gyrification_metrics.py test-gi-dhcp.csv 300 dhcp-labels/sub*nii.gz

Outputs:
  - OUT_WIDE.csv (wide)
  - OUT_WIDE.long.csv (long)

Dependencies:
  pip install nibabel numpy scipy scikit-image pandas
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import nibabel as nib
from scipy import ndimage
from skimage import measure


LEFT_LABELS  = [1, 3, 5, 7, 9, 11]
RIGHT_LABELS = [2, 4, 6, 8, 10, 12]
LABELS_1_12  = list(range(1, 13))

# Lobe-wise simple averages of metrics (NOT mask-merged)
LOBE_PAIRS = {
    "frontal_lobe_mean":    (1, 2),
    "parietal_lobe_mean":   (3, 4),
    "occipital_lobe_mean":  (5, 6),
    "insular_lobe_mean":    (7, 8),
    "temporal_lobe_mean":   (9, 10),
    "cingulate_lobe_mean":  (11, 12),
}

# Output metric columns (used for ordering + wide pivot)
METRIC_COLS = [
    "voxels",
    "volume_mm3",
    "surface_area_mm2",
    "hull_surface_area_mm2",
    "gyrification_index",
    "surface_to_volume_mm-1",
    "sphericity",
]

# Deterministic ROI order (wide columns grouped accordingly)
ROI_ORDER = (
    [f"label_{i}" for i in range(1, 13)]
    + ["left_hemisphere_combined", "right_hemisphere_combined", "full_cortex_combined"]
    + list(LOBE_PAIRS.keys())
)


def voxel_sizes_mm(affine: np.ndarray) -> np.ndarray:
    """Voxel spacing (mm) from affine columns."""
    return np.linalg.norm(affine[:3, :3], axis=0)


def voxel_volume_mm3(spacing_xyz: np.ndarray) -> float:
    return float(np.prod(spacing_xyz))


def surface_area_mm2(mask_xyz: np.ndarray, spacing_xyz: np.ndarray) -> float:
    """
    Surface area (mm^2) via marching cubes.

    nibabel arrays are typically indexed (X,Y,Z).
    We transpose to (Z,Y,X) and pass spacing (sz,sy,sx).
    """
    if mask_xyz.sum() < 10:
        return 0.0

    m_zyx = mask_xyz.astype(np.uint8).transpose(2, 1, 0)  # (Z,Y,X)
    verts, faces, _, _ = measure.marching_cubes(
        m_zyx, level=0.5,
        spacing=(float(spacing_xyz[2]), float(spacing_xyz[1]), float(spacing_xyz[0]))
    )
    return float(measure.mesh_surface_area(verts, faces))


def closing_hull(mask_xyz: np.ndarray, spacing_xyz: np.ndarray, closing_radius_mm: float) -> np.ndarray:
    """
    Outer hull proxy by morphological closing with a 3D structuring element.
    For isotropic 0.5mm, closing_radius_mm=2.0 -> ~4 vox radius.
    """
    if mask_xyz.sum() < 10:
        return mask_xyz

    min_step = float(np.min(spacing_xyz))
    r = max(1, int(np.round(closing_radius_mm / max(min_step, 1e-6))))
    structure = np.ones((2 * r + 1, 2 * r + 1, 2 * r + 1), dtype=bool)
    return ndimage.binary_closing(mask_xyz, structure=structure)


def compute_metrics(mask_xyz: np.ndarray, spacing_xyz: np.ndarray, closing_radius_mm: float) -> dict:
    """Compute metrics for a binary ROI mask."""
    vvox = int(mask_xyz.sum())
    vmm3 = float(vvox) * voxel_volume_mm3(spacing_xyz)

    sa = surface_area_mm2(mask_xyz, spacing_xyz)

    hull = closing_hull(mask_xyz, spacing_xyz, closing_radius_mm=closing_radius_mm)
    hull_sa = surface_area_mm2(hull, spacing_xyz)

    gi = (sa / hull_sa) if hull_sa > 0 else np.nan
    s2v = (sa / vmm3) if vmm3 > 0 else np.nan
    sphericity = ((np.pi ** (1/3)) * ((6.0 * vmm3) ** (2/3)) / sa) if sa > 0 else np.nan

    return {
        "voxels": vvox,
        "volume_mm3": vmm3,
        "surface_area_mm2": sa,
        "hull_surface_area_mm2": hull_sa,
        "gyrification_index": gi,
        "surface_to_volume_mm-1": s2v,
        "sphericity": sphericity,
    }


def process_file(seg_path: Path, closing_radius_mm: float) -> list[dict]:
    """
    Returns list of 21 dict rows for one subject in LONG format:
      id, roi, label, metrics...
    """
    img = nib.load(str(seg_path))
    data = np.asarray(img.get_fdata(dtype=np.float32))
    labels = np.rint(data).astype(np.int16)

    spacing = voxel_sizes_mm(img.affine)
    file_id = seg_path.name

    rows = []
    label_rows = {}

    # --- 12 individual labels
    for lab in LABELS_1_12:
        m = (labels == lab)
        met = compute_metrics(m, spacing, closing_radius_mm)
        row = {"id": file_id, "roi": f"label_{lab}", "label": lab, **met}
        rows.append(row)
        label_rows[lab] = row

    # --- 3 combined masks (geometry recomputed on merged masks)
    left = np.isin(labels, LEFT_LABELS)
    right = np.isin(labels, RIGHT_LABELS)
    full = np.isin(labels, LABELS_1_12)

    rows.append({"id": file_id, "roi": "left_hemisphere_combined", "label": "L",
                 **compute_metrics(left, spacing, closing_radius_mm)})
    rows.append({"id": file_id, "roi": "right_hemisphere_combined", "label": "R",
                 **compute_metrics(right, spacing, closing_radius_mm)})
    rows.append({"id": file_id, "roi": "full_cortex_combined", "label": "LR",
                 **compute_metrics(full, spacing, closing_radius_mm)})

    # --- 6 lobe-wise simple averages (mean of metric values from label-pairs)
    for lobe_name, (lab_l, lab_r) in LOBE_PAIRS.items():
        row_l = label_rows[lab_l]
        row_r = label_rows[lab_r]
        avg = {k: float(np.mean([row_l[k], row_r[k]])) for k in METRIC_COLS}
        rows.append({"id": file_id, "roi": lobe_name, "label": f"{lab_l}+{lab_r}", **avg})

    # sanity
    if len(rows) != 21:
        raise RuntimeError(f"Expected 21 ROIs, got {len(rows)} for {seg_path}")

    return rows


def long_to_wide(df_long: pd.DataFrame) -> pd.DataFrame:
    """
    Convert LONG:
      id, roi, metrics...
    to WIDE:
      id, {roi}__{metric} columns
    """
    melted = df_long.melt(
        id_vars=["id", "roi"],
        value_vars=METRIC_COLS,
        var_name="metric",
        value_name="value",
    )

    # roi can be Categorical in long df -> cast to str before concatenation
    melted["col"] = melted["roi"].astype(str) + "__" + melted["metric"].astype(str)

    wide = melted.pivot_table(index="id", columns="col", values="value", aggfunc="first").reset_index()
    wide.columns.name = None

    # enforce deterministic column order: id first, then ROI_ORDER × METRIC_COLS
    desired_cols = ["id"] + [f"{roi}__{met}" for roi in ROI_ORDER for met in METRIC_COLS]
    existing = set(wide.columns.tolist())
    for c in desired_cols:
        if c not in existing:
            wide[c] = np.nan
    wide = wide[desired_cols]

    return wide


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    out_wide_csv = Path(sys.argv[1])
    try:
        n_expected = int(sys.argv[2])
    except ValueError:
        raise SystemExit("Second argument must be an integer: number of files (N).")

    files = [Path(p) for p in sys.argv[3:]]
    if len(files) == 0:
        raise SystemExit("No input files provided.")

    if len(files) != n_expected:
        print(f"WARNING: N={n_expected} but got {len(files)} file paths. Proceeding with {len(files)} files.")

    # Default hull smoothing. Good compromise for 0.5mm fetal cortex across 20–36w.
    closing_radius_mm = 2.0

    all_rows = []
    missing = 0
    for i, f in enumerate(files, start=1):
        if not f.exists():
            print(f"WARNING: missing file: {f}")
            missing += 1
            continue
        print(f"[{i}/{len(files)}] {f.name}")
        all_rows.extend(process_file(f, closing_radius_mm=closing_radius_mm))

    if len(all_rows) == 0:
        raise SystemExit("No rows produced (all files missing or failed).")

    # LONG dataframe
    df_long = pd.DataFrame(all_rows)

    # For a stable LONG ordering (nice for QC), set roi categorical and sort
    df_long["roi"] = pd.Categorical(df_long["roi"], categories=ROI_ORDER, ordered=True)
    df_long = df_long.sort_values(["id", "roi"]).reset_index(drop=True)

    # write LONG
    out_wide_csv.parent.mkdir(parents=True, exist_ok=True)
    out_long_csv = out_wide_csv.with_suffix(".long.csv")
    df_long_cols = ["id", "roi", "label"] + METRIC_COLS
    df_long[df_long_cols].to_csv(out_long_csv, index=False)
    print(f"Saved LONG CSV: {out_long_csv}  (rows={len(df_long)})")

    # WIDE dataframe
    df_wide = long_to_wide(df_long[["id", "roi"] + METRIC_COLS])

    # write WIDE
    df_wide.to_csv(out_wide_csv, index=False)
    print(f"Saved WIDE CSV: {out_wide_csv}  (rows={len(df_wide)}, cols={len(df_wide.columns)})")

    if missing:
        print(f"NOTE: {missing} input files were missing.")


if __name__ == "__main__":
    main()