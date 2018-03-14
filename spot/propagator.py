import os
from os.path import join as jph

from tools.iterative_propagator import iterative_propagator
from tools.utils import stack_a_list_of_images_from_list_pfi, get_list_pfi_images_3d_from_list_images_4d


def propagator(sp):
    """
    Propagate the atlas over the target. Parameters of the operation are in the instance of the class spot.
    :param sp: instance of a class spot.
    :return: get stack segmentation propagation of the input class in the files sp.stack_anatomies_pfi
    and sp.stack_segmentations_pfi.
    - - - -
    Part A) Each chart of the atlas is registered to the target and the segmentation propagated in different files.
    Part B) All the propagated warped and segmentations are stacked into two files.
    NOTE: folders and chart structure are completely defined in the class spot.
    """
    # A) Start iterative propagation in external module.

    iterative_propagator(sp)

    pfo_tmp = sp.scaffoldings_pfo
    pfo_target_mod = jph(sp.target_pfo, sp.arch_modalities_name_folder)

    assert os.path.exists(pfo_tmp)
    assert os.path.exists(pfo_target_mod)

    # B) After iterative propagation, now stack all the segmentations and the warped images (and sanity check).
    if sp.propagation_controller['Stack_warps_and_segms']:

        print('- Stack warps and segm {} '.format(sp.target_name))

        if len(sp.propagation_options['N_rigid_modalities']) > 0:
            # non-rigid registration
            if sp.propagation_options['Final_smoothing_factor'] > 0:
                list_pfi_warp_segm = [jph(pfo_tmp, 'segm_moving_nrigid_warp_{0}_on_target_{1}_SMOL.nii.gz').format(sj, sp.target_name) for sj in sp.atlas_list_charts_names]
            else:
                list_pfi_warp_segm = [jph(pfo_tmp, 'segm_moving_nrigid_warp_{0}_on_target_{1}.nii.gz').format(sj, sp.target_name) for sj in sp.atlas_list_charts_names]
            list_pfi_warp_mod = [jph(pfo_tmp, 'moving_nrigid_warp_{0}_on_target_{1}_mod.nii.gz').format(sj, sp.target_name) for sj in sp.atlas_list_charts_names]

        else:
            # rigid registration only
            if sp.propagation_options['Final_smoothing_factor'] > 0:
                list_pfi_warp_segm = [jph(pfo_tmp, 'segm_moving_aff_warp_{0}_on_target_{1}_SMOL.nii.gz').format(sj, sp.target_name) for sj in sp.atlas_list_charts_names]

            else:
                list_pfi_warp_segm = [jph(pfo_tmp, 'segm_moving_aff_warp_{0}_on_target_{1}.nii.gz').format(sj, sp.target_name) for sj in sp.atlas_list_charts_names]
            list_pfi_warp_mod = [jph(pfo_tmp, 'moving_aff_warp_{0}_on_target_{1}_mod.nii.gz').format(sj, sp.target_name) for sj in sp.atlas_list_charts_names]

        # Sanity check
        msg = ''
        for p in list_pfi_warp_segm:
            if not os.path.exists(p):
                msg += 'File {} in the list of segmentations does not exists. \n'.format(p)
        if not msg == '':
            raise IOError(msg)

        for p in list_pfi_warp_mod:
            if not os.path.exists(p):
                msg += 'File {} in the list of warped does not exists \n'.format(p)
        if not msg == '':
            raise IOError(msg)

        if sp.propagation_controller['Stack_warps_and_segms']:
            # -- > Create the stack segmentation:
            fin_stack_segm = '{0}_stack_warp_segm_{1}.nii.gz'.format(sp.target_name, sp.parameters_tag)
            pfi_4d_stack_warp_segm = jph(pfo_tmp, fin_stack_segm)
            stack_a_list_of_images_from_list_pfi(list_pfi_warp_segm, pfi_4d_stack_warp_segm)

            # -- > Create the stack modalities mono and multi are stacked differently:
            fin_stack_warp = '{0}_stack_warp_mod_{1}.nii.gz'.format(sp.target_name, sp.parameters_tag)
            pfi_4d_stack_warp_mod = jph(pfo_tmp, fin_stack_warp)

            stack_mono_modal = True

            if len(sp.propagation_options['N_rigid_modalities']) > 1:
                stack_mono_modal = False
            if len(sp.propagation_options['Affine_modalities']) > 1:
                if len(sp.propagation_options['N_rigid_modalities']) == 0:
                    stack_mono_modal = False

            if stack_mono_modal:
                # stack the last modality that you have warped
                stack_a_list_of_images_from_list_pfi(list_pfi_warp_mod, pfi_4d_stack_warp_mod)
            else:
                # stack_a_list_of_images_from_list_pfi(list_pfi_warp_mod, pfi_4d_stack_warp_mod, stack_dim=5)
                # extract the timepoint specified in the propagator options and then stack
                tp = sp.fuser_options['Tp_mod_to_stack']
                list_pfi_warp_mod_new = get_list_pfi_images_3d_from_list_images_4d(list_pfi_warp_mod, tp)
                stack_a_list_of_images_from_list_pfi(list_pfi_warp_mod_new, pfi_4d_stack_warp_mod)
