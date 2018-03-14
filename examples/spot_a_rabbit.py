from collections import OrderedDict
from os.path import join as jph

from spot.tools.system_parameters import bfc_corrector_cmd
from spot.spotter import SpotDS

if __name__ == '__main__':

    root_rabbit = '/Volumes/sebastianof/rabbits'

    # --- initialise the class spot:
    target_name = '4501'
    spot_sj = SpotDS(atlas_pfo=jph(root_rabbit, 'A_atlas'),  # here path to the folder with the atlas.
                     target_pfo=jph(root_rabbit, 'A_data/PTB/ex_vivo/{0}/stereotaxic'.format(target_name)),
                     target_name=target_name,
                     parameters_tag='P2')

    '''
    Tag-method correspondence. Check SPOT_parameters_record.txt for confirmation.
    'P1' -> Mono modal both on the affine and non-rigid, with non-rigid + BFC differentials.
    'P1' -> Mono modal both on the affine and non-rigid, with non-rigid + NO BFC.
    'P2' -> Multi modal both on the affine and non-rigid, with non-rigid and with BFC.
    'Test0' -> test with reduced atlas. all on T1 + BFC.
    'Test1' -> test with reduced atlas. all T1, no BFC yes slim mask and smol.
    'Test11' -> test with reduced atlas. T1 only affine no BFC no slim mask and no smol.
    'Test111' -> test with reduced atlas. T1 affine and non-rigid no BFC YES slim mask and no smol.
    'TestA' -> test with reduced atlas. T1, FA affine and non-rigid no BFC Yes slim mask and no smol.
    'Test2' -> test with reduced atlas. T1 FA for the affine, T1 only for the nrigid. no slim mask, no smol.
    'Test3' -> test with reduced atlas. T1 for the affine, T1, FA, S0 for the nrigid. no BFC. no slim mask, no smol.
    'Test4' -> test with reduced atlas. T1, S0 for the affine, T1, S0, FA for the nrigid. BFC for the T1. no slim mask, no smol.
    'Test5' -> test with reduced atlas. T1, S0 for the affine, T1, S0, FA for the nrigid. BFC for the T1 and S0. no slim mask, no smol.
    '''

    # Template parameters:
    spot_sj.atlas_name = 'MANRround3'  # Multi Atlas Newborn Rabbit
    spot_sj.atlas_list_charts_names = ['1201', '1203', '1305', '1404', '1507', '1510', '1702', '1805', '2002', '2502', '3301', '3404']
    spot_sj.atlas_list_suffix_modalities = ['T1', 'S0', 'V1', 'MD', 'FA']
    spot_sj.atlas_list_suffix_masks = ['roi_mask', 'roi_reg_mask']
    spot_sj.atlas_reference_chart_name = '1305'
    spot_sj.atlas_segmentation_suffix = 'approved_round3'

    # --- target parameters
    spot_sj.target_list_suffix_modalities = ['T1', 'S0', 'V1', 'MD', 'FA']
    spot_sj.target_name = target_name

    # --- Utils
    spot_sj.bfc_corrector_cmd = bfc_corrector_cmd

    # --- Propagator option
    spot_sj.propagation_options['Affine_modalities']        = ('T1', 'FA')
    spot_sj.propagation_options['Affine_reg_masks']         = ('T1', 'S0')  # if (), there is a single mask for all modalities
    spot_sj.propagation_options['Affine_parameters']        = ' -speeeeed '
    spot_sj.propagation_options['N_rigid_modalities']       = ('T1', 'FA')  # if empty, no non-rigid step.
    spot_sj.propagation_options['N_rigid_reg_masks']        = ('T1', 'S0')  # if [], same mask for all modalities
    spot_sj.propagation_options['N_rigid_slim_reg_mask']    = True
    spot_sj.propagation_options['N_rigid_mod_diff_bfc']     = ('T1', )  # empty list no diff bfc. - put a comma!!
    spot_sj.propagation_options['N_rigid_parameters']       = '  -be 0.5 -ln 6 -lp 4  -smooR 1.5 -smooF 1.5 '
    spot_sj.propagation_options['N_rigid_same_mask_moving'] = True
    spot_sj.propagation_options['Final_smoothing_factor']   = 0

    # --- Propagator controller
    spot_sj.propagation_controller['Aff_alignment']         = False
    spot_sj.propagation_controller['Propagate_aff_to_segm'] = False
    spot_sj.propagation_controller['Propagate_aff_to_mask'] = False
    spot_sj.propagation_controller['Get_N_rigid_slim_mask'] = True
    spot_sj.propagation_controller['Get_differential_BFC']  = True
    spot_sj.propagation_controller['N_rigid_alignment']     = True
    spot_sj.propagation_controller['Propagate_n_rigid']     = True
    spot_sj.propagation_controller['Smooth_results']        = True
    spot_sj.propagation_controller['Stack_warps_and_segms'] = True

    # --- Fuser option
    spot_sj.fuser_options['Fusion_methods']  = ['MV']  # 'MV', 'STAPLE',
    spot_sj.fuser_options['Tp_mod_to_stack'] = 0
    spot_sj.fuser_options['STAPLE_params']   = OrderedDict([('pr1', None)])
    spot_sj.fuser_options['STEPS_params']    = OrderedDict([('pr{0}_{1}'.format(k, n), [k, n, 4])
                                                         for n in [9] for k in [5,  11]])
    # --- Fuser controller
    spot_sj.fuser_controller['Fuse']         = True
    spot_sj.fuser_controller['Save_results'] = True

    spot_sj.spot_on_target_initialise()
    spot_sj.propagate()
    spot_sj.fuse()

