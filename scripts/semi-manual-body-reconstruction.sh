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

echo "Setting environment ... "
echo

source ~/.bashrc

#eval "$(conda shell.bash hook)"
#
#conda init bash
#
#conda activate Segmentation_FetalMRI_MONAI
#


#NOTE: UPDATE AS REQUIRED BEFORE RUNNING !!!!
#NOTE - BEFORE USING: UPLOAD https://gin.g-node.org/SVRTK/fetal_mri_network_weights
#
#echo "NOTE: UPDATE SOFTWARE PAHTS AS REQUIRED BEFORE RUNNING !!!!"
#echo "NOTE: DOWNLOAD MONAI WEIGHTS INTO auto-proc-svrtk/trained_models FOLDER FROM https://gin.g-node.org/SVRTK/fetal_mri_network_weights"
#
#exit


software_path=/home

default_run_dir=/home/tmp_proc

segm_path=${software_path}/auto-proc-svrtk

dcm2niix_path=/bin/dcm2niix/build/bin

mirtk_path=/bin/MIRTK/build/bin

template_path=${segm_path}/templates

model_path=${segm_path}/trained_models




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
echo "SVRTK for fetal MRI (KCL): manual body DSVR reconstruction and auto reorientation for TSE T2w fetal MRI"
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

if [ $# -ne 4 ] ; then

    if [ $# -ne 8 ] ; then
        echo "Usage: bash /home/auto-proc-svrtk/scripts/semi-manual-body-reconstruction.sh"
        echo "            [FULL path to the folder with raw T2w stacks in .nii or .dcm, e.g., /home/data/test]"
        echo "            [FULL path to the folder for recon results, e.g., /home/data/out-test]"
        echo "            [FULL path to the .nii/.nii.gz template file, e.g., /home/data/test/template.nii.gz]"
        echo "            [FULL path to the .nii/.nii.gz mask file, e.g., /home/data/test/mask.nii.gz]"
        echo "            (optional) [motion correction mode (0 or 1): 0 - minor, 1 - >180 degree rotations] - default: 0"
        echo "            (optional) [slice thickness] - default: 3.0"
        echo "            (optional) [output recon resolution] - default: 0.8"
        echo "            (optional) [number of packages] - default: 1"
        echo
        exit
    else
        input_main_folder=$1
        output_main_folder=$2
        man_template=$3
        man_mask=$4
        motion_correction_mode=$5
        default_thickness=$6
        recon_resolution=$7
        num_packages=$8
    fi
    
else
    input_main_folder=$1
    output_main_folder=$2
    man_template=$3
    man_mask=$4
    motion_correction_mode=0
    default_thickness=3.0
    recon_resolution=0.8
    num_packages=1
fi


echo " - input folder : " ${input_main_folder}
echo " - output folder : " ${output_main_folder}
echo " - template : " ${man_template}
echo " - mask : " ${man_mask}
echo " - motion correction mode : " ${motion_correction_mode}
echo " - slice thickness : " ${default_thickness}
echo " - output resolution : " ${recon_resolution}


recon_roi=body


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

rm *mask*
rm *label*

stack_names=$(ls *.nii*)
read -rd '' -a all_stacks <<<"$stack_names"

echo
echo "-----------------------------------------------------------------------------"
echo "REMOVING NAN & NEGATIVE/EXTREME VALUES & SPLITTING INTO DYNAMICS ..."
echo "-----------------------------------------------------------------------------"
echo

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
echo "RUNNING RECONSTRUCTION ..."
echo

cd ${main_dir}


if [ $recon_roi = "body" ]; then

    echo
    echo "-----------------------------------------------------------------------------"
    echo "SELECTING STACKS / GENERATING TEMPLATE ..."
    echo "-----------------------------------------------------------------------------"
    echo
    
    cd ${main_dir}
    
    recon_roi_global=body
    

    echo
    echo "-----------------------------------------------------------------------------"
    echo "DSVR RECONSTRUCTION ..."
    echo "-----------------------------------------------------------------------------"
    echo

    mkdir out-recon-files-${recon_roi}
    cd out-recon-files-${recon_roi}
    number_of_stacks=$(ls ../org-files-preproc/*.nii* | wc -l)
    
    recon_roi_out=body
    

    ${mirtk_path}/mirtk reconstructFFD ../DSVR-output-${recon_roi_out}.nii.gz  ${number_of_stacks} ../org-files-preproc/*.nii* -mask ${man_mask} -template ${man_template} -default_thickness ${default_thickness} -resolution ${recon_resolution} -iterations 2 -cp 12 9 -default -structural -dilation 7 -delta 110 -lambda 0.018 -lastIter 0.008 -combined_rigid_ffd -exclusion_ncc 0.45 -exclusion_ssim 0.25 -jac_threshold 20
    
    
    test_file=../DSVR-output-${recon_roi_out}.nii.gz
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
    echo "REORIENTATION TO THE STANDARD SPACE ..."
    echo "-----------------------------------------------------------------------------"
    echo
    
    cd ${main_dir}


    number_of_stacks=1
    roi=body
    res=128
    monai_lab_num=6
    
    echo " ... "
    
#    ${mirtk_path}/mirtk mask-image DSVR-output-${recon_roi_out}.nii.gz average-thorax-reo-mask.nii.gz   masked-DSVR-output-${recon_roi_out}.nii.gz
#
#    ${mirtk_path}/mirtk crop-image masked-DSVR-output-${recon_roi_out}.nii.gz average-thorax-reo-mask.nii.gz   masked-DSVR-output-${recon_roi_out}.nii.gz
    
    ${mirtk_path}/mirtk prepare-for-monai res-svr-files/ svr-files/ reo-svr-info.json reo-svr-info.csv ${res} ${number_of_stacks} DSVR-output-${recon_roi_out}.nii.gz > tmp.log

    # current_monai_check_path=${model_path}/monai-checkpoints-unet-thorax-reo-4-lab-cmr

    # current_monai_check_path=/home/data/monai-checkpoints-unet-3t-reo_ogans-4-lab

#    current_monai_check_path=/home/auto-proc-svrtk/trained_models/monai-checkpoints-unet-thorax-reo-4-lab-cmr

    current_monai_check_path=${segm_path}/trained_models/monai-checkpoints-unet-stack-cdh-thorax-reo-6-lab

    
    mkdir monai-segmentation-results-svr-reo
    python3 ${segm_path}/src/run_monai_unet_segmentation-rot-180-2024.py ${main_dir}/ ${current_monai_check_path}/ reo-svr-info.json ${main_dir}/monai-segmentation-results-svr-reo ${res} ${monai_lab_num}
    
    
    number_of_stacks=$(find monai-segmentation-results-svr-reo/ -name "*.nii*" | wc -l)
    if [ ${number_of_stacks} -eq 0 ];then

        chmod 1777 -R ${output_main_folder}/

        echo
        echo "-----------------------------------------------------------------------------"
        echo "ERROR: REO CNN LOCALISATION DID NOT WORK !!!!"
        echo "-----------------------------------------------------------------------------"
        echo
        exit
    fi
    
    mkdir out-svr-reo-masks
    for ((q=1;q<5;q++));
    do
        ${mirtk_path}/mirtk extract-label monai-segmentation-results-svr-reo/cnn* out-svr-reo-masks/mask-${q}.nii.gz ${q} ${q}
#        ${mirtk_path}/mirtk erode-image out-svr-reo-masks/mask-${q}.nii.gz out-svr-reo-masks/mask-${q}.nii.gz  -iterations 1
        # ${mirtk_path}/mirtk erode-image out-svr-reo-masks/mask-${q}.nii.gz out-svr-reo-masks/mask-${q}.nii.gz   -iterations 1
        ${mirtk_path}/mirtk extract-connected-components out-svr-reo-masks/mask-${q}.nii.gz out-svr-reo-masks/mask-${q}.nii.gz -n 1

    done


    thorax_reo_template=${template_path}/reo-spine-body-atlas

    z1=1; z2=2; z3=3; z4=4; n_roi=4;
    ${mirtk_path}/mirtk init-dof init.dof
    
     ${mirtk_path}/mirtk register-landmarks ${thorax_reo_template}/reo-fetal-t2w-body-atlas-reo-label-all.nii.gz ${man_mask} init.dof dof-to-atl-${recon_roi}.dof ${n_roi} ${n_roi} ${thorax_reo_template}/reo-label-all-${z1}.nii.gz ${thorax_reo_template}/reo-label-all-${z2}.nii.gz ${thorax_reo_template}/reo-label-all-${z3}.nii.gz ${thorax_reo_template}/reo-label-all-${z4}.nii.gz out-svr-reo-masks/mask-${z1}.nii.gz out-svr-reo-masks/mask-${z2}.nii.gz out-svr-reo-masks/mask-${z3}.nii.gz out-svr-reo-masks/mask-${z4}.nii.gz  > tmp.log

    ${mirtk_path}/mirtk info dof-to-atl-${recon_roi}.dof
    
#    recon_resolution=1.2
    ${mirtk_path}/mirtk resample-image  ${thorax_reo_template}/ref.nii.gz ref.nii.gz -size ${recon_resolution} ${recon_resolution} ${recon_resolution} -interp BSpline

    ${mirtk_path}/mirtk transform-image DSVR-output-${recon_roi_out}.nii.gz reo-DSVR-output-${recon_roi_out}.nii.gz -target ref.nii.gz -dofin dof-to-atl-${recon_roi}.dof -interp BSpline
    ${mirtk_path}/mirtk threshold-image reo-DSVR-output-${recon_roi_out}.nii.gz tmp-m.nii.gz 0.01 > tmp.txt
    ${mirtk_path}/mirtk crop-image reo-DSVR-output-${recon_roi_out}.nii.gz tmp-m.nii.gz reo-DSVR-output-${recon_roi_out}.nii.gz
    ${mirtk_path}/mirtk nan reo-DSVR-output-${recon_roi_out}.nii.gz 100000
    ${mirtk_path}/mirtk convert-image reo-DSVR-output-${recon_roi_out}.nii.gz reo-DSVR-output-${recon_roi_out}.nii.gz -rescale 0 5000 -short

#    rm masked-DSVR-output-${recon_roi_out}.nii.gz

    test_file=reo-DSVR-output-${recon_roi_out}.nii.gz
    if [ ! -f ${test_file} ];then

        chmod 1777 -R ${output_main_folder}/
        
        echo
        echo "-----------------------------------------------------------------------------"
        echo "ERROR: REORIENTATION OF RECONSTRUCTED IMAGE DID NOT WORK !!!!"
        echo "-----------------------------------------------------------------------------"
        echo
        exit
    fi
    

    test_file=reo-DSVR-output-${recon_roi_out}.nii.gz
    if [ -f ${test_file} ];then

        cp -r reo-DSVR-output-${recon_roi_out}.nii.gz ${output_main_folder}/
#        cp -r average_mask_cnn.nii.gz ${output_main_folder}/

        echo "-----------------------------------------------------------------------------"
        echo "Reconstructed SVR results are in the output folder : " ${output_main_folder}
        echo "-----------------------------------------------------------------------------"

        chmod 1777 -R ${output_main_folder}/
        
    else
        echo
        echo "-----------------------------------------------------------------------------"
        echo "ERROR: COULD NOT COPY THE FILES TO THE OUTPUT FOLDER : " ${output_main_folder}
        echo "PLEASE CHECK THE WRITE PERMISSIONS / LOCATION !!!"
        echo
        # echo "note: you can still find the recon files in : " ${main_dir}
        echo "-----------------------------------------------------------------------------"
        echo

        chmod 1777 -R ${output_main_folder}/

        exit
    fi

fi


echo
echo "-----------------------------------------------------------------------------"
echo "-----------------------------------------------------------------------------"
echo





