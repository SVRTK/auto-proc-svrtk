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

echo "Setting environment ... "
echo

source ~/.bashrc

# source /root/.bashrc

# eval "$(conda shell.bash hook)"

# conda init bash

# conda activate Segmentation_FetalMRI_MONAI



software_path=/home

default_run_dir=/home/tmp_proc

segm_path=${software_path}/auto-proc-svrtk

dcm2niix_path=/bin/dcm2niix/build/bin

mirtk_path=/bin/MIRTK/build/bin

template_path=${segm_path}/templates

model_path=${segm_path}/trained_models


atl=${template_path}/body-stack-reo-template-2023


test_dir=/bin/MIRTK
if [ ! -d $test_dir ];then
    echo "ERROR: COULD NOT FIND MIRTK INSTALLED IN : " ${software_path}
    echo "PLEASE INSTALL OR UPDATE THE PATH software_path VARIABLE IN THE SCRIPT"
    exit
fi

test_dir=${segm_path}/trained_models
if [ ! -d $test_dir ];then
    echo "ERROR: COULD NOT FIND SEGMENTATION MODULE INSTALLED IN : " ${software_path}
    echo "PLEASE INSTALL OR UPDATE THE PATH software_path VARIABLE IN THE SCRIPT"
    exit
fi




test_dir=${default_run_dir}
if [ ! -d $test_dir ];then
    mkdir ${default_run_dir}
else
    rm -r ${default_run_dir}/*
fi

test_dir=${default_run_dir}
if [ ! -d $test_dir ];then
    echo "ERROR: COULD NOT CREATE THE PROCESSING FOLDER : " ${default_run_dir}
    echo "PLEASE CHECK THE PERMISSIONS OR UPDATE THE PATH default_run_dir VARIABLE IN THE SCRIPT"
    exit
fi



echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo
echo "SVRTK for fetal MRI (KCL): auto body DSVR reconstruction for TSE T2w fetal MRI"
echo "Source code: https://github.com/SVRTK/auto-proc-svrtk"
echo
echo "Please cite: Uus, A. U., Neves Silva, S., Aviles Verdera, J., Payette, K.,"
echo "Hall, M., Colford, K., Luis, A., Sousa, H. S., Ning, Z., Roberts, T., McElroy, S.,"
echo "Deprez, M., Hajnal, J. V., Rutherford, M. A., Story, L., Hutter, J. (2024) "
echo "Scanner-based real-time 3D brain+body slice-to-volume reconstruction for "
echo "T2-weighted 0.55T low field fetal MRI. medRxiv 2024.04.22.24306177:"
echo "https://doi.org/10.1101/2024.04.22.24306177"
echo
echo "Uus, A., Zhang, T., Jackson, L., Roberts, T., Rutherford, M., Hajnal, J.V., "
echo "Deprez, M. (2020). Deformable Slice-to-Volume Registration for Motion Correction "
echo "in Fetal Body MRI and Placenta. IEEE Transactions on Medical Imaging, 39(9), 2750-2759:"
echo "http://dx.doi.org/10.1109/TMI.2020.2974844"
echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo 

if [ $# -ne 2 ] ; then

    if [ $# -ne 6 ] ; then
        echo "Usage: bash /home/auto-proc-svrtk/scripts/auto-body-reconstruction-2026.sh"
        echo "            [FULL path to the folder with raw T2w stacks in .nii or .dcm, e.g., /home/data/test]"
        echo "            [FULL path to the folder for recon results, e.g., /home/data/out-test]"
        echo "            (optional) [motion correction mode (0 or 1): 0 - minor, 1 - >180 degree rotations] - default: 1"
        echo "            (optional) [slice thickness] - default: 3.0"
        echo "            (optional) [output recon resolution] - default: 0.85"
        echo "            (optional) [number of packages] - default: 1"
        echo
        exit
    else
        input_main_folder=$1
        output_main_folder=$2
        motion_correction_mode=$3
        default_thickness=$4
        recon_resolution=$5
        num_packages=$6
    fi
    
else
    input_main_folder=$1
    output_main_folder=$2
    motion_correction_mode=1
    default_thickness=3.0
    recon_resolution=0.85
    num_packages=1
fi


echo " - input folder : " ${input_main_folder}
echo " - output folder : " ${output_main_folder}
echo " - motion correction mode : " ${motion_correction_mode}
echo " - slice thickness : " ${default_thickness}
echo " - output resolution : " ${recon_resolution}


recon_roi=brain


test_dir=${input_main_folder}
if [ ! -d $test_dir ];then
    echo
	echo "ERROR: NO FOLDER WITH THE INPUT FILES FOUND !!!!" 
	exit
fi


test_dir=${output_main_folder}
if [ ! -d $test_dir ];then
	mkdir ${output_main_folder}
    chmod 1777 -R ${output_main_folder}/
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
if [ $number_of_stacks -eq 0 ];then

    chmod 1777 -R ${output_main_folder}/

    echo
    echo "-----------------------------------------------------------------------------"
	echo "ERROR: NO INPUT .nii / .nii.gz FILES FOUND !!!!"
    echo "-----------------------------------------------------------------------------"
    echo
	exit
fi 

mkdir ${default_run_dir}/org-files
find ${input_main_folder}/ -name "*.nii*" -exec cp {} ${default_run_dir}/org-files  \; 


number_of_stacks=$(find ${default_run_dir}/org-files -name "*SVR-output*.nii*" | wc -l)
if [ $number_of_stacks -gt 0 ];then
    echo
    echo "-----------------------------------------------------------------------------"
    echo "WARNING: FOUND ALREADY EXISTING *SVR-output* FILES IN THE DATA FOLDER !!!!"
    echo "-----------------------------------------------------------------------------"
    echo "note: they won't be used in reconstruction"
    echo
    rm ${default_run_dir}/org-files/"*SVR-output*.nii*"
fi

number_of_stacks=$(find ${default_run_dir}/org-files -name "*mask*.nii*" | wc -l)
if [ $number_of_stacks -gt 0 ];then

    echo
    echo "-----------------------------------------------------------------------------"
    echo "WARNING: FOUND *mask* FILES IN THE DATA FOLDER !!!!"
    echo "-----------------------------------------------------------------------------"
    echo "note: they won't be used in reconstruction"
    echo
    rm ${default_run_dir}/org-files/"*mask*.nii*"
fi

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
read -rd '' -a all_stacks <<<"$stack_names"

echo
echo "-----------------------------------------------------------------------------"
echo "REMOVING NAN & NEGATIVE/EXTREME VALUES & PLANNING STACKS & SPLITTING INTO DYNAMICS ..."
echo "-----------------------------------------------------------------------------"
echo

for ((i=0;i<${#all_stacks[@]};i++));
do
    echo " - " ${i} " : " ${all_stacks[$i]}

    st=${all_stacks[$i]}
    st=$(echo ${st//.nii.gz\//\.nii.gz})
    st=$(echo ${st//.nii\//\.nii})

    ${mirtk_path}/mirtk convert-image ${st} pw-z.nii.gz
    num_slices=$(/bin/MIRTK/build/lib/tools/get-z pw-z.nii.gz)
     
    if [ $num_slices -lt 15 ]; then
        rm ${st}
        echo
        echo " - note: stack " ${st} " was excluded - not enough slices "
        echo
    fi
    rm pw-z.nii.gz

done

stack_names=$(ls *.nii*)
read -rd '' -a all_stacks <<<"$stack_names"

for ((i=0;i<${#all_stacks[@]};i++));
do
    echo " - " ${i} " : " ${all_stacks[$i]}

    st=${all_stacks[$i]}
    st=$(echo ${st//.nii.gz\//\.nii.gz})
    st=$(echo ${st//.nii\//\.nii})
    
    ${mirtk_path}/mirtk nan ${st} 100000
    ${mirtk_path}/mirtk extract-image-region ${st} ${st} -split t
    rm ${st}
    
    
done



stack_names=$(ls *.nii*)
read -rd '' -a all_stacks <<<"$stack_names"


if [ $num_packages -ne 1 ]; then
    echo
    echo "-----------------------------------------------------------------------------"
    echo "SPLITTING INTO PACKAGES ..."
    echo "-----------------------------------------------------------------------------"
    echo

    for ((i=0;i<${#all_stacks[@]};i++));
    do
        echo " - " ${i} " : " ${all_stacks[$i]}
        
        st=${all_stacks[$i]}
        st=$(echo ${st//.nii.gz\//\.nii.gz})
        st=$(echo ${st//.nii\//\.nii})
        
        ${mirtk_path}/mirtk extract-packages ${st} ${num_packages}

        rm ${st}
        rm package-template.nii.gz

    done
fi



echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo 
echo "RUNNING GLOBAL BODY LOCALISATION AND REORIENTATION ..."
echo


cd ${default_run_dir}

mkdir res-global-stacks
mkdir out-global-masks

mkdir res-crop-stacks
mkdir out-reo-masks
mkdir out-dofs-to-template


mkdir proc-files

org_stack_names=$(ls org-files-preproc/*.nii*)
read -rd '' -a all_org_stacks <<<"$org_stack_names"

${mirtk_path}/mirtk init-dof i.dof 


for ((i=0;i<${#all_org_stacks[@]};i++));
do
    echo
    echo " - " ${i} " : " ${all_org_stacks[$i]}
    echo
    
    
    jj=$((${i}+1000))

    cp ${all_org_stacks[$i]} proc-files/org-stack-${jj}.nii.gz 


    ${mirtk_path}/mirtk pad-3d ${all_org_stacks[$i]} res-global-stacks/stack-${jj}.nii.gz 128 1 

    res=128 ; lab_num=2 ;
    current_monai_check_path=${model_path}/monai-checkpoints-unet-global-loc-2-lab/best_metric_model.pth
    python3 ${segm_path}/src/run_monai_unet_segmentation_1case-2024.py ${res} ${lab_num} ${current_monai_check_path} res-global-stacks/stack-${jj}.nii.gz out-global-masks/mask-${jj}.nii.gz

    ${mirtk_path}/mirtk extract-label out-global-masks/mask-${jj}.nii.gz out-global-masks/mask-${jj}.nii.gz 1 1

    ${mirtk_path}/mirtk extract-connected-components out-global-masks/mask-${jj}.nii.gz out-global-masks/mask-${jj}.nii.gz

    ${mirtk_path}/mirtk dilate-image out-global-masks/mask-${jj}.nii.gz out-global-masks/dl-mask-${jj}.nii.gz -iterations 2
    
    ${mirtk_path}/mirtk crop-image ${all_org_stacks[$i]} out-global-masks/dl-mask-${jj}.nii.gz  res-crop-stacks/crop-stack-${jj}.nii.gz
    ${mirtk_path}/mirtk resample-image res-crop-stacks/crop-stack-${jj}.nii.gz res-crop-stacks/crop-stack-${jj}.nii.gz -size 1.5 1.5 1.5
    ${mirtk_path}/mirtk mask-image res-crop-stacks/crop-stack-${jj}.nii.gz out-global-masks/dl-mask-${jj}.nii.gz  res-crop-stacks/crop-stack-${jj}.nii.gz
    ${mirtk_path}/mirtk pad-3d res-crop-stacks/crop-stack-${jj}.nii.gz res-crop-stacks/crop-stack-${jj}.nii.gz 128 1

    res=128 ; lab_num=4 ;
    current_monai_check_path=${model_path}/monai-checkpoints-unet-stack-body-reo-4-lab/best_metric_model.pth
    # python3 ${segm_path}/src/run_monai_atunet_segmentation_1case-2024.py ${res} ${lab_num} ${current_monai_check_path} res-crop-stacks/crop-stack-${jj}.nii.gz out-reo-masks/reo-mask-${jj}.nii.gz
	python3 ${segm_path}/src/run_monai_unet_segmentation_1case-2024.py ${res} ${lab_num} ${current_monai_check_path} res-crop-stacks/crop-stack-${jj}.nii.gz out-reo-masks/reo-mask-${jj}.nii.gz



    ${mirtk_path}/mirtk threshold-image out-reo-masks/reo-mask-${jj}.nii.gz m.nii.gz 0.5 > t.txt
    ${mirtk_path}/mirtk extract-connected-components m.nii.gz m.nii.gz 
    ${mirtk_path}/mirtk mask-image out-reo-masks/reo-mask-${jj}.nii.gz m.nii.gz out-reo-masks/reo-mask-${jj}.nii.gz


    for ((q=1;q<5;q=q+1));
    do

        ${mirtk_path}/mirtk extract-label out-reo-masks/reo-mask-${jj}.nii.gz l${q}.nii.gz ${q} ${q}
        # ${mirtk_path}/mirtk dilate-image l${q}.nii.gz l${q}.nii.gz 
        ${mirtk_path}/mirtk extract-connected-components l${q}.nii.gz l${q}.nii.gz -n 1   
        # ${mirtk_path}/mirtk erode-image l${q}.nii.gz l${q}.nii.gz 

    done 

    # q=5 
    # ${mirtk_path}/mirtk extract-label out-reo-masks/reo-mask-${jj}.nii.gz l${q}.nii.gz 2 4
    # ${mirtk_path}/mirtk extract-connected-components l${q}.nii.gz l${q}.nii.gz

    ${mirtk_path}/mirtk init-dof i.dof 
    ${mirtk_path}/mirtk register-landmarks ${atl}/v3-l1.nii.gz l1.nii.gz i.dof proc-files/d-${jj}.dof 4 4 ${atl}/mask-1.nii.gz ${atl}/mask-2.nii.gz ${atl}/mask-3.nii.gz ${atl}/mask-4.nii.gz l1.nii.gz l2.nii.gz l3.nii.gz l4.nii.gz  > t.txt

    ${mirtk_path}/mirtk transform-image out-reo-masks/reo-mask-${jj}.nii.gz proc-files/org-mask-${jj}.nii.gz -target proc-files/org-stack-${jj}.nii.gz  -labels
    
    ${mirtk_path}/mirtk threshold-image proc-files/org-mask-${jj}.nii.gz proc-files/org-mask-${jj}.nii.gz 0.5 > t.txt
    
    ${mirtk_path}/mirtk extract-label proc-files/org-mask-${jj}.nii.gz proc-files/org-thorax-mask-${jj}.nii.gz 1 2


done 


number_of_stacks=$(ls proc-files/d-*.dof | wc -l)
if [ $number_of_stacks -eq 0 ]; then
    echo 
    echo "-----------------------------------------------------------------------------"
    echo "ERROR: PROCESSING FAILED ..."
    echo "-----------------------------------------------------------------------------"
    echo 
    chmod 1777 -R ${output_main_folder}/
    exit
fi 



echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo 
echo "RUNNING STACK AND TEMPLATE SELECTION ..."
echo

${mirtk_path}/mirtk stacks-and-masks-selection-2026 selected-template.nii.gz selected-mask.nii.gz recon-files 40 1200 ${number_of_stacks} proc-files/org-stack-*.nii.gz proc-files/org-mask-*.nii.gz proc-files/d-*.dof

test_file=selected-template.nii.gz
if [ ! -f ${test_file} ];then
    echo 
    echo "-----------------------------------------------------------------------------"
    echo "ERROR: PROCESSING FAILED ..."
    echo "-----------------------------------------------------------------------------"
    echo
    chmod 1777 -R ${output_main_folder}/ 
    exit
fi 

number_of_stacks=$(ls recon-files/proc-stack-*.nii.gz | wc -l)
if [ $number_of_stacks -lt 2 ]; then
    echo 
    echo "-----------------------------------------------------------------------------"
    echo "ERROR: PROCESSING FAILED ..."
    echo "-----------------------------------------------------------------------------"
    echo 
    chmod 1777 -R ${output_main_folder}/
    exit
fi 


${mirtk_path}/mirtk resample-image ${template_path}/body-stack-reo-template-2023/ref-space.nii.gz atlas-ref.nii.gz -size 1 1 1


test_file=recon-files/reo.txt
if [ -f ${test_file} ];then

    ${mirtk_path}/mirtk transform-image selected-template.nii.gz selected-template.nii.gz -target atlas-ref.nii.gz
    ${mirtk_path}/mirtk nan selected-template.nii.gz 100000
    ${mirtk_path}/mirtk threshold-image selected-template.nii.gz m.nii.gz 0.5 > t.txt 
    ${mirtk_path}/mirtk dilate-image m.nii.gz m.nii.gz -iterations 7 
    ${mirtk_path}/mirtk crop-image selected-template.nii.gz m.nii.gz selected-template.nii.gz 
    ${mirtk_path}/mirtk transform-image selected-mask.nii.gz selected-mask.nii.gz -target selected-template.nii.gz -labels 

else 

    ${mirtk_path}/mirtk transform-image selected-template.nii.gz selected-template.nii.gz -target atlas-ref.nii.gz
    ${mirtk_path}/mirtk nan selected-template.nii.gz 100000
    ${mirtk_path}/mirtk threshold-image selected-template.nii.gz m.nii.gz 0.5 > t.txt 
    ${mirtk_path}/mirtk dilate-image m.nii.gz m.nii.gz -iterations 7
    ${mirtk_path}/mirtk crop-image selected-template.nii.gz m.nii.gz selected-template.nii.gz
    ${mirtk_path}/mirtk transform-image selected-mask.nii.gz selected-mask.nii.gz -target selected-template.nii.gz -labels 

    # ${mirtk_path}/mirtk average-images tmp-ref.nii.gz recon-files/proc-stack-*.nii.gz 
	# ${mirtk_path}/mirtk resample-image tmp-ref.nii.gz tmp-ref.nii.gz -size 1 1 1 
	# ${mirtk_path}/mirtk transform-image selected-template.nii.gz selected-template.nii.gz -target tmp-ref.nii.gz
	# ${mirtk_path}/mirtk nan selected-template.nii.gz 100000
    # ${mirtk_path}/mirtk threshold-image selected-template.nii.gz m.nii.gz 0.5 > t.txt 
    # ${mirtk_path}/mirtk crop-image selected-template.nii.gz m.nii.gz selected-template.nii.gz 
    # ${mirtk_path}/mirtk transform-image selected-mask.nii.gz selected-mask.nii.gz -target selected-template.nii.gz -labels

fi 

${mirtk_path}/mirtk dilate-image selected-mask.nii.gz dl-selected-mask.nii.gz -iterations 1


echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo 
echo "RUNNING RECONSTRUCTION ..."
echo

mkdir recon-out 
cd recon-out



#  if [ $motion_correction_mode -eq 1 ]; then

${mirtk_path}/mirtk reconstructFFD ../DSVR-output.nii.gz  ${number_of_stacks} ../recon-files/proc-stack-*.nii.gz -resolution ${recon_resolution} -iterations 3 -sr_iterations 4  -default -structural -dilation 7 -combined_rigid_ffd  -template ../selected-template.nii.gz -mask ../dl-selected-mask.nii.gz -default_thickness ${default_thickness}


# -exclusion_ncc 0.45 -exclusion_ssim 0.25 -jac_threshold 20 -delta 110 -lambda 0.018 -lastIter 0.008 -cp 12 9 

#  else 

#  fi 

 
test_file=../DSVR-output.nii.gz
if [ ! -f ${test_file} ];then
    chmod 1777 -R ${output_main_folder}/ 
    echo
    echo "-----------------------------------------------------------------------------"
    echo "ERROR: SVR RECONSTRUCTION DID NOT WORK !!!!"
    echo "-----------------------------------------------------------------------------"
    echo
    exit
fi
        

echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo 
echo "RUNNING REORIENTATION TO THE STANDARD SPACE ..."
echo

cd ${default_run_dir}
    
# ${mirtk_path}/mirtk dilate-image dl-selected-mask.nii.gz dl-selected-mask.nii.gz -iterations 1
# ${mirtk_path}/mirtk mask-image DSVR-output.nii.gz dl-selected-mask.nii.gz masked-DSVR-output.nii.gz
# ${mirtk_path}/mirtk crop-image masked-DSVR-output.nii.gz dl-selected-mask.nii.gz masked-DSVR-output.nii.gz
# ${mirtk_path}/mirtk pad-3d masked-DSVR-output.nii.gz pad-res-masked-DSVR-output.nii.gz 128 1

${mirtk_path}/mirtk pad-3d DSVR-output.nii.gz pad-res-masked-DSVR-output.nii.gz 128 1


res=128 ; lab_num=6 ;

current_monai_check_path=${segm_path}/trained_models/monai-checkpoints-unet-stack-cdh-thorax-reo-6-lab/best_metric_model.pth
python3 ${segm_path}/src/run_monai_unet_segmentation_1case-2024.py  ${res} ${lab_num} ${current_monai_check_path} pad-res-masked-DSVR-output.nii.gz reo-mask-for-DSVR-output.nii.gz


test_file=reo-mask-for-DSVR-output.nii.gz
if [ ! -f ${test_file} ];then
    chmod 1777 -R ${output_main_folder}/
    echo
    echo "-----------------------------------------------------------------------------"
    echo "ERROR: DSVR REORIENTATION DID NOT WORK !!!!"
    echo "-----------------------------------------------------------------------------"
    echo
    exit
fi
     

mkdir out-svr-reo-masks
for ((q=1;q<5;q++));
do
    ${mirtk_path}/mirtk extract-label reo-mask-for-DSVR-output.nii.gz out-svr-reo-masks/mask-${q}.nii.gz ${q} ${q}
#    ${mirtk_path}/mirtk dilate-image out-svr-reo-masks/mask-${q}.nii.gz out-svr-reo-masks/mask-${q}.nii.gz  -iterations 2
#    ${mirtk_path}/mirtk erode-image out-svr-reo-masks/mask-${q}.nii.gz out-svr-reo-masks/mask-${q}.nii.gz   -iterations 2
    ${mirtk_path}/mirtk extract-connected-components out-svr-reo-masks/mask-${q}.nii.gz out-svr-reo-masks/mask-${q}.nii.gz -n 1
done


thorax_reo_template=${template_path}/reo-spine-body-atlas

z1=1; z2=2; z3=3; z4=4; n_roi=4;
${mirtk_path}/mirtk init-dof init.dof
${mirtk_path}/mirtk register-landmarks ${thorax_reo_template}/reo-fetal-t2w-body-atlas-reo-label-all.nii.gz ${all_org_stacks[$j]} init.dof dof-to-atl.dof ${n_roi} ${n_roi} ${thorax_reo_template}/reo-label-all-${z1}.nii.gz ${thorax_reo_template}/reo-label-all-${z2}.nii.gz ${thorax_reo_template}/reo-label-all-${z3}.nii.gz ${thorax_reo_template}/reo-label-all-${z4}.nii.gz out-svr-reo-masks/mask-${z1}.nii.gz out-svr-reo-masks/mask-${z2}.nii.gz out-svr-reo-masks/mask-${z3}.nii.gz out-svr-reo-masks/mask-${z4}.nii.gz > tmp.log

${mirtk_path}/mirtk info dof-to-atl.dof
    
${mirtk_path}/mirtk resample-image ${thorax_reo_template}/ref.nii.gz  ref.nii.gz -size ${recon_resolution} ${recon_resolution} ${recon_resolution}

${mirtk_path}/mirtk transform-image DSVR-output.nii.gz reo-DSVR-output.nii.gz -target ref.nii.gz -dofin dof-to-atl.dof -interp BSpline
${mirtk_path}/mirtk threshold-image reo-DSVR-output.nii.gz tmp-m.nii.gz 0.01 > tmp.txt
${mirtk_path}/mirtk crop-image reo-DSVR-output.nii.gz tmp-m.nii.gz reo-DSVR-output.nii.gz
${mirtk_path}/mirtk nan reo-DSVR-output.nii.gz 100000
${mirtk_path}/mirtk convert-image reo-DSVR-output.nii.gz reo-DSVR-output.nii.gz -rescale 0 5000 -short

test_file=reo-DSVR-output.nii.gz
if [ ! -f ${test_file} ];then
    chmod 1777 -R ${output_main_folder}/
    echo
    echo "-----------------------------------------------------------------------------"
    echo "ERROR: REORIENTATION OF RECONSTRUCTED IMAGE DID NOT WORK !!!!"
    echo "-----------------------------------------------------------------------------"
    echo
    exit
fi


cp -r reo-DSVR-output.nii.gz ${output_main_folder}/
chmod 1777 -R ${output_main_folder}/

test_file=${output_main_folder}/reo-DSVR-output.nii.gz
if [ ! -f ${test_file} ];then

        chmod 1777 -R ${output_main_folder}/

        echo
        echo "-----------------------------------------------------------------------------"
        echo "-----------------------------------------------------------------------------"
        echo "ERROR: COULD NOT COPY THE FILES TO THE OUTPUT FOLDER : " ${output_main_folder}
        echo "PLEASE CHECK THE WRITE PERMISSIONS / LOCATION !!!"
        echo
        echo "note: you can still find the recon files in : " ${main_dir}
        echo "-----------------------------------------------------------------------------"
        echo
        exit

else 

    echo 
    echo "-----------------------------------------------------------------------------"
    echo "Reconstructed SVR results are in the output folder : " ${output_main_folder}
    echo "-----------------------------------------------------------------------------"
    echo

fi 





echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo





