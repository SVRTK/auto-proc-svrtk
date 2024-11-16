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
echo "SVRTK for fetal MRI (KCL): auto lung segmentation for 3D DSVR SSTSE / HASTE T2w fetal MRI"
echo "Source code: https://github.com/SVRTK/auto-proc-svrtk"
echo
echo "Towards automated multi-regional lung parcellation for 0.55-3T 3D T2w fetal MRI"
echo "Uus, A., Avena Zampieri, C., Downes, F., Egloff Collado, A., Hall, M., Davidson, "
echo "J. R., Payette, K., Aviles Verdera, J., Grigorescu, I., Hajnal, J., Deprez, M., "
echo "Aertsen, M., Hutter, J., Rutherford, M., Deprest, J. & Story, L., Jul 2024, "
echo "PIPPI MICCAI Workshop 2024. LNCS, vol 14747. https://doi.org/10.1007/978-3-031-73260-7_11"
echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo

if [[ $# -ne 2 ]] ; then
    echo "Usage: bash /home/auto-proc-svrtk/scripts/auto-lung-segmentation.sh"
    echo "            [full path to the folder with 3D T2w DSVR recons]"
    echo "            [full path to the folder for segmentation results]"
    echo
    echo "note: tmp processing files are stored in /home/tmp_proc"
    echo
    exit
else
    input_main_folder=$1
    output_main_folder=$2
fi


echo " - input folder : " ${input_main_folder}
echo " - output folder : " ${output_main_folder}


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


number_of_stacks=$(find ${input_main_folder}/ -name "*.dcm" | wc -l)
if [ $number_of_stacks -gt 0 ];then
    echo
    echo "-----------------------------------------------------------------------------"
    echo "FOUND .dcm FILES - CONVERTING TO .nii.gz !!!!"
    echo "-----------------------------------------------------------------------------"
    echo
    cd ${input_main_folder}/
    ${dcm2niix_path}/dcm2niix -z y .
    cd ${main_dir}/
fi



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
echo "CROPPING & REMOVING NAN & NEGATIVE/EXTREME VALUES & "
echo "TRANSFORMING TO THE STANDARD SPACE & REMOVING DYNAMICS..."
echo "-----------------------------------------------------------------------------"
echo

for ((i=0;i<${#all_stacks[@]};i++));
do
    echo " - " ${i} " : " ${all_stacks[$i]}
#    ${mirtk_path}/mirtk nan ${all_stacks[$i]} 100000
    ${mirtk_path}/mirtk extract-image-region ${all_stacks[$i]} ${all_stacks[$i]} -Rt1 0 -Rt2 0
    ${mirtk_path}/mirtk threshold-image ${all_stacks[$i]} ../th.nii.gz 0.005 > ../tmp.txt
    ${mirtk_path}/mirtk crop-image ${all_stacks[$i]} ../th.nii.gz ${all_stacks[$i]}
    
    ${mirtk_path}/mirtk edit-image ${template_path}/reo-spine-body-atlas/ref.nii.gz ../ref.nii.gz -copy-origin ${all_stacks[$i]}
    ${mirtk_path}/mirtk transform-image ${all_stacks[$i]} ${all_stacks[$i]} -target ../ref.nii.gz -interp Linear
    ${mirtk_path}/mirtk crop-image ${all_stacks[$i]} ../th.nii.gz ${all_stacks[$i]}
    ${mirtk_path}/mirtk nan ${all_stacks[$i]} 1000000
    
    
done

stack_names=$(ls *.nii*)
IFS=$'\n' read -rd '' -a all_stacks <<<"$stack_names"


echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo
echo "3D LUNG SEGMENTATION OF 3D DSVR T2W BODY RECONS..."
echo

cd ${main_dir}

echo
echo "-----------------------------------------------------------------------------"
echo "UNET SEGMENTATION ..."
echo "-----------------------------------------------------------------------------"
echo

number_of_stacks=$(ls org-files-preproc/*.nii* | wc -l)
stack_names=$(ls org-files-preproc/*.nii*)

echo " ... "

res=256
monai_lab_num=10
number_of_stacks=$(find org-files-preproc/ -name "*.nii*" | wc -l)
${mirtk_path}/mirtk prepare-for-monai res-stack-files/ stack-files/ stack-info.json stack-info.csv ${res} ${number_of_stacks} org-files-preproc/*nii* > tmp.log

current_monai_check_path=${segm_path}/trained_models/monai-checkpoints-unet-body-lung-multi-256-10-lab

mkdir monai-segmentation-results-p1
python3 ${segm_path}/src/run_monai_unet_segmentation-2022.py ${main_dir}/ ${current_monai_check_path}/ stack-info.json ${main_dir}/monai-segmentation-results-p1 ${res} ${monai_lab_num}


number_of_stacks=$(find monai-segmentation-results-p1/ -name "*.nii*" | wc -l)
if [[ ${number_of_stacks} -eq 0 ]];then
    echo
    echo "-----------------------------------------------------------------------------"
    echo "ERROR: SEGMENTATION DID NOT WORK !!!!"
    echo "-----------------------------------------------------------------------------"
    echo
    exit
fi


echo
echo "-----------------------------------------------------------------------------"
echo "EXTRACTING LABELS ..."
echo "-----------------------------------------------------------------------------"
echo

out_mask_names=$(ls monai-segmentation-results-p1/cnn-*.nii*)
IFS=$'\n' read -rd '' -a all_masks <<<"$out_mask_names"

stack_names=$(ls org-files-preproc/*.nii*)
IFS=$'\n' read -rd '' -a all_stacks <<<"$stack_names"


mkdir lung-masks

for ((i=0;i<${#all_stacks[@]};i++));
do
    echo " - " ${i} " : " ${all_stacks[$i]} ${all_masks[$i]}
    
    jj=$((${i}+1000))
    
    ${mirtk_path}/mirtk extract-label ${all_masks[$i]} m.nii.gz 1 5
    ${mirtk_path}/mirtk mask-image ${all_masks[$i]} m.nii.gz lung-masks/mask-${jj}.nii.gz
#    ${mirtk_path}/mirtk extract-connected-components lung-masks/mask-${jj}.nii.gz lung-masks/mask-${jj}.nii.gz
#    cp ${all_masks[$i]} lung-masks/mask-${jj}.nii.gz

done



echo
echo "-----------------------------------------------------------------------------"
echo "TRANSFORMING TO THE ORIGINAL SPACE ..."
echo "-----------------------------------------------------------------------------"
echo


stack_names=$(ls org-files/*.nii*)
IFS=$'\n' read -rd '' -a all_stacks <<<"$stack_names"


mkdir final-masks

for ((i=0;i<${#all_stacks[@]};i++));
do
    echo " - " ${i} " : " ${all_stacks[$i]}
    
    jj=$((${i}+1000))
    
    echo
    
    ${mirtk_path}/mirtk transform-image lung-masks/mask-${jj}.nii.gz lung-masks/mask-${jj}.nii.gz  -target ${all_stacks[$i]} -labels
    
#    ${mirtk_path}/mirtk smooth-image lung-masks/mask-${jj}.nii.gz lung-masks/mask-${jj}.nii.gz -float
#
#    ${mirtk_path}/mirtk threshold-image lung-masks/mask-${jj}.nii.gz lung-masks/mask-${jj}.nii.gz 0.5  > t.txt

    ${mirtk_path}/mirtk transform-and-rename ${all_stacks[$i]} lung-masks/mask-${jj}.nii.gz "-mask-lung-lobes-5" ${main_dir}/final-masks
    
    echo

done



number_of_final_files=$(ls ${main_dir}/final-masks/*.nii* | wc -l)
if [[ ${number_of_final_files} -ne 0 ]];then

    cp -r final-masks/*.nii* ${output_main_folder}/
    
    chmod 1777 -R ${output_main_folder}
    

    echo "-----------------------------------------------------------------------------"
    echo "Segmentation results are in the output folder : " ${output_main_folder}
    echo "-----------------------------------------------------------------------------"
        
else

    chmod 1777 -R ${output_main_folder}
    
    echo
    echo "-----------------------------------------------------------------------------"
    echo "ERROR: COULD NOT COPY THE FILES TO THE OUTPUT FOLDER : " ${output_main_folder}
    echo "PLEASE CHECK THE WRITE PERMISSIONS / LOCATION !!!"
    echo
    echo "-----------------------------------------------------------------------------"
    echo

fi


echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo



    





