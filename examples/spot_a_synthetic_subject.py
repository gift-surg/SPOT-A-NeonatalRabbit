"""
TESTING the whole pipeline with the possible options.
Module based on phantom generated with LabelsManager - https://github.com/SebastianoF/LabelsManager
---
Each branch involved in the possible options is tested in a stand-alone branch and tested comparing ground truth
and result.
---
This module can be used as an example as well.
"""

import os
from os.path import join as jph
from collections import OrderedDict

from spot.tools.system_parameters import bfc_corrector_cmd
from spot.spotter import SpotDS
from test.test_spotter_phantom import generate_test_dataset


# parameters - use the same dataset used for testing.
ROOT_CODE = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
PATH_DIR = jph(ROOT_CODE, 'test', 'test_data')
PATH_MULTI_ATLAS = jph(PATH_DIR, 'MultiAtlas')
PATH_TARGETS = jph(PATH_DIR, 'Targets')
MULTI_ATLAS_NAME_PREFIX = 'sj'
TARGET_NAME_SUFFIX = 'ta'
N = 8
RS = 0.3
RN = 0.4


if __name__ == '__main__':
    global PATH_DIR
    generate_test_dataset(PATH_DIR)

    # --- initialise the class spot:
    target_name = '{}01'.format(TARGET_NAME_SUFFIX)
    spot_sj = SpotDS(atlas_pfo=PATH_MULTI_ATLAS,
                     target_pfo=PATH_TARGETS,
                     target_name=target_name,
                     parameters_tag='MyTag')

    # Template parameters:
    spot_sj.atlas_name = 'test'  # Multi Atlas Newborn Rabbit
    spot_sj.atlas_list_charts_names = [MULTI_ATLAS_NAME_PREFIX + str(n + 1).zfill(len(str(N)) + 1) for n in range(N)]
    spot_sj.atlas_list_suffix_modalities = ['mod1', 'mod2']
    spot_sj.atlas_list_suffix_masks = ['roi_mask', 'roi_reg_mask']
    spot_sj.atlas_reference_chart_name = 'sj02'
    spot_sj.atlas_segmentation_suffix = 'segm_GT'

    # --- target parameters
    spot_sj.target_list_suffix_modalities = ['mod1', 'mod2']

    # --- Utils
    spot_sj.bfc_corrector_cmd = bfc_corrector_cmd

    # --- Propagator option
    spot_sj.propagation_options['Affine_modalities']        = ('mod1', 'mod2')
    spot_sj.propagation_options['Affine_reg_masks']         = ()  # if (), there is a single mask for all modalities
    spot_sj.propagation_options['Affine_parameters']        = ' -speeeeed '
    spot_sj.propagation_options['N_rigid_modalities']       = ('mod1', 'mod2')  # if empty, no non-rigid step.
    spot_sj.propagation_options['N_rigid_reg_masks']        = ()  # if [], same mask for all modalities
    spot_sj.propagation_options['N_rigid_slim_reg_mask']    = True
    spot_sj.propagation_options['N_rigid_mod_diff_bfc']     = ('mod2', )  # empty list no diff bfc. - put a comma!!
    spot_sj.propagation_options['N_rigid_parameters']       = ' -vel -be 0.5 -ln 6 -lp 6  -smooR 1.5 -smooF 1.5 '
    spot_sj.propagation_options['N_rigid_same_mask_moving'] = True
    spot_sj.propagation_options['Final_smoothing_factor']   = 0

    # --- Propagator controller
    spot_sj.propagation_controller['Aff_alignment']         = True
    spot_sj.propagation_controller['Propagate_aff_to_segm'] = True
    spot_sj.propagation_controller['Propagate_aff_to_mask'] = True
    spot_sj.propagation_controller['Get_N_rigid_slim_mask'] = True
    spot_sj.propagation_controller['Get_differential_BFC']  = True
    spot_sj.propagation_controller['N_rigid_alignment']     = True
    spot_sj.propagation_controller['Propagate_n_rigid']     = True
    spot_sj.propagation_controller['Smooth_results']        = True
    spot_sj.propagation_controller['Stack_warps_and_segms'] = True

    # --- Fuser option
    spot_sj.fuser_options['Fusion_methods'] = ['MV', 'STAPLE', 'STEPS']
    spot_sj.fuser_options['Tp_mod_to_stack'] = 0
    spot_sj.fuser_options['STAPLE_params'] = OrderedDict([('pr1', None)])
    spot_sj.fuser_options['STEPS_params'] = OrderedDict([('pr{0}_{1}'.format(k, n), [k, n, 4])
                                                         for n in [9] for k in [5, 11]])
    # --- Fuser controller
    spot_sj.fuser_controller['Fuse'] = True
    spot_sj.fuser_controller['Save_results'] = True

    spot_sj.spot_on_target_initialise()
    spot_sj.propagate()
    spot_sj.fuse()

    final_msg = '\n\n-------------------------' + \
                'Synthetic target spotted! \nCheck under {} to see the resulting segmentation.\n' + \
                'Check under {} to see the intermediate files.\n' \
                'Check under {} to see a record of the parameter you selected.\n'.format(
                    jph(PATH_TARGETS, spot_sj.arch_segmentations_name_folder , spot_sj.arch_automatic_segmentations_name_folder),
                    jph(PATH_DIR, ), 3)
    print(final_msg)
