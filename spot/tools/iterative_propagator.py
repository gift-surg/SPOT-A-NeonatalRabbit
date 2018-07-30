"""
Module with the propagation auxiliary files.
The main propagation is divided into 2 parts.
Affine and non-rigid according to the parameter values in the spotter instance.
 ----
Note: for some combination of options, the code may create duplicate files just with different names.
This is because the preference was for the computational time in testing different options rather than memory
optimisation.
To save space (and lose debugging steps) call erase_scaffoldings after each subject spotted.
"""
import os
from os.path import join as jph

from LABelsToolkit.tools.aux_methods.utils import print_and_run

from spot.tools.utils import substitute_volume_at_timepoint_by_path, get_timepoint_by_path, \
    stack_a_list_of_images_from_list_pfi


def affine_propagator(sp):
    """
    Core of the propagation - affine part
    :param sp: instance of the class spot containing the parameters required for the cycle.
    :return: outcome of the affine registration
    """
    if sp.propagation_controller['Aff_alignment'] == False and \
                    sp.propagation_controller['Propagate_aff_to_mask'] == False and \
                    sp.propagation_controller['Propagate_aff_to_segm'] == False:
        return

    pfo_tmp = sp.scaffoldings_pfo

    pfo_target_mod   = jph(sp.target_pfo, sp.arch_modalities_name_folder)
    pfo_target_masks = jph(sp.target_pfo, sp.arch_masks_name_folder)

    # --- Prepare target affine -> Mono or Multi modal.
    num_modalities = len(sp.propagation_options['Affine_modalities'])
    # output:
    pfi_target_mod = jph(pfo_tmp, 'target_aff_{}_mod.nii.gz'.format(sp.target_name))
    pfi_target_reg_mask = jph(pfo_tmp, 'target_aff_{0}_{1}.nii.gz'.format(sp.target_name, sp.arch_suffix_masks[1]))
    # STACK modalities:
    pfi_target_mod_list = [jph(pfo_target_mod, '{0}_{1}.nii.gz'.format(sp.target_name, m))
                           for m in sp.propagation_options['Affine_modalities']]
    stack_a_list_of_images_from_list_pfi(pfi_target_mod_list, pfi_target_mod)
    # STACK reg masks:
    if not sp.propagation_options['Affine_reg_masks']:
        pfi_target_reg_mask_list = [jph(pfo_target_masks, '{0}_{1}.nii.gz'.format(sp.target_name, sp.arch_suffix_masks[1]))
                                    for _ in range(num_modalities)]
        stack_a_list_of_images_from_list_pfi(pfi_target_reg_mask_list, pfi_target_reg_mask)

    else:
        assert len(sp.propagation_options['Affine_modalities']) == len(sp.propagation_options['Affine_reg_masks'])
        pfi_target_reg_mask_list = [jph(pfo_target_masks, '{0}_{1}_{2}.nii.gz'.format(
                                                           sp.target_name, m, sp.arch_suffix_masks[1]))
                                    for m in sp.propagation_options['Affine_reg_masks']]
        stack_a_list_of_images_from_list_pfi(pfi_target_reg_mask_list, pfi_target_reg_mask)

    for sj in sp.atlas_list_charts_names:

        pfo_sj_mod   = jph(sp.atlas_pfo, sj, sp.arch_modalities_name_folder)
        pfo_sj_masks = jph(sp.atlas_pfo, sj, sp.arch_masks_name_folder)
        pfo_sj_segm  = jph(sp.atlas_pfo, sj, sp.arch_segmentations_name_folder)

        # prepare sj atlas source -> Mono / Multi modal.
        suffix_reg = '{}_on_target_{}'.format(sj, sp.target_name)
        # Output:
        pfi_moving_sj_mod      = jph(pfo_tmp, 'moving_aff_{}_mod.nii.gz'.format(sj))
        pfi_moving_sj_reg_mask = jph(pfo_tmp, 'moving_aff_{}_{}.nii.gz'.format(sj, sp.arch_suffix_masks[1]))
        # Modalities:
        pfi_sj_list_mod = [jph(pfo_sj_mod, '{0}_{1}.nii.gz'.format(sj, m)) for m in sp.propagation_options['Affine_modalities']]
        stack_a_list_of_images_from_list_pfi(pfi_sj_list_mod, pfi_moving_sj_mod)
        # Registration masks:
        pfi_sj_list_reg_masks = [jph(pfo_sj_masks, '{0}_{1}.nii.gz'.format(sj, sp.arch_suffix_masks[1])) for _ in range(num_modalities)]
        stack_a_list_of_images_from_list_pfi(pfi_sj_list_reg_masks, pfi_moving_sj_reg_mask)

        if sp.propagation_controller['Aff_alignment']:
            print('Affine alignment, subject {}'.format(sj))
            for p in [pfi_target_mod, pfi_target_reg_mask, pfi_moving_sj_mod, pfi_moving_sj_reg_mask]:
                assert os.path.exists(p), p
            # Output:
            pfi_moving_sj_on_target_aff_trans = jph(pfo_tmp, 'aff_trans_{}.txt'.format(suffix_reg))
            pfi_moving_sj_on_target_aff_warp  = jph(pfo_tmp, 'moving_aff_warp_{}_mod.nii.gz'.format(suffix_reg))
            # Command:
            cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} -omp {6} {7}'.format(
                pfi_target_mod, pfi_target_reg_mask, pfi_moving_sj_mod, pfi_moving_sj_reg_mask,
                pfi_moving_sj_on_target_aff_trans, pfi_moving_sj_on_target_aff_warp,
                sp.num_cores_run,
                sp.propagation_options['Affine_parameters'])
            # Run
            print_and_run(cmd)

        if sp.propagation_controller['Propagate_aff_to_mask']:
            print('Affine alignment, mask propagation subject {}'.format(sj))
            pfi_moving_sj_on_target_aff_trans = jph(pfo_tmp, 'aff_trans_{}.txt'.format(suffix_reg))
            assert os.path.exists(pfi_moving_sj_on_target_aff_trans), pfi_moving_sj_on_target_aff_trans
            # Output:
            pfi_moving_sj_on_target_aff_roi_mask_warp = jph(pfo_tmp, 'moving_aff_warp_{}_{}.nii.gz'.format(suffix_reg, sp.arch_suffix_masks[0]))
            pfi_moving_sj_on_target_aff_reg_mask_warp = jph(pfo_tmp, 'moving_aff_warp_{}_{}.nii.gz'.format(suffix_reg, sp.arch_suffix_masks[1]))
            # Command 1:
            cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0 '.format(
                pfi_target_mod, pfi_moving_sj_reg_mask,
                pfi_moving_sj_on_target_aff_trans, pfi_moving_sj_on_target_aff_roi_mask_warp)
            # Run
            print_and_run(cmd)
            # Command 2
            cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0 '.format(
                pfi_target_mod, pfi_moving_sj_reg_mask,
                pfi_moving_sj_on_target_aff_trans, pfi_moving_sj_on_target_aff_reg_mask_warp)
            # Run
            print_and_run(cmd)

        if sp.propagation_controller['Propagate_aff_to_segm']:
            print('Affine alignment, segmentation propagation subject {}'.format(sj))
            pfi_moving_sj_on_target_aff_trans = jph(pfo_tmp, 'aff_trans_{}.txt'.format(suffix_reg))
            pfi_segm_sj = jph(pfo_sj_segm, '{0}_{1}.nii.gz'.format(sj, sp.atlas_segmentation_suffix))
            assert os.path.exists(pfi_moving_sj_on_target_aff_trans), pfi_moving_sj_on_target_aff_trans
            # Output
            pfi_segm_sj_on_target_aff = jph(pfo_tmp, 'segm_moving_aff_warp_{}.nii.gz'.format(suffix_reg))
            # Command:
            cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0 '.format(
                pfi_target_mod, pfi_segm_sj, pfi_moving_sj_on_target_aff_trans, pfi_segm_sj_on_target_aff)
            # Run
            print_and_run(cmd)


def non_rigid_propagator(sp):
    """
    Core of the propagation - non-rigid part
    :param sp: instance of the class Spot.
    :return: outcome of the non-rigid registration
    """
    pfo_tmp = sp.scaffoldings_pfo

    pfo_target_mod = jph(sp.target_pfo, sp.arch_modalities_name_folder)
    pfo_target_masks = jph(sp.target_pfo, sp.arch_masks_name_folder)

    # --- prepare target affine -> Mono or Multi modal.
    num_modalities = len(sp.propagation_options['N_rigid_modalities'])
    target_suffix_mask = sp.arch_suffix_masks[sp.propagation_options['N_reg_mask_target']]
    moving_suffix_mask = sp.arch_suffix_masks[sp.propagation_options['N_reg_mask_moving']]
    # output:
    pfi_target_mod      = jph(pfo_tmp, 'target_nrigid_{0}_mod.nii.gz'.format(sp.target_name))
    pfi_target_reg_mask = jph(pfo_tmp, 'target_nrigid_{0}_{1}.nii.gz'.format(sp.target_name, target_suffix_mask))
    # STACK modalities:
    pfi_target_mod_list = [jph(pfo_target_mod, '{0}_{1}.nii.gz'.format(sp.target_name, m))
                           for m in sp.propagation_options['N_rigid_modalities']]
    stack_a_list_of_images_from_list_pfi(pfi_target_mod_list, pfi_target_mod)
    # STACK reg masks target:
    if len(sp.propagation_options['N_rigid_reg_masks']) == 0:
        pfi_target_reg_mask_list = [
            jph(pfo_target_masks, '{0}_{1}.nii.gz'.format(sp.target_name, target_suffix_mask))
            for _ in range(num_modalities)]
        stack_a_list_of_images_from_list_pfi(pfi_target_reg_mask_list, pfi_target_reg_mask)

    else:  # TODO every input subject must have roi_mask and reg_mask per modality.
        assert len(sp.propagation_options['N_rigid_modalities']) == len(sp.propagation_options['N_rigid_reg_masks'])
        pfi_target_reg_mask_list = [
            jph(pfo_target_masks, '{0}_{1}_{2}.nii.gz'.format(sp.target_name, m, target_suffix_mask))
            for m in sp.propagation_options['N_rigid_reg_masks']]
        stack_a_list_of_images_from_list_pfi(pfi_target_reg_mask_list, pfi_target_reg_mask)

    for sj in sp.atlas_list_charts_names:

        pfo_sj_mod = jph(sp.atlas_pfo, sj, sp.arch_modalities_name_folder)
        pfo_sj_masks = jph(sp.atlas_pfo, sj, sp.arch_masks_name_folder)

        # ---- prepare sj atlas source -> Mono / Multi modal.
        suffix_reg = '{}_on_target_{}'.format(sj, sp.target_name)
        # output:
        pfi_moving_nrigid_sj_mod      = jph(pfo_tmp, 'moving_nrigid_{}_mod.nii.gz'.format(suffix_reg))
        pfi_moving_nrigid_sj_reg_mask = jph(pfo_tmp, 'moving_nrigid_{}_{}.nii.gz'.format(suffix_reg, moving_suffix_mask))

        # -- warp not yet warped sj modalities if any.
        if sp.propagation_options['N_rigid_modalities'] != sp.propagation_options['Affine_modalities']:
            # > stack the modalities:
            pfi_target_mod_list = [jph(pfo_sj_mod, '{0}_{1}.nii.gz'.format(sj, m))
                                   for m in sp.propagation_options['N_rigid_modalities']]
            stack_a_list_of_images_from_list_pfi(pfi_target_mod_list, pfi_moving_nrigid_sj_mod)
            # > warp the stacked modalities:
            pfi_moving_sj_on_target_aff_trans = jph(pfo_tmp, 'aff_trans_{}.txt'.format(suffix_reg))
            assert os.path.exists(pfi_moving_sj_on_target_aff_trans), pfi_moving_sj_on_target_aff_trans
            cmd = 'reg_resample -ref {0} -flo {0} -trans {1} -res {0} '.format(
                pfi_moving_nrigid_sj_mod, pfi_moving_sj_on_target_aff_trans)
            print_and_run(cmd)
        else:
            # > copy the warped mod from affine registration:
            pfi_moving_sj_on_target_aff_warp = jph(pfo_tmp, 'moving_aff_warp_{}_mod.nii.gz'.format(suffix_reg))
            assert os.path.exists(pfi_moving_sj_on_target_aff_warp)
            cmd = 'cp {} {}'.format(pfi_moving_sj_on_target_aff_warp, pfi_moving_nrigid_sj_mod)
            print_and_run(cmd)

        # -- warp not yet warped reg_masks

        if sp.propagation_options['N_rigid_reg_masks'] != sp.propagation_options['Affine_reg_masks']:
            # > stack the masks:
            if not sp.propagation_options['N_rigid_reg_masks']:
                pfi_moving_reg_mask_list = [jph(pfo_sj_masks, '{0}_{1}.nii.gz'.format(sj, moving_suffix_mask))
                                            for _ in range(num_modalities)]
                stack_a_list_of_images_from_list_pfi(pfi_moving_reg_mask_list, pfi_moving_nrigid_sj_reg_mask)

            else:
                pfi_moving_reg_mask_list = [jph(pfo_sj_masks, '{0}_{1}_{2}.nii.gz'.format(sj, m, moving_suffix_mask))
                                            for m in sp.propagation_options['Affine_reg_masks']]
                stack_a_list_of_images_from_list_pfi(pfi_moving_reg_mask_list, pfi_moving_nrigid_sj_reg_mask)
            # > warp the stacked masks:
            pfi_moving_sj_on_target_aff_trans = jph(pfo_tmp, 'aff_trans_{}.txt'.format(suffix_reg))
            assert os.path.exists(pfi_moving_sj_on_target_aff_trans), pfi_moving_sj_on_target_aff_trans
            cmd = 'reg_resample -ref {0} -flo {0} -trans {1} -res {0} '.format(
                pfi_moving_nrigid_sj_reg_mask, pfi_moving_sj_on_target_aff_trans)
            print_and_run(cmd)

        else:
            # > copy the warped mask from affine registration
            pfi_moving_sj_on_target_aff_mask_warp = jph(pfo_tmp, 'moving_aff_warp_{}_{}.nii.gz'.format(suffix_reg, moving_suffix_mask))
            assert os.path.exists(pfi_moving_sj_on_target_aff_mask_warp)
            cmd = 'cp {} {}'.format(pfi_moving_sj_on_target_aff_mask_warp, pfi_moving_nrigid_sj_reg_mask)
            print_and_run(cmd)

        if sp.propagation_options['N_rigid_slim_reg_mask'] and sp.propagation_controller['Get_N_rigid_slim_mask']:
            # > Create slim registration mask (the segmentation is employed to create a mask only of the tissue).
            pfi_segm_aff_warp_sj_on_target = jph(pfo_tmp, 'segm_moving_aff_warp_{}.nii.gz'.format(suffix_reg))
            assert os.path.exists(pfi_segm_aff_warp_sj_on_target), pfi_segm_aff_warp_sj_on_target
            pfi_slim_mask_of_sj = jph(pfo_tmp, 'slim_mask_{}.nii.gz'.format(suffix_reg))
            cmd0 = 'seg_maths {0} -bin {1} '.format(pfi_segm_aff_warp_sj_on_target, pfi_slim_mask_of_sj)
            cmd1 = 'seg_maths {0} -dil 1 {0} '.format(pfi_slim_mask_of_sj)
            cmd2 = 'seg_maths {0} -ero 1 {0} '.format(pfi_slim_mask_of_sj)
            print_and_run(cmd0)
            print_and_run(cmd1)
            print_and_run(cmd2)
            # > Stack slim registration mask.
            pfi_moving_slim_mask_list = [pfi_slim_mask_of_sj for _ in range(num_modalities)]
            # output:
            pfi_moving_slim_mask_aff_warp = jph(pfo_tmp, 'moving_nrigid_{}_{}_SLIM.nii.gz'.format(suffix_reg, moving_suffix_mask))
            stack_a_list_of_images_from_list_pfi(pfi_moving_slim_mask_list, pfi_moving_slim_mask_aff_warp)

            # > Multiply slim registration mask to the final reg_mask. - save it with another name, call later with if.
            cmd = 'seg_maths {0} -mul {1} {1} '.format(pfi_moving_nrigid_sj_reg_mask, pfi_moving_slim_mask_aff_warp)
            print_and_run(cmd)

        if len(sp.propagation_options['N_rigid_mod_diff_bfc']) > 0 and sp.propagation_controller['Get_differential_BFC']:
            # Final output:
            pfi_target_mod_BFC      = jph(pfo_tmp, 'target_nrigid_{}_mod_BFC.nii.gz'.format(sp.target_name))
            pfi_moving_nrigid_mod_BFC = jph(pfo_tmp, 'moving_nrigid_{}_mod_BFC.nii.gz'.format(suffix_reg))
            # Copy non-bfc as output to be modified
            cmd = 'cp {} {}'.format(pfi_target_mod, pfi_target_mod_BFC)
            print_and_run(cmd)
            cmd = 'cp {} {}'.format(pfi_moving_nrigid_sj_mod, pfi_moving_nrigid_mod_BFC)
            print_and_run(cmd)
            for bfc_mod in sp.propagation_options['N_rigid_mod_diff_bfc']:

                timepoint = sp.propagation_options['N_rigid_modalities'].index(bfc_mod)

                # Get target slice at timepoint
                pfi_bfc_target_mod_slice = jph(pfo_tmp, 'bfc_slice_target_{0}_{1}.nii.gz'.format(sp.target_name, bfc_mod))
                get_timepoint_by_path(pfi_target_mod, timepoint, pfi_bfc_target_mod_slice)

                # Get target mask slice at timepoint
                pfi_bfc_target_reg_mask_slice = jph(pfo_tmp, 'bfc_slice_target_{0}_{1}_mask.nii.gz'.format(sp.target_name, bfc_mod))
                get_timepoint_by_path(pfi_target_reg_mask, timepoint, pfi_bfc_target_reg_mask_slice)

                # Get moving at timepoint
                pfi_bfc_moving_mod_slice = jph(pfo_tmp, 'bfc_slice_moving_{0}_{1}.nii.gz'.format(suffix_reg, bfc_mod))
                get_timepoint_by_path(pfi_moving_nrigid_sj_mod, timepoint, pfi_bfc_moving_mod_slice)

                # Get moving mask at timepoint
                pfi_bfc_moving_reg_mask_slice = jph(pfo_tmp, 'bfc_slice_moving_{0}_{1}_mask.nii.gz'.format(suffix_reg, bfc_mod))
                if sp.propagation_options['N_rigid_slim_reg_mask']:
                    pfi_moving_aff_mask = jph(pfo_tmp, 'moving_nrigid_{}_{}_SLIM.nii.gz'.format(suffix_reg, moving_suffix_mask))
                else:
                    pfi_moving_aff_mask = jph(pfo_tmp, 'moving_aff_warp_{0}_{1}.nii.gz'.format(suffix_reg, moving_suffix_mask))
                get_timepoint_by_path(pfi_moving_aff_mask, timepoint, pfi_bfc_moving_reg_mask_slice)

                # Output
                pfi_diff_bfc_target  = jph(pfo_tmp, 'bfc_{0}.nii.gz'.format(sp.target_name))
                pfi_diff_bfc_subject = jph(pfo_tmp, 'bfc_{0}.nii.gz'.format(suffix_reg))

                cmd = sp.bfc_corrector_cmd + ' {0} {1} {2} {3} {4} {5} '.format(
                    pfi_bfc_target_mod_slice, pfi_bfc_target_reg_mask_slice, pfi_diff_bfc_target,
                    pfi_bfc_moving_mod_slice, pfi_bfc_moving_reg_mask_slice, pfi_diff_bfc_subject)
                print_and_run(cmd)

                # Integrate the partial BFC output in the final output - target
                substitute_volume_at_timepoint_by_path(pfi_target_mod_BFC, pfi_diff_bfc_target, timepoint, pfi_target_mod_BFC)
                substitute_volume_at_timepoint_by_path(pfi_moving_nrigid_mod_BFC, pfi_diff_bfc_subject, timepoint, pfi_moving_nrigid_mod_BFC)

        if sp.propagation_controller['N_rigid_alignment']:
            # Input
            target_mod = pfi_target_mod
            target_mask = pfi_target_reg_mask

            moving_mod = pfi_moving_nrigid_sj_mod
            moving_mask = pfi_moving_nrigid_sj_reg_mask

            if len(sp.propagation_options['N_rigid_mod_diff_bfc']) > 0:
                target_mod = jph(pfo_tmp, 'target_nrigid_{}_mod_BFC.nii.gz'.format(sp.target_name))
                moving_mod = jph(pfo_tmp, 'moving_nrigid_{}_mod_BFC.nii.gz'.format(suffix_reg))

            if sp.propagation_options['N_rigid_slim_reg_mask']:
                moving_mask = jph(pfo_tmp, 'moving_nrigid_{}_{}_SLIM.nii.gz'.format(suffix_reg, moving_suffix_mask))

            assert os.path.exists(target_mod)
            assert os.path.exists(target_mask)
            assert os.path.exists(moving_mod)
            assert os.path.exists(moving_mask)

            if sp.propagation_options['N_rigid_same_mask_moving']:
                target_mask = moving_mask

            # Output
            pfi_cpp_nrigid_warp = jph(pfo_tmp, 'cpp_nrigid_warp_{}.nii.gz'.format(suffix_reg))
            pfi_mod_nrigid_warp = jph(pfo_tmp, 'moving_nrigid_warp_{}_mod.nii.gz'.format(suffix_reg))

            # Command
            cmd = 'reg_f3d -ref {0} -rmask {1} -flo {2} -fmask {3} -cpp {4} -res {5} -omp {6} {7}'.format(
                target_mod, target_mask, moving_mod, moving_mask,
                pfi_cpp_nrigid_warp, pfi_mod_nrigid_warp,
                sp.num_cores_run, sp.propagation_options['N_rigid_parameters'])
            print_and_run(cmd)

        if sp.propagation_controller['Propagate_n_rigid']:

            pfi_cpp_nrigid_warp = jph(pfo_tmp, 'cpp_nrigid_warp_{}.nii.gz'.format(suffix_reg))
            assert os.path.exists(pfi_cpp_nrigid_warp)

            # Propagate to reg_mask affine transformed:
            pfi_moving_sj_on_target_aff_mask_warp = jph(pfo_tmp, 'moving_aff_warp_{}_{}.nii.gz'.format(suffix_reg, moving_suffix_mask))
            assert os.path.exists(pfi_moving_sj_on_target_aff_mask_warp)

            pfi_reg_mask_sj_on_target_nrigid_warp = jph(pfo_tmp, 'moving_nrigid_warp_{}_reg_mask.nii.gz'.format(suffix_reg))
            cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
                pfi_target_mod, pfi_moving_sj_on_target_aff_mask_warp, pfi_cpp_nrigid_warp, pfi_reg_mask_sj_on_target_nrigid_warp)
            print_and_run(cmd)

            # Propagate to segm affine transformed:
            pfi_segm_sj_on_target_aff_warp = jph(pfo_tmp, 'segm_moving_aff_warp_{}.nii.gz'.format(suffix_reg))
            assert os.path.exists(pfi_segm_sj_on_target_aff_warp), pfi_segm_sj_on_target_aff_warp

            pfi_segm_sj_on_target_nrigid = jph(pfo_tmp, 'segm_moving_nrigid_warp_{}.nii.gz'.format(suffix_reg))
            cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
                pfi_target_mod, pfi_segm_sj_on_target_aff_warp, pfi_cpp_nrigid_warp,
                pfi_segm_sj_on_target_nrigid)
            print_and_run(cmd)


def iterative_propagator(sp):
    """
    Propagate all the atlas of the multi-atlas on the target according to the spot instance data.
    :param sp: instance of the class Spot.
    :return: for each subjec sj of the multi atlas we have the final segmentation and warped, ready to be stacked:
     'final_{0}_over_{1}_segm.nii.gz'.format(sj, sp.target_name)
     and 'final_{0}_over_{1}_warp.nii.gz'.format(sj, sp.target_name)
    """
    pfo_tmp = sp.scaffoldings_pfo

    # --  AFFINE  --
    affine_propagator(sp)

    # --  NON RIGID  --
    num_nrigid_modalities = len(sp.propagation_options['N_rigid_modalities'])
    if num_nrigid_modalities > 0:
        non_rigid_propagator(sp)
        resulting_segmentations_pfi_list = [jph(pfo_tmp, 'segm_moving_nrigid_warp_{0}_on_target_{1}.nii.gz').format(sj, sp.target_name)
                                            for sj in sp.atlas_list_charts_names]
    else:
        resulting_segmentations_pfi_list = [jph(pfo_tmp, 'segm_moving_aff_warp_{0}_on_target_{1}.nii.gz').format(sj, sp.target_name)
                                            for sj in sp.atlas_list_charts_names]

    # -- SMOOTHING RESULTING SEGMENTATION
    if sp.propagation_options['Final_smoothing_factor'] > 0 and sp.propagation_controller['Smooth_results']:
        for p in resulting_segmentations_pfi_list:
            assert os.path.exists(p), p
            p_new = p.replace('.nii.gz', '_SMOL.nii.gz')
            cmd = 'seg_maths {0} -smol {1} {2}'.format(p, sp.propagation_options['Final_smoothing_factor'], p_new)
            print_and_run(cmd)
