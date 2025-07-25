#!/usr/bin/env bash -l

#
# Auto SVRTK : deep learning automation for SVRTK reconstruction for fetal MRI
#
# Copyright 2018- King's College London
#
# The auto SVRTK code and all scripts are distributed under the terms of the
# [GNU General Public License v3.0:
# https://www.gnu.org/licenses/gpl-3.0.en.html.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3 of the License.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#

echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo
echo "SVRTK for fetal MRI (KCL): auto brain biomety for 3D SVR TSE T2w fetal MRI"
echo "Source code: https://github.com/SVRTK/auto-proc-svrtk"
echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo


if [ $# -ne 10 ] ; then

    echo "Usage: bash /home/auto-proc-svrtk/scripts/auto-brain-biometry.sh "
    echo "            [Case ID, e.g., test100"
    echo "            [Case GA in weeks (integers), e.g., 30]"
    echo "            [Input T2w .nii.gz file, e.g., /home/data/test100-t2.nii.gz]"
    echo "            [Input BOUNTI label .nii.gz file, e.g., /home/data/test100-t2-bounti-tissue-label.nii.gz]"
    echo "            [Input CC label .nii.gz file, e.g., /home/data/test100-t2-cc-label.nii.gz]"
    echo "            [Output resampled and reoriented T2w .nii.gz file, e.g., /home/data/reo-res-test100-t2.nii.gz]"
    echo "            [Output reoriented BOUNTI label .nii.gz file, e.g., /home/data/reo-res-test100-t2-bounti.nii.gz]"
    echo "            [Output rigid transformation .dof file, e.g., /home/data/reo-test100-rigid.dof]"
    echo "            [Output biometry label .nii.gz file, e.g., /home/data/reo-res-test100-t2-biometry.nii.gz]"
    echo "            [Output biometry .csv file, e.g., /home/data/test100-t2-biometry.csv]"
    echo
    exit

fi

source ~/.bashrc



echo
echo "-----------------------------------------------------------------------------"
echo "INPUT PARAMETERS"
echo "-----------------------------------------------------------------------------"
echo


s=$1
ga=$2
t2=$3
bounti=$4
cc=$5
res_reo_t2=$6
out_bounti=$7
out_dof=$8
bio=$9
bio_csv=$10


echo " - Case ID : " ${s}
echo " - Case GA : " ${ga}
echo " - Input T2w file: " ${t2}
echo " - Input BOUNTI file: " ${bounti}
echo " - Input CC file: " ${cc}
echo " - Output resampled and reoriented T2w .nii.gz file: " ${res_reo_t2}
echo " - Output resampled and reoriented BOUNTI .nii.gz file: " ${out_bounti}
echo " - Output rigid transformation.dof file: " ${out_dof}
echo " - Output resampled and reoriented BIO .nii.gz file: " ${bio}
echo " - Output BIO .csv file: " ${bio_csv}


proc=/home/tmp_proc

rm -r ${proc}/*


ga=$( printf "%.0f" $ga )


src=/home/auto-proc-svrtk

mirtk_path=/bin/MIRTK/build/lib/tools
mrtrix_path=/bin/mrtrix3/bin

atlas_t2=${src}/templates/plane-055t-brain-atlas-t2
atlas_bounti=${src}/templates/plane-055t-brain-atlas-bounti
atlas_train=${src}/templates/train-072024-atlas-fm-v0
atlas_dofs=${src}/templates/plane-055t-ave-dofs-to-atlas
atlas_scaled=${src}/templates/plane-055t-brain-atlas-scaled

checkpoint_path=${src}/trained_models/monai-checkpoints-unet-brain-bio-256-37-lab


echo
echo "-----------------------------------------------------------------------------"
echo "PREPROCESSING"
echo "-----------------------------------------------------------------------------"
echo

echo " ... "

${mirtk_path}/init-dof ${proc}/i.dof

${mirtk_path}/extract-label-brain-lr ${bounti} ${proc}/lr-hemi-label-${s}.nii.gz

${mirtk_path}/register ${atlas_scaled}/scaled-label-lr-hemi-label-${ga}.nii.gz ${proc}/lr-hemi-label-${s}.nii.gz -model Rigid -dofin ${proc}/i.dof -dofout ${proc}/rigid-to-atl-${ga}-${s}.dof -v 0
    
${mirtk_path}/register ${atlas_bounti}/lr-hemi-label-${ga}.nii.gz ${proc}/lr-hemi-label-${s}.nii.gz -model Affine -dofin ${atlas_dofs}/ave-${ga}.dof -dofout ${proc}/aff-to-atl-${ga}-${s}.dof -v 0

${mirtk_path}/transform-image ${t2} ${proc}/${s}-${ga}-t2.nii.gz -interp BSpline -target ${atlas_train}/${ga}-t2.nii.gz -dofin ${proc}/aff-to-atl-${ga}-${s}.dof

${mirtk_path}/transform-image ${bounti} ${proc}/m.nii.gz -labels -target ${atlas_train}/${ga}-t2.nii.gz -dofin ${proc}/aff-to-atl-${ga}-${s}.dof

${mirtk_path}/dilate-image ${proc}/m.nii.gz ${proc}/m.nii.gz -iterations 15

${mirtk_path}/mask-image ${proc}/${s}-${ga}-t2.nii.gz ${proc}/m.nii.gz ${proc}/${s}-${ga}-t2.nii.gz

${mirtk_path}/nan ${proc}/${s}-${ga}-t2.nii.gz 1000000


${mirtk_path}/transform-image ${t2} ${res_reo_t2} -target ${atlas_scaled}/scaled-t2-${ga}.nii.gz -dofin ${proc}/rigid-to-atl-${ga}-${s}.dof -interp BSpline

${mirtk_path}/crop-image ${res_reo_t2} ${res_reo_t2} ${res_reo_t2}

${mirtk_path}/nan ${res_reo_t2} 1000000

${mirtk_path}/convert-image ${res_reo_t2} ${res_reo_t2} -short


${mirtk_path}/transform-image ${bounti} ${out_bounti} -target  ${res_reo_t2} -dofin ${proc}/rigid-to-atl-${ga}-${s}.dof -labels


${mirtk_path}/transform-image ${cc} ${proc}/tr-cc.nii.gz -target  ${res_reo_t2} -dofin ${proc}/rigid-to-atl-${ga}-${s}.dof -labels
${mirtk_path}/extract-connected-components ${proc}/tr-cc.nii.gz ${proc}/tr-cc.nii.gz


cp ${proc}/rigid-to-atl-${ga}-${s}.dof ${out_dof}


echo
echo "-----------------------------------------------------------------------------"
echo "LANDMARK EXTRACTION"
echo "-----------------------------------------------------------------------------"
echo

res=256
lab_num=37

python3 ${src}/src/run_monai_unet_segmentation_1case-2024.py ${res} ${lab_num} ${checkpoint_path}/best_metric_model.pth ${proc}/${s}-${ga}-t2.nii.gz ${proc}/${s}-${ga}-bio-lab.nii.gz


# ${mirtk_path}/flip-image ${proc}/${s}-${ga}-t2.nii.gz ${proc}/flip-${s}-${ga}-t2.nii.gz -x

# python3 ${src}/src/run_monai_unet_segmentation_1case-2024.py ${res} ${lab_num} ${checkpoint_path}/best_metric_model.pth ${proc}/flip-${s}-${ga}-t2.nii.gz ${proc}/flip-${s}-${ga}-bio-lab.nii.gz


# ${mirtk_path}/flip-image ${proc}/flip-${s}-${ga}-bio-lab.nii.gz ${proc}/flip-${s}-${ga}-bio-lab.nii.gz  -x

echo
echo "-----------------------------------------------------------------------------"
echo "PROCESSING LABELS"
echo "-----------------------------------------------------------------------------"
echo
 
 
echo " ... "

${mirtk_path}/invert-dof ${proc}/aff-to-atl-${ga}-${s}.dof ${proc}/inv-aff-to-atl-${ga}-${s}.dof
 
${mirtk_path}/transform-image ${proc}/${s}-${ga}-bio-lab.nii.gz ${proc}/res-org-${s}-bio-lab.nii.gz -dofin ${proc}/rigid-to-atl-${ga}-${s}.dof  ${proc}/inv-aff-to-atl-${ga}-${s}.dof -target ${res_reo_t2} -labels


${mrtrix_path}/mrcalc ${proc}/res-org-${s}-bio-lab.nii.gz 0 -mult ${proc}/repl-res-org-${s}-bio-lab.nii.gz -force -quiet

for ((z=1;z<37;z=z+1)); 
do
#    echo $z
    ${mirtk_path}/extract-label ${proc}/res-org-${s}-bio-lab.nii.gz ${proc}/m.nii.gz ${z} ${z}
    ${mirtk_path}/extract-connected-components ${proc}/m.nii.gz ${proc}/m.nii.gz -v 0 > nul 2>&1
    ${mrtrix_path}/mrcalc ${proc}/m.nii.gz ${z} -mult ${proc}/m.nii.gz -force -quiet
    ${mrtrix_path}/mrcalc ${proc}/m.nii.gz ${proc}/repl-res-org-${s}-bio-lab.nii.gz -add ${proc}/repl-res-org-${s}-bio-lab.nii.gz -force -quiet

done


${mirtk_path}/replace-label-brain ${proc}/repl-res-org-${s}-bio-lab.nii.gz ${proc}/repl-res-org-${s}-bio-lab.nii.gz


#cp ${proc}/repl-res-org-${s}-bio-lab.nii.gz ${bio}




# ${mirtk_path}/transform-image ${proc}/flip-${s}-${ga}-bio-lab.nii.gz ${proc}/res-org-${s}-bio-lab-flip.nii.gz -dofin ${proc}/rigid-to-atl-${ga}-${s}.dof  ${proc}/inv-aff-to-atl-${ga}-${s}.dof -target ${res_reo_t2} -labels



# ${mrtrix_path}/mrcalc ${proc}/res-org-${s}-bio-lab-flip.nii.gz 0 -mult ${proc}/repl-res-org-${s}-bio-lab-flip.nii.gz -force -quiet

# for ((z=1;z<37;z=z+1));
# do
# #    echo $z
#     ${mirtk_path}/extract-label ${proc}/res-org-${s}-bio-lab-flip.nii.gz ${proc}/m.nii.gz ${z} ${z}
#     ${mirtk_path}/extract-connected-components ${proc}/m.nii.gz ${proc}/m.nii.gz -v 0 > nul 2>&1
#     ${mrtrix_path}/mrcalc ${proc}/m.nii.gz ${z} -mult ${proc}/m.nii.gz -force -quiet
#     ${mrtrix_path}/mrcalc ${proc}/m.nii.gz ${proc}/repl-res-org-${s}-bio-lab-flip.nii.gz -add ${proc}/repl-res-org-${s}-bio-lab-flip.nii.gz -force -quiet

# done



# #cp ${proc}/repl-res-org-${s}-bio-lab-flip.nii.gz  /home/data/102024/


# ${mirtk_path}/replace-label-brain-flip ${proc}/repl-res-org-${s}-bio-lab.nii.gz ${proc}/repl-res-org-${s}-bio-lab-flip.nii.gz ${proc}/repl-res-org-${s}-bio-lab.nii.gz


${mirtk_path}/fix-label-brain-cc ${proc}/repl-res-org-${s}-bio-lab.nii.gz ${out_bounti} ${proc}/tr-cc.nii.gz ${proc}/repl-res-org-${s}-bio-lab-fix.nii.gz ${ga}



test_file=${proc}/repl-res-org-${s}-bio-lab-fix.nii.gz
if [[ -f ${test_file} ]];then


    cp ${proc}/repl-res-org-${s}-bio-lab-fix.nii.gz ${bio}


    echo
    echo "-----------------------------------------------------------------------------"
    echo "OUTPUTS"
    echo "-----------------------------------------------------------------------------"
    echo


    ${mirtk_path}/label-biometry-brain ${bio_csv} 1 ${proc}/repl-res-org-${s}-bio-lab-fix.nii.gz

    chmod 1777 ${bio_csv}
    chmod 1777 ${bio}
    chmod 1777 ${res_reo_t2}
    chmod 1777 ${out_bounti}
    chmod 1777 ${out_dof}

    echo
    echo "-----------------------------------------------------------------------------"
    echo "-----------------------------------------------------------------------------"
    echo
 
else

    echo
    echo "-----------------------------------------------------------------------------"
    echo "RPOCESSING ERROR - NO OUTPUT BIOMETRY FILES ... "
    echo "-----------------------------------------------------------------------------"
    echo

    chmod 1777 ${res_reo_t2}
    chmod 1777 ${out_bounti}
    chmod 1777 ${out_dof}

fi
