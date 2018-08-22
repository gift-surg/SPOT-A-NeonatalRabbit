import os
from os.path import join as jph

from nilabel.tools.aux_methods.utils import print_and_run
from nilabel.tools.aux_methods.sanity_checks import check_path_validity


def fuser(sp):

    print('Apply the nifty-seg fusion method {}'.format(sp.target_pfo))

    pfo_tmp = sp.scaffoldings_pfo
    assert os.path.exists(pfo_tmp)

    if sp.fuser_controller['Fuse']:
        print('- Fuse {} '.format(sp.target_name))

        # file-names and file-paths of the resulting stacks:
        fin_stack_segm = '{0}_stack_warp_segm_{1}.nii.gz'.format(sp.target_name, sp.parameters_tag)
        fin_stack_warp = '{0}_stack_warp_mod_{1}.nii.gz'.format(sp.target_name, sp.parameters_tag)

        pfi_4d_stack_warp_segm = jph(pfo_tmp, fin_stack_segm)
        pfi_4d_stack_warp_mod = jph(pfo_tmp, fin_stack_warp)

        assert os.path.exists(pfi_4d_stack_warp_segm)
        assert os.path.exists(pfi_4d_stack_warp_mod)

        # ------------ MV ------------
        pfi_output_MV = jph(pfo_tmp, 'result_{0}_MV_{1}.nii.gz'.format(sp.target_name, sp.parameters_tag))
        if 'MV' in sp.fuser_options['Fusion_methods']:
            cmd_mv = 'seg_LabFusion -in {0} -out {1} -MV'.format(pfi_4d_stack_warp_segm, pfi_output_MV)
            print_and_run(cmd_mv, short_path_output=False)
            assert check_path_validity(pfi_output_MV, timeout=5000, interval=5)

        # -------- STAPLE ------------
        if 'STAPLE' in sp.fuser_options['Fusion_methods']:
            for key_staple in sp.fuser_options['STAPLE_params'].keys():
                pfi_output_STAPLE = jph(pfo_tmp, 'result_{0}_STAPLE_{1}_{2}.nii.gz'.format(sp.target_name, key_staple, sp.parameters_tag))
                beta = sp.fuser_options['STAPLE_params'][key_staple]
                if beta is None:
                    cmd_staple = 'seg_LabFusion -in {0} -STAPLE -out {1}'.format(pfi_4d_stack_warp_segm, pfi_output_STAPLE)
                else:
                    cmd_staple = 'seg_LabFusion -in {0} -STAPLE -out {1} -MRF_beta {2}'.format(pfi_4d_stack_warp_segm, pfi_output_STAPLE, beta)

                print_and_run(cmd_staple, short_path_output=False)
                assert check_path_validity(pfi_output_STAPLE, timeout=5000, interval=5)

        # ------------ STEPS ------------
        if 'STEPS' in sp.fuser_options['Fusion_methods']:
            # select the path to target:
            if len(sp.propagation_options['N_rigid_modalities']) > 0:
                if len(sp.propagation_options['N_rigid_mod_diff_bfc']) > 0:
                    pfi_target = jph(pfo_tmp, 'target_nrigid_{}_mod_BFC.nii.gz'.format(sp.target_name))
                else:
                    pfi_target = jph(pfo_tmp, 'target_nrigid_{}_mod.nii.gz'.format(sp.target_name))
            else:
                pfi_target = sp.propagation_options['N_rigid_modalities'] = jph(pfo_tmp, 'target_aff_{}_mod.nii.gz'.format(sp.target_name))

            assert os.path.exists(pfi_target)

            for key_steps in sp.fuser_options['STEPS_params'].keys():
                pfi_output_STEPS = jph(pfo_tmp, 'result_{0}_STEPS_{1}_{2}.nii.gz'.format(sp.target_name, key_steps, sp.parameters_tag))
                k, n, beta = sp.fuser_options['STEPS_params'][key_steps]
                if beta is None:
                    cmd_steps = 'seg_LabFusion -in {0} -out {1} -STEPS {2} {3} {4} {5} -prop_update'.format(
                        pfi_4d_stack_warp_segm,
                        pfi_output_STEPS,
                        k,
                        n,
                        pfi_target,
                        pfi_4d_stack_warp_mod)
                else:
                    cmd_steps = 'seg_LabFusion -in {0} -out {1} -STEPS {2} {3} {4} {5} -MRF_beta {5}  -prop_update '.\
                        format(pfi_4d_stack_warp_segm,
                               pfi_output_STEPS,
                               k,
                               n,
                               pfi_target,
                               pfi_4d_stack_warp_mod,
                               str(beta))
                print_and_run(cmd_steps, short_path_output=False)
                assert check_path_validity(pfi_output_STEPS, timeout=1000, interval=10)

    if sp.fuser_controller['Save_results']:

        print('- save result for target subject {}'.format(sp.target_name))

        pfo_automatic_segmentations_results = jph(sp.target_pfo, sp.arch_segmentations_name_folder,
                                                  sp.arch_automatic_segmentations_name_folder)

        cmd0 = 'mkdir -p {}'.format(jph(sp.target_pfo, sp.arch_segmentations_name_folder))
        cmd1 = 'mkdir -p {}'.format(pfo_automatic_segmentations_results)
        print_and_run(cmd0)
        print_and_run(cmd1)

        for filename in os.listdir(pfo_tmp):
            if filename.startswith('result_'):
                cmd = 'cp {0} {1}'.format(jph(pfo_tmp, filename),
                                          jph(pfo_automatic_segmentations_results, filename.replace('result_', '')))
                print_and_run(cmd)
