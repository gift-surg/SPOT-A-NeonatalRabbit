"""
A record is a .txt file containing all the parameters information of an instance of the class SPOT_DS
"""
import datetime
from os.path import join as jph
from collections import OrderedDict


def update_parameters_record(sp):
    pfi_parameters_record = jph(sp.scaffoldings_pfo, 'SPOT_parameters_records.txt')
    with open(pfi_parameters_record, 'w') as f:

        f.write('=== SPOT-A-rabbit parameters file ===\n\nTODAY : {1}\nTAG : {0}\n'.format(sp.parameters_tag, datetime.datetime.now()))
        str_atlas_and_target_data = '''
atlas_name = {0}
atlas_pfo = {1}
atlas_list_charts_names = {2}
atlas_list_suffix_modalities = {3}
atlas_reference_chart_name = {4}

target_pfo = {5}
target_name = {6}
        '''.format(sp.atlas_name,
                    sp.atlas_pfo,
                    sp.atlas_list_charts_names,
                    sp.atlas_list_suffix_modalities,
                    sp.atlas_reference_chart_name,
                    sp.target_pfo,
                    sp.target_name)

        f.write(str_atlas_and_target_data)

        # f.write('\n---Target parameters \n')
        # if isinstance(sp.target_parameters, OrderedDict) or isinstance(sp.target_parameters, dict):
        #     for k in sp.target_parameters.keys():
        #         f.write('{0:<20} : {1} \n'.format(k, sp.target_parameters[k]))
        # else:
        #     f.write('{}\n'.format(sp.target_parameters))

        f.write('\n--- Propagation options:\n')
        for k in sp.propagation_options.keys():
            f.write('{0:<40} : {1} \n'.format(k, sp.propagation_options[k]))

        f.write('\n--- Propagation controller:\n')
        for k in sp.propagation_controller.keys():
            f.write('{0:<40} : {1} \n'.format(k, sp.propagation_controller[k]))

        f.write('\n--- Fuser options:\n')
        for k in sp.fuser_options.keys():
            if isinstance(sp.fuser_options[k], OrderedDict):
                f.write('{0}\n '.format(k))
                for sub_k in sp.fuser_options[k].keys():
                    f.write('       {0:<10} : {1} \n'.format(sub_k, sp.fuser_options[k][sub_k]))
            else:
                f.write('{0:<40} : {1} \n'.format(k, sp.fuser_options[k]))

        f.write('\n--- Fuser controller:\n')
        for k in sp.fuser_controller.keys():
            f.write('{0:<40} : {1} \n'.format(k, sp.fuser_controller[k]))

        # f.write('\n--- Stereotaxic alignment options:\n')
        # for k in sp.stereotaxic_alignment_options.keys():
        #     f.write('{0:<40} : {1} \n'.format(k, sp.stereotaxic_alignment_options[k]))
        #
        # f.write('\n--- Stereotaxic alignment controller:\n')
        # for k in sp.stereotaxic_alignment_controller.keys():
        #     f.write('{0:<40} : {1} \n'.format(k, sp.stereotaxic_alignment_controller[k]))


if __name__ == '__main__':
    from spot.spotter import SpotDS
    from collections import OrderedDict
    sp = SpotDS('', '', '', '')   # dummy test!
    # extra utils:
    sp.bfc_corrector_cmd = ''
    sp.num_cores_run = 8

    # Output tagging and intermediate files
    sp.parameters_tag = 'OP1'
    sp.target_scaffoldings_folder_name = sp.arch_scaffoldings_name_folder + '_' + sp.parameters_tag
    sp.scaffoldings_pfo = '/Users/sebastiano/Desktop/test_scaffoldings'
    sp.stack_anatomies_pfi = jph(sp.scaffoldings_pfo, 'res_4d_seg.nii.gz')
    sp.stack_segmentations_pfi = jph(sp.scaffoldings_pfo, 'res_4d_warp.nii.gz')

    # Options and controller for propagation, fuser and stereotaxic alignment:
    sp.propagation_options = OrderedDict({
        'Rigid_modalities': ['T1', 'S0inT1', 'FAinT1'],
        'Rigid_masks': ['T1', 'S0inT1', 'S0inT1'],
        'Rigid_parameters': ' ',
        'N_rigid_modalities': ['T1', 'S0inT1', 'FAinT1'],  # if empty, no non-rigid step.
        'N_rigid_masks': ['T1', 'S0inT1', 'S0inT1'],
        'N_rigid_slim_reg_mask': False,
        'N_rigid_differential_bfc': True,
        'N_rigid_parameters': '  -vel -be 0.5 -ln 6 -lp 4  -smooR 0.07 -smooF 0.07 '})

    sp.propagation_controller = OrderedDict({
        'Reorient_chart_hd': True,
        'Aff_alignment': True,
        'Propagate_aff_to_segm': True,
        'Propagate_aff_to_mask': True,
        'Get_differential_BFC': True,
        'N-rig_alignment': True,
        'Propagate_to_target_n-rig': True,
        'Smooth_results': True,
        'Stack_warps_and_segms': True})

    sp.fuser_options = OrderedDict({
        'Fusion_methods': ['MV', 'STAPLE', 'STEPS'],
        'STAPLE_params': OrderedDict([('pr_1', None)]),  # (id, params)
        # k-pixels, n (5 or lower) beta
        'STEPS_params': OrderedDict([('pr_{0}_{1}'.format(k1, n), [k1, n, 0.4])
                                     for n in [5, 7, 9] for k1 in [5, 11]])})

    sp.fuser_controller = OrderedDict({
        'Fuse': True,
        'Save_results': True})

    update_parameters_record(sp)
