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
echo "SVRTK for fetal MRI (KCL): auto reorientation of fetal SVR brain T2w recons"
echo "Source code: https://github.com/SVRTK/auto-proc-svrtk"
echo
echo "Please cite: Uus, A. U., Neves Silva, S., Aviles Verdera, J., Payette, K.,"
echo "Hall, M., Colford, K., Luis, A., Sousa, H. S., Ning, Z., Roberts, T., McElroy, S.,"
echo "Deprez, M., Hajnal, J. V., Rutherford, M. A., Story, L., Hutter, J. (2024) "
echo "Scanner-based real-time 3D brain+body slice-to-volume reconstruction for "
echo "T2-weighted 0.55T low field fetal MRI. medRxiv 2024.04.22.24306177:"
echo "https://doi.org/10.1101/2024.04.22.24306177"
echo
echo "Uus, A. U., Hall, M., Payette, K., Hajnal, J. V., Deprez, M., Hutter, J., "
echo "Rutherford, M. A., Story, L. (2023) Combined quantitative T2* map and structural "
echo "T2- weighted tissue-specific analysis for fetal brain MRI: pilot automated pipeline. "
echo "PIPPI MICCAI 2023 workshop, LNCS 14246.: https://doi.org/10.1007/978-3-031-45544-5_3"
echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo

out_res=0.75
out_type=0
out_scale=0

if [[ $# -ne 5 ]] ; then

   if [[ $# -ne 2 ]] ; then

 	echo "Usage: bash /home/auto-proc-svrtk/scripts/auto-brain-reorientation.sh"
 	echo "            [full path to the folder with T2w SVR recons]"
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
    ${mirtk_path}/mirtk extract-image-region ${all_stacks[$i]} ${all_stacks[$i]} -split t
    rm ${all_stacks[$i]}
done

stack_names=$(ls *.nii*)
IFS=$'\n' read -rd '' -a all_stacks <<<"$stack_names"


echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo
echo "REORIENTATION OF SVR BRAIN RECONS..."
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

current_monai_check_path=${segm_path}/trained_models/monai-checkpoints-attunet-brain-bet-1-lab

mkdir monai-segmentation-results-bet
python3 ${segm_path}/src/run_monai_atunet_segmentation-2022.py ${main_dir}/ ${current_monai_check_path}/ stack-info.json ${main_dir}/monai-segmentation-results-bet ${res} ${monai_lab_num}


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
echo "EXTRACTING LABELS AND MASKING ..."
echo "-----------------------------------------------------------------------------"
echo

out_mask_names=$(ls monai-segmentation-results-bet/cnn-*.nii*)
IFS=$'\n' read -rd '' -a all_masks <<<"$out_mask_names"

stack_names=$(ls org-files-preproc/*.nii*)
IFS=$'\n' read -rd '' -a all_stacks <<<"$stack_names"


mkdir bet-masks

mkdir masked-cropped-stacks-brain

for ((i=0;i<${#all_stacks[@]};i++));
do
    echo " - " ${i} " : " ${all_stacks[$i]} ${all_masks[$i]}
    
    jj=$((${i}+1000))
    
    ${mirtk_path}/mirtk extract-label ${all_masks[$i]} bet-masks/mask-${jj}.nii.gz 1 1

    ${mirtk_path}/mirtk extract-connected-components bet-masks/mask-${jj}.nii.gz bet-masks/mask-${jj}.nii.gz
    
    ${mirtk_path}/mirtk dilate-image bet-masks/mask-${jj}.nii.gz tmp-dl.nii.gz -iterations 4
    
    ${mirtk_path}/mirtk mask-image ${all_stacks[$i]} tmp-dl.nii.gz masked-cropped-stacks-brain/stack-${jj}.nii.gz
    
    ${mirtk_path}/mirtk crop-image masked-cropped-stacks-brain/stack-${jj}.nii.gz tmp-dl.nii.gz masked-cropped-stacks-brain/stack-${jj}.nii.gz
 
done




echo
echo "-----------------------------------------------------------------------------"
echo "RUNNING LANDMARK UNET ..."
echo "-----------------------------------------------------------------------------"
echo

number_of_stacks=$(ls masked-cropped-stacks-brain/*.nii* | wc -l)
stack_names=$(ls masked-cropped-stacks-brain/*.nii*)

echo " ... "

res=128
monai_lab_num=5
number_of_stacks=$(find org-files-preproc/ -name "*.nii*" | wc -l)
${mirtk_path}/mirtk prepare-for-monai res-reo-files/ reo-files/ stack-info.json stack-info.csv ${res} ${number_of_stacks} masked-cropped-stacks-brain/*nii* > tmp.log

current_monai_check_path=${segm_path}/trained_models/monai-checkpoints-unet-svr-brain-reo-5-lab

mkdir monai-segmentation-results-reo
python3 ${segm_path}/src/run_monai_unet_segmentation-2022.py ${main_dir}/ ${current_monai_check_path}/ stack-info.json ${main_dir}/monai-segmentation-results-reo ${res} ${monai_lab_num}


number_of_stacks=$(find monai-segmentation-results-reo/ -name "*.nii*" | wc -l)
if [[ ${number_of_stacks} -eq 0 ]];then
    echo
    echo "-----------------------------------------------------------------------------"
    echo "ERROR: REO CNN LOCALISATION DID NOT WORK !!!!"
    echo "-----------------------------------------------------------------------------"
    echo
    exit
fi

echo
echo "-----------------------------------------------------------------------------"
echo "EXTRACTING LABELS AND REORIENTING..."
echo "-----------------------------------------------------------------------------"
echo

out_mask_names=$(ls monai-segmentation-results-reo/cnn-*.nii*)
IFS=$'\n' read -rd '' -a all_masks <<<"$out_mask_names"

org_stack_names=$(ls org-files-preproc/*.nii*)
IFS=$'\n' read -rd '' -a all_org_stacks <<<"$org_stack_names"


mkdir reo-results
mkdir out-svr-reo-masks
mkdir dofs-to-atlas


current_template_path=${template_path}/brain-ref-atlas-2022
${mirtk_path}/mirtk init-dof init.dof

${mirtk_path}/mirtk resample-image ${current_template_path}/ref-space-brain.nii.gz res-ref.nii.gz -size ${out_res} ${out_res} ${out_res}
    
for ((i=0;i<${#all_org_stacks[@]};i++));
do
    echo " - " ${i} " : " ${all_org_stacks[$i]} ${all_masks[$i]}
    
    jj=$((${i}+1000))

    for ((q=1;q<6;q++));
    do
        ${mirtk_path}/mirtk extract-label ${all_masks[$i]} out-svr-reo-masks/mask-${jj}-${q}.nii.gz ${q} ${q}
        ${mirtk_path}/mirtk dilate-image out-svr-reo-masks/mask-${jj}-${q}.nii.gz out-svr-reo-masks/mask-${jj}-${q}.nii.gz -iterations 2
        ${mirtk_path}/mirtk erode-image out-svr-reo-masks/mask-${jj}-${q}.nii.gz out-svr-reo-masks/mask-${jj}-${q}.nii.gz -iterations 2
        ${mirtk_path}/mirtk extract-connected-components out-svr-reo-masks/mask-${jj}-${q}.nii.gz out-svr-reo-masks/mask-${jj}-${q}.nii.gz
    done

    z1=1; z2=2; z3=3; z4=4; n_roi=4;

    

    ${mirtk_path}/mirtk register-landmarks ${current_template_path}/mask-${z1}.nii.gz ${all_org_stacks[$j]} init.dof dofs-to-atlas/dof-to-atl-${jj}.dof ${n_roi} ${n_roi} ${current_template_path}/mask-${z1}.nii.gz ${current_template_path}/mask-${z2}.nii.gz ${current_template_path}/mask-${z3}.nii.gz ${current_template_path}/mask-${z4}.nii.gz out-svr-reo-masks/mask-${jj}-${z1}.nii.gz out-svr-reo-masks/mask-${jj}-${z2}.nii.gz out-svr-reo-masks/mask-${jj}-${z3}.nii.gz out-svr-reo-masks/mask-${jj}-${z4}.nii.gz > tmp.log
    
    ${mirtk_path}/mirtk info dofs-to-atlas/dof-to-atl-${jj}.dof
    
    echo " ... "

    ${mirtk_path}/mirtk transform-image ${all_org_stacks[$i]} ${all_org_stacks[$i]} -target res-ref.nii.gz -dofin dofs-to-atlas/dof-to-atl-${jj}.dof -interp BSpline
    
    ${mirtk_path}/mirtk threshold-image ${all_org_stacks[$i]} m.nii.gz 0.5 > tmp.log
    
    ${mirtk_path}/mirtk crop-image ${all_org_stacks[$i]} m.nii.gz ${all_org_stacks[$i]}
    
    ${mirtk_path}/mirtk nan ${all_org_stacks[$i]}  100000

    if [[ ${out_scale} -eq 1 ]];then
	${mirtk_path}/mirtk convert-image ${all_org_stacks[$i]} ${all_org_stacks[$i]} -rescale 0 1000 
    fi 
    
    if [[ ${out_type} -eq 1 ]];then
	${mirtk_path}/mirtk convert-image ${all_org_stacks[$i]} ${all_org_stacks[$i]} -short 
    fi 

    
    ${mirtk_path}/mirtk transform-and-rename ${all_org_stacks[$i]} ${all_org_stacks[$i]}  "_reo" ${main_dir}/reo-results
        
        
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
    echo "note: you can still find the reoriented files in : " ${main_dir}/reo-results
    echo "-----------------------------------------------------------------------------"
    echo

fi

chmod 1777 -R ${output_main_folder}

echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo



    





