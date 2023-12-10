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

source ~/.bashrc

#eval "$(conda shell.bash hook)"
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

#fetal
monai_check_path_bet_attunet=${segm_path}/trained_models/monai-checkpoints-attunet-brain-bet-1-lab
monai_check_path_bounti_unet=${segm_path}/trained_models/monai-checkpoints-unet-brain-bounti-19-lab
monai_check_path_bounti_attunet=${segm_path}/trained_models/monai-checkpoints-red-attunet-brain_bounti-19-lab

##neo
#monai_check_path_bet_neo_attunet=${segm_path}/trained_models/monai-checkpoints-attunet-neo-brain-bet-1-lab
#monai_check_path_bounti_neo_unet=${segm_path}/trained_models/monai-checkpoints-unet-neo-brain-bounti-19-lab
#

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
echo "SVRTK for fetal MRI (KCL): auto brain tissue segmentation for 3D SVR SSTSE / HASTE T2w fetal MRI"
echo "Source code: https://github.com/SVRTK/auto-proc-svrtk"
echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo

if [[ $# -ne 2 ]] ; then
    echo "Usage: bash /home/auto-proc-svrtk/scripts/auto-brain-bounti-segmentation-fetal.sh"
    echo "            [full path to the folder with 3D T2w SVR recons]"
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
    
    ${mirtk_path}/mirtk edit-image ${template_path}/brain-ref-space.nii.gz ../ref.nii.gz -copy-origin ${all_stacks[$i]}
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
echo "3D BOUNTI TISSUE SEGMENTATION OF 3D SVR T2W BRAIN RECONS..."
echo

cd ${main_dir}

echo
echo "-----------------------------------------------------------------------------"
echo "GLOBAL BET ..."
echo "-----------------------------------------------------------------------------"
echo

number_of_stacks=$(ls org-files-preproc/*.nii* | wc -l)
stack_names=$(ls org-files-preproc/*.nii*)

echo " ... "

res=128
monai_lab_num=1
number_of_stacks=$(find org-files-preproc/ -name "*.nii*" | wc -l)
${mirtk_path}/mirtk prepare-for-monai res-stack-files/ stack-files/ stack-info.json stack-info.csv ${res} ${number_of_stacks} org-files-preproc/*nii* > tmp.log

mkdir monai-segmentation-results-bet
python3 ${segm_path}/src/run_monai_atunet_segmentation-2022.py ${main_dir}/ ${monai_check_path_bet_attunet}/ stack-info.json ${main_dir}/monai-segmentation-results-bet ${res} ${monai_lab_num}


number_of_stacks=$(find monai-segmentation-results-bet/ -name "*.nii*" | wc -l)
if [[ ${number_of_stacks} -eq 0 ]];then
    echo
    echo "-----------------------------------------------------------------------------"
    echo "ERROR: BET LOCALISATION DID NOT WORK !!!!"
    echo "-----------------------------------------------------------------------------"
    echo
    exit
fi


echo
echo "-----------------------------------------------------------------------------"
echo "EXTRACTING LABELS AND MASKING..."
echo "-----------------------------------------------------------------------------"
echo

out_mask_names=$(ls monai-segmentation-results-bet/cnn-*.nii*)
IFS=$'\n' read -rd '' -a all_masks <<<"$out_mask_names"

stack_names=$(ls org-files-preproc/*.nii*)
IFS=$'\n' read -rd '' -a all_stacks <<<"$stack_names"


mkdir masked-stacks
mkdir bet-masks

for ((i=0;i<${#all_stacks[@]};i++));
do
    echo " - " ${i} " : " ${all_stacks[$i]} ${all_masks[$i]}
    
    jj=$((${i}+1000))
    
    ${mirtk_path}/mirtk extract-label ${all_masks[$i]} bet-masks/mask-${jj}.nii.gz 1 1
    ${mirtk_path}/mirtk extract-connected-components bet-masks/mask-${jj}.nii.gz bet-masks/mask-${jj}.nii.gz
    ${mirtk_path}/mirtk transform-image bet-masks/mask-${jj}.nii.gz bet-masks/mask-${jj}.nii.gz -target ${all_stacks[$i]} -labels
    ${mirtk_path}/mirtk dilate-image bet-masks/mask-${jj}.nii.gz dl.nii.gz -iterations 4
    ${mirtk_path}/mirtk erode-image dl.nii.gz dl.nii.gz -iterations 2
    ${mirtk_path}/mirtk mask-image ${all_stacks[$i]} dl.nii.gz masked-stacks/masked-stack-${jj}.nii.gz
    ${mirtk_path}/mirtk crop-image masked-stacks/masked-stack-${jj}.nii.gz dl.nii.gz masked-stacks/masked-stack-${jj}.nii.gz

    # ${mirtk_path}/mirtk N4 -i masked-stacks/masked-stack-${jj}.nii.gz -x dl.nii.gz -o tmp.nii.gz  -c "[50x50x50,0.001]" -s 2 -b "[100,3]" -t "[0.15,0.01,200]" > tmp.txt
    # cp tmp.nii.gz  masked-stacks/masked-stack-${jj}.nii.gz

done


echo
echo "-----------------------------------------------------------------------------"
echo "BOUNTI BRAIN TISSUE SEGMENTATION ..."
echo "-----------------------------------------------------------------------------"
echo

number_of_stacks=$(ls masked-stacks/*.nii* | wc -l)
stack_names=$(ls masked-stacks/*.nii*)

echo " ... "

res=256
monai_lab_num=19
number_of_stacks=$(find masked-stacks/ -name "*.nii*" | wc -l)
${mirtk_path}/mirtk prepare-for-monai res-masked-stack-files/ masked-stack-files/ masked-stack-info.json masked-stack-info.csv ${res} ${number_of_stacks} masked-stacks/*nii* > tmp.log

mkdir monai-segmentation-results-bounti

python3 ${segm_path}/src/run_monai_comb_red_atunet_unet_segmentation-2022-lr.py ${main_dir}/ ${monai_check_path_bounti_attunet}/ ${monai_check_path_bounti_unet}/ masked-stack-info.json ${main_dir}/monai-segmentation-results-bounti ${res} ${monai_lab_num}



number_of_stacks=$(find monai-segmentation-results-bounti/ -name "*.nii*" | wc -l)
if [[ ${number_of_stacks} -eq 0 ]];then
    echo
    echo "-----------------------------------------------------------------------------"
    echo "ERROR: BOUNTI SEGMENTATION DID NOT WORK !!!!"
    echo "-----------------------------------------------------------------------------"
    echo
    exit
fi



echo
echo "-----------------------------------------------------------------------------"
echo "EXTRACTING LABELS AND TRANSFORMING TO THE ORIGINAL SPACE ..."
echo "-----------------------------------------------------------------------------"
echo

out_mask_names=$(ls monai-segmentation-results-bounti/cnn-*.nii*)
IFS=$'\n' read -rd '' -a all_masks <<<"$out_mask_names"

stack_names=$(ls org-files/*.nii*)
IFS=$'\n' read -rd '' -a all_stacks <<<"$stack_names"


mkdir bounti-masks

for ((i=0;i<${#all_stacks[@]};i++));
do
    echo " - " ${i} " : " ${all_stacks[$i]} ${all_masks[$i]}
    
    jj=$((${i}+1000))
    
    echo
    
    ${mirtk_path}/mirtk transform-image ${all_masks[$i]} ${all_masks[$i]} -target ${all_stacks[$i]} -labels
    ${mirtk_path}/mirtk transform-and-rename ${all_stacks[$i]} ${all_masks[$i]} "-mask-brain_bounti-"${monai_lab_num} ${main_dir}/bounti-masks
    
    ${mirtk_path}/mirtk transform-image bet-masks/mask-${jj}.nii.gz bet-masks/mask-${jj}.nii.gz  -target ${all_stacks[$i]} -labels
    ${mirtk_path}/mirtk transform-and-rename ${all_stacks[$i]} bet-masks/mask-${jj}.nii.gz "-mask-bet-1" ${main_dir}/bounti-masks
    
    echo

done



number_of_final_files=$(ls ${main_dir}/bounti-masks/*.nii* | wc -l)
if [[ ${number_of_final_files} -ne 0 ]];then

    cp -r bounti-masks/*.nii* ${output_main_folder}/
    

    echo "-----------------------------------------------------------------------------"
    echo "Segmentation results are in the output folder : " ${output_main_folder}
    echo "-----------------------------------------------------------------------------"
        
else
    echo
    echo "-----------------------------------------------------------------------------"
    echo "ERROR: COULD NOT COPY THE FILES TO THE OUTPUT FOLDER : " ${output_main_folder}
    echo "PLEASE CHECK THE WRITE PERMISSIONS / LOCATION !!!"
    echo
    echo "note: you can still find the reoriented files in : " ${main_dir}/reo-results
    echo "-----------------------------------------------------------------------------"
    echo

fi


echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo



    





