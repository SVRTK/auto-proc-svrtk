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
echo "SVRTK for fetal MRI (KCL): auto fetal segmentation for BTFE / BSSF / TRUFI stacks"
echo "Source code: https://github.com/SVRTK/auto-proc-svrtk"
echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo

if [[ $# -ne 2 ]] ; then
    echo "Usage: bash /home/auto-proc-svrtk/scripts/auto-btfe-whole-fetus-segmentation.sh"
    echo "            [full path to the folder with BTFE / BSSF / TRUFI stacks]"
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
echo "CROPPING & REMOVING NAN & NEGATIVE/EXTREME VALUES & REMOVING DYNAMICS..."
echo "-----------------------------------------------------------------------------"
echo

for ((i=0;i<${#all_stacks[@]};i++));
do
    echo " - " ${i} " : " ${all_stacks[$i]}
    
#    ${mirtk_path}/mirtk nan ${all_stacks[$i]} 100000

    s=${all_stacks[$i]}
    if [[ $s == *.nii ]]; then
        ${mirtk_path}/mirtk convert-image ${s} ${s}.gz
        rm ${s}
        s=${s}.gz
    fi
    
    ${mirtk_path}/mirtk extract-image-region ${s} ${s} -Rt1 0 -Rt2 0
    ${mirtk_path}/mirtk threshold-image ${s} ../th.nii.gz 0.005 > ../tmp.txt
    ${mirtk_path}/mirtk crop-image ${s} ../th.nii.gz ${s}
    ${mirtk_path}/mirtk nan ${s} 1000000
    
    
done

stack_names=$(ls *.nii*)
IFS=$'\n' read -rd '' -a all_stacks <<<"$stack_names"


echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo
echo "3D WHOLE FETUS AND PLACENTA SEGMENTATION ..."
echo

cd ${main_dir}

echo
echo "-----------------------------------------------------------------------------"
echo "UNET SEGMENTATION GLOBAL ..."
echo "-----------------------------------------------------------------------------"
echo

number_of_stacks=$(ls org-files-preproc/*.nii* | wc -l)
stack_names=$(ls org-files-preproc/*.nii*)

echo " ... "

res=128
monai_lab_num=4
number_of_stacks=$(find org-files-preproc/ -name "*.nii*" | wc -l)
${mirtk_path}/mirtk prepare-for-monai res-stack-files/ stack-files/ stack-info.json stack-info.csv ${res} ${number_of_stacks} org-files-preproc/*nii* > tmp.log

current_monai_check_path=${segm_path}/trained_models/monai-checkpoints-unet-whole-fetus-btfe-128-4-lab

mkdir monai-segmentation-results-p1
python3 ${segm_path}/src/run_monai_unet_segmentation-rot-180-2024.py ${main_dir}/ ${current_monai_check_path}/ stack-info.json ${main_dir}/monai-segmentation-results-p1 ${res} ${monai_lab_num}


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
echo "EXTRACTING PRELIMINARY LABELS AND CROPPING ..."
echo "-----------------------------------------------------------------------------"
echo

out_mask_names=$(ls monai-segmentation-results-p1/cnn-*.nii*)
IFS=$'\n' read -rd '' -a all_masks <<<"$out_mask_names"

stack_names=$(ls org-files-preproc/*.nii*)
IFS=$'\n' read -rd '' -a all_stacks <<<"$stack_names"


mkdir cropped-stacks

for ((i=0;i<${#all_stacks[@]};i++));
do
    echo " - " ${i} " : " ${all_stacks[$i]} ${all_masks[$i]}
    
    jj=$((${i}+1000))
    
    ${mirtk_path}/mirtk extract-label ${all_masks[$i]} m-fetus.nii.gz 2 3
    ${mirtk_path}/mirtk extract-label ${all_masks[$i]} m-placenta.nii.gz 4 4
    ${mirtk_path}/mirtk extract-connected-components m-fetus.nii.gz m-fetus.nii.gz
    ${mirtk_path}/mirtk extract-connected-components m-placenta.nii.gz m-placenta.nii.gz
    
    ${mirtk_path}/mirtk add-images m-fetus.nii.gz m-placenta.nii.gz m.nii.gz
    
    dilate-image m.nii.gz m.nii.gz -iterations 12
    
    ${mirtk_path}/mirtk crop-image ${all_stacks[$i]} m.nii.gz cropped-stacks/cropped-stack-${jj}.nii.gz

done


echo
echo "-----------------------------------------------------------------------------"
echo "UNET SEGMENTATION LOCAL ..."
echo "-----------------------------------------------------------------------------"
echo

number_of_stacks=$(ls cropped-stacks/*.nii* | wc -l)
stack_names=$(ls cropped-stacks/*.nii*)

echo " ... "

res=128
monai_lab_num=4
number_of_stacks=$(find org-files-preproc/ -name "*.nii*" | wc -l)
${mirtk_path}/mirtk prepare-for-monai res-stack-files/ stack-files/ stack-info.json stack-info.csv ${res} ${number_of_stacks} cropped-stacks/*nii* > tmp.log

current_monai_check_path=${segm_path}/trained_models/monai-checkpoints-unet-whole-fetus-btfe-128-4-lab

mkdir monai-segmentation-results-p1
python3 ${segm_path}/src/run_monai_unet_segmentation-rot-180-2024.py ${main_dir}/ ${current_monai_check_path}/ stack-info.json ${main_dir}/monai-segmentation-results-p1 ${res} ${monai_lab_num}


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
echo "EXTRACTING FINAL LABELS ..."
echo "-----------------------------------------------------------------------------"
echo

out_mask_names=$(ls monai-segmentation-results-p1/cnn-*.nii*)
IFS=$'\n' read -rd '' -a all_masks <<<"$out_mask_names"

stack_names=$(ls org-files-preproc/*.nii*)
IFS=$'\n' read -rd '' -a all_stacks <<<"$stack_names"


mkdir fetus-placenta-masks

for ((i=0;i<${#all_stacks[@]};i++));
do
    echo " - " ${i} " : " ${all_stacks[$i]} ${all_masks[$i]}
    
    jj=$((${i}+1000))
    
    ${mirtk_path}/mirtk extract-label ${all_masks[$i]} m-fetus.nii.gz 2 3
    ${mirtk_path}/mirtk extract-label ${all_masks[$i]} m-placenta.nii.gz 4 4
    ${mirtk_path}/mirtk extract-connected-components m-fetus.nii.gz m-fetus.nii.gz
    ${mirtk_path}/mirtk extract-connected-components m-placenta.nii.gz m-placenta.nii.gz
    ${mirtk_path}/mirtk convert-image m-placenta.nii.gz m-placenta.nii.gz -rescale 0 2
    
    ${mirtk_path}/mirtk add-images m-placenta.nii.gz m-fetus.nii.gz fetus-placenta-masks/mask-${jj}.nii.gz

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
    
    ${mirtk_path}/mirtk transform-image fetus-placenta-masks/mask-${jj}.nii.gz fetus-placenta-masks/mask-${jj}.nii.gz  -target ${all_stacks[$i]} -labels
    
#    ${mirtk_path}/mirtk smooth-image fetus-placenta-masks/mask-${jj}.nii.gz fetus-placenta-masks/mask-${jj}.nii.gz -float
#
#    ${mirtk_path}/mirtk threshold-image fetus-placenta-masks/mask-${jj}.nii.gz fetus-placenta-masks/mask-${jj}.nii.gz 0.5  > t.txt

    ${mirtk_path}/mirtk transform-and-rename ${all_stacks[$i]} fetus-placenta-masks/mask-${jj}.nii.gz "-mask-fetus-placenta" ${main_dir}/final-masks
    
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
    echo
    echo "-----------------------------------------------------------------------------"
    echo "ERROR: COULD NOT COPY THE FILES TO THE OUTPUT FOLDER : " ${output_main_folder}
    echo "PLEASE CHECK THE WRITE PERMISSIONS / LOCATION !!!"
    echo
    echo "-----------------------------------------------------------------------------"
    echo

fi

chmod 1777 -R ${output_main_folder}

echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo



    





