#!/usr/bin/env bash -l

#
# Auto SVRTK : deep learning automation for fetal MRI analysis
#
# Copyright 2018- King's College London
#
# The code in https://github.com/SVRTK/auto-proc-svrtk repository
# was designed and created by Alena Uus https://github.com/alenauus
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


source ~/.bashrc

#source /root/.bashrc

#eval "$(conda shell.bash hook)"

#conda init bash

#conda init bash
#conda activate Segmentation_FetalMRI_MONAI

#UPDATE AS REQUIRED BEFORE RUNNING !!!!
software_path=/home
default_run_dir=/home/tmp_proc

dcm2niix_path=/bin/dcm2niix/build/bin
mirtk_path=/bin/MIRTK/build/bin

segm_path=${software_path}/auto-proc-svrtk
template_path=${segm_path}/templates



test_dir=/bin/MIRTK
if [[ ! -d ${test_dir} ]];then
    echo "ERROR: COULD NOT FIND MIRTK INSTALLED IN : " ${software_path}
    echo "PLEASE INSTALL OR UPDATE THE PATH software_path VARIABLE IN THE SCRIPT"
    exit
fi

test_dir=${segm_path}/trained_models
if [[ ! -d ${test_dir} ]];then
    echo "ERROR: COULD NOT FIND SEGMENTATION MODULE INSTALLED IN : " ${software_path}
    echo "PLEASE INSTALL OR UPDATE THE PATH software_path VARIABLE IN THE SCRIPT"
    exit
fi



test_dir=${default_run_dir}
if [[ ! -d ${test_dir} ]];then
    mkdir ${default_run_dir}
else
    rm -r ${default_run_dir}/*
fi

test_dir=${default_run_dir}
if [[ ! -d ${test_dir} ]];then
    echo "ERROR: COULD NOT CREATE THE PROCESSING FOLDER : " ${default_run_dir}
    echo "PLEASE CHECK THE PERMISSIONS OR UPDATE THE PATH default_run_dir VARIABLE IN THE SCRIPT"
    exit
fi



echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo
echo "SVRTK for fetal MRI (KCL): auto reorientation of fetal DSVR body T2w recons"
echo "Source code: https://github.com/SVRTK/auto-proc-svrtk"
echo
echo "Please cite: Uus, A. U., Neves Silva, S., Aviles Verdera, J., Payette, K.,"
echo "Hall, M., Colford, K., Luis, A., Sousa, H. S., Ning, Z., Roberts, T., McElroy, S.,"
echo "Deprez, M., Hajnal, J. V., Rutherford, M. A., Story, L., Hutter, J. (2024) "
echo "Scanner-based real-time 3D brain+body slice-to-volume reconstruction for "
echo "T2-weighted 0.55T low field fetal MRI. medRxiv 2024.04.22.24306177:"
echo "https://doi.org/10.1101/2024.04.22.24306177"
echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo


out_res=0.75
out_type=0
out_scale=0

if [[ $# -ne 5 ]] ; then

   if [[ $# -ne 2 ]] ; then

 	echo "Usage: bash /home/auto-proc-svrtk/scripts/auto-body-reorientation-cdh.sh"
 	echo "            [full path to the folder with T2w DSVR recons]"
 	echo "            [full path to the folder for reoriented results]"
 	echo "            [OPTIONAL: out resolution in mm] | DEFAULT: 0.75" 
 	echo "            [OPTIONAL: out type: 0 - float / 1 - short] | DEFAULT: 0 " 
 	echo "            [OPTIONAL: out scale: 0 - original / 1 - 0-1000] | DEFAULT : 0" 
 	exit

   else
 	input_main_folder=$1
	output_main_folder=$2
   fi 
else 

   input_main_folder=$1
   output_main_folder=$2
   out_res=$3
   out_type=$4 
   out_scale=$5

fi 


echo " - input folder : " ${input_main_folder}
echo " - output folder : " ${input_main_folder}


test_dir=${input_main_folder}
if [[ ! -d ${test_dir} ]];then
    echo
	echo "ERROR: NO FOLDER WITH THE INPUT FILES FOUND !!!!" 
	exit
fi


test_dir=${output_main_folder}
if [[ ! -d ${test_dir} ]];then
	mkdir ${output_main_folder}
    chmod 1777 -R ${output_main_folder}
fi 



cd ${default_run_dir}
main_dir=$(pwd)


cp -r ${input_main_folder} ${default_run_dir}/input-files
input_main_folder=${default_run_dir}/input-files


number_of_stacks=$(find ${input_main_folder}/ -name "*.nii*" | wc -l)
if [[ ${number_of_stacks} -eq 0 ]];then
    echo
    echo "-----------------------------------------------------------------------------"
	echo "ERROR: NO INPUT .nii / .nii.gz FILES FOUND !!!!"
    echo "-----------------------------------------------------------------------------"
    echo
	exit
fi 

mkdir ${default_run_dir}/org-files
find ${input_main_folder}/ -name "*.nii*" -exec cp {} ${default_run_dir}/org-files  \; 

echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo
echo "PREPROCESSING ..."
echo

cd ${default_run_dir}


mkdir org-files-preproc
cp org-files/* org-files-preproc

cd org-files-preproc

stack_names=$(ls *.nii*)
IFS=$'\n' read -rd '' -a all_stacks <<<"$stack_names"

echo
echo "-----------------------------------------------------------------------------"
echo "REMOVING NAN & NEGATIVE/EXTREME VALUES & SPLITTING INTO DYNAMICS..."
echo "-----------------------------------------------------------------------------"
echo

for ((i=0;i<${#all_stacks[@]};i++));
do
    echo " - " ${i} " : " ${all_stacks[$i]}
    ${mirtk_path}/mirtk nan ${all_stacks[$i]} 100000
    ${mirtk_path}/mirtk extract-image-region ${all_stacks[$i]} ${all_stacks[$i]} -Rt1 0 -Rt2 0
#    rm ${all_stacks[$i]}
done

stack_names=$(ls *.nii*)
IFS=$'\n' read -rd '' -a all_stacks <<<"$stack_names"


echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo
echo "REORIENTATION OF DSVR RECONS..."
echo

cd ${main_dir}

echo
echo "-----------------------------------------------------------------------------"
echo "LOCALISATION OF LANDMARK LABELS..."
echo "-----------------------------------------------------------------------------"
echo

number_of_stacks=$(ls org-files-preproc/*.nii* | wc -l)
stack_names=$(ls org-files-preproc/*.nii*)

echo " ... "

res=128
monai_lab_num=6
number_of_stacks=$(find org-files-preproc/ -name "*.nii*" | wc -l)
${mirtk_path}/mirtk prepare-for-monai res-stack-files/ stack-files/ stack-info.json stack-info.csv ${res} ${number_of_stacks} org-files-preproc/*nii* > tmp.log

current_monai_check_path=${segm_path}/trained_models/monai-checkpoints-unet-stack-cdh-thorax-reo-6-lab

mkdir monai-segmentation-results-global


python3 ${segm_path}/src/run_monai_unet_segmentation-rot-180-2024.py ${main_dir}/ ${current_monai_check_path}/ stack-info.json ${main_dir}/monai-segmentation-results-global ${res} ${monai_lab_num}


number_of_stacks=$(find monai-segmentation-results-global/ -name "*.nii*" | wc -l)
if [[ ${number_of_stacks} -eq 0 ]];then
    echo
    echo "-----------------------------------------------------------------------------"
    echo "ERROR: LOCALISATION DID NOT WORK !!!!"
    echo "-----------------------------------------------------------------------------"
    echo
    exit
fi



echo
echo "-----------------------------------------------------------------------------"
echo "EXTRACTING LABELS AND REORIENTING..."
echo "-----------------------------------------------------------------------------"
echo

out_mask_names=$(ls monai-segmentation-results-global/cnn-*.nii*)
IFS=$'\n' read -rd '' -a all_masks <<<"$out_mask_names"

stack_names=$(ls org-files-preproc/*.nii*)
IFS=$'\n' read -rd '' -a all_stacks <<<"$stack_names"

mkdir reo-results
mkdir out-svr-reo-masks
mkdir dofs-to-atlas


thorax_reo_template=${template_path}/reo-spine-body-atlas
${mirtk_path}/mirtk init-dof init.dof


${mirtk_path}/mirtk resample-image ${thorax_reo_template}/ref.nii.gz res-ref.nii.gz -size ${out_res} ${out_res} ${out_res}

    
for ((i=0;i<${#all_stacks[@]};i++));
do
    echo " - " ${i} " : " ${all_stacks[$i]} ${all_masks[$i]}
    
    jj=$((${i}+1000))

    for ((q=1;q<5;q++));
    do
        ${mirtk_path}/mirtk extract-label ${all_masks[$i]} out-svr-reo-masks/mask-${jj}-${q}.nii.gz ${q} ${q}
#        ${mirtk_path}/mirtk dilate-image out-svr-reo-masks/mask-${jj}-${q}.nii.gz out-svr-reo-masks/mask-${jj}-${q}.nii.gz -iterations 1
#        ${mirtk_path}/mirtk erode-image out-svr-reo-masks/mask-${jj}-${q}.nii.gz out-svr-reo-masks/mask-${jj}-${q}.nii.gz -iterations 1
        ${mirtk_path}/mirtk extract-connected-components out-svr-reo-masks/mask-${jj}-${q}.nii.gz out-svr-reo-masks/mask-${jj}-${q}.nii.gz
    done

    z1=1; z2=2; z3=3; z4=4; n_roi=4;

    ${mirtk_path}/mirtk register-landmarks ${thorax_reo_template}/reo-fetal-t2w-body-atlas-reo-label-all.nii.gz ${all_masks[$j]} init.dof dofs-to-atlas/dof-to-atl-${jj}.dof ${n_roi} ${n_roi}  ${thorax_reo_template}/reo-label-all-${z1}.nii.gz ${thorax_reo_template}/reo-label-all-${z2}.nii.gz ${thorax_reo_template}/reo-label-all-${z3}.nii.gz ${thorax_reo_template}/reo-label-all-${z4}.nii.gz out-svr-reo-masks/mask-${jj}-${z1}.nii.gz out-svr-reo-masks/mask-${jj}-${z2}.nii.gz out-svr-reo-masks/mask-${jj}-${z3}.nii.gz out-svr-reo-masks/mask-${jj}-${z4}.nii.gz > tmp.log
    
    ${mirtk_path}/mirtk info dofs-to-atlas/dof-to-atl-${jj}.dof
    
    echo " ... "

    ${mirtk_path}/mirtk transform-image ${all_stacks[$i]} ${all_stacks[$i]} -target res-ref.nii.gz -dofin dofs-to-atlas/dof-to-atl-${jj}.dof -interp BSpline
    
    ${mirtk_path}/mirtk threshold-image ${all_stacks[$i]} m.nii.gz 0.5 > tmp.log
    
    
    ${mirtk_path}/mirtk crop-image ${all_stacks[$i]} m.nii.gz ${all_stacks[$i]}
    
    ${mirtk_path}/mirtk nan ${all_stacks[$i]}  100000


    if [[ ${out_scale} -eq 1 ]];then
        ${mirtk_path}/mirtk convert-image ${all_stacks[$i]} ${all_stacks[$i]} -rescale 0 5000
    fi 
    
    if [[ ${out_type} -eq 1 ]];then
        ${mirtk_path}/mirtk convert-image ${all_stacks[$i]} ${all_stacks[$i]} -short
    fi 


    ${mirtk_path}/mirtk transform-and-rename ${all_stacks[$i]} ${all_stacks[$i]}  "_reo" ${main_dir}/reo-results
        
        
done


number_of_final_files=$(ls ${main_dir}/reo-results/*.nii* | wc -l)
if [[ ${number_of_final_files} -ne 0 ]];then

    cp -r reo-results/*.nii* ${output_main_folder}/
    

    echo "-----------------------------------------------------------------------------"
    echo "Reorientation results are in the output folder : " ${output_main_folder}
    echo "-----------------------------------------------------------------------------"
        
else
    echo
    echo "-----------------------------------------------------------------------------"
    echo "ERROR: COULD NOT COPY THE FILES TO THE OUTPUT FOLDER : " ${output_main_folder}
    echo "PLEASE CHECK THE WRITE PERMISSIONS / LOCATION !!!"
    echo
#    echo "note: you can still find the reoriented files in : " ${main_dir}/reo-results
    echo "-----------------------------------------------------------------------------"
    echo

fi

chmod 1777 -R ${output_main_folder}


echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo



    





