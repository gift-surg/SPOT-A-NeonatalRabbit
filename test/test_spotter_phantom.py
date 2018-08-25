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
import nibabel as nib

from nose.tools import assert_raises

from spot.tools.system_parameters import bfc_corrector_cmd
from spot.spotter import SpotDS

from nilabels.tools.phantoms_generator.generate_phantom_multi_atlas import generate_multi_atlas_at_folder, \
    generate_atlas_at_folder

from nilabels.tools.caliber.distances import global_dice_score


# parameters
PATH_DIR = jph(os.path.dirname(os.path.realpath(__file__)), 'test_data')
PATH_MULTI_ATLAS = jph(PATH_DIR, 'MultiAtlas')
PATH_TARGETS = jph(PATH_DIR, 'Targets')
MULTI_ATLAS_NAME_PREFIX = 'sj'
TARGET_NAME_SUFFIX = 'ta'
N = 8
RS = 0.3
RN = 0.4


def generate_phantom_dataset(path_dir):
    if not os.path.exists(jph(path_dir)):
        print('\n\nGenerating dataset for testing: phantom multi-atlas and phantom target in {}. '
              'Will take some minutes.'.format(path_dir))
        os.system('mkdir {}'.format(path_dir))
        os.system('mkdir {}'.format(jph(path_dir, 'MultiAtlas')))
        os.system('mkdir {}'.format(jph(path_dir, 'Targets')))
        generate_multi_atlas_at_folder(jph(path_dir, 'MultiAtlas'), number_of_subjects=N,
                                       multi_atlas_root_name=MULTI_ATLAS_NAME_PREFIX,
                                       randomness_shape=RS, randomness_noise=RN)
        generate_atlas_at_folder(jph(path_dir, 'Targets'), atlas_name='{}01'.format(TARGET_NAME_SUFFIX),
                                 randomness_shape=RS, randomness_noise=RN)


def test_standard_experiment_with_phantom():

    global PATH_DIR
    generate_phantom_dataset(PATH_DIR)

    # # --- initialise the class spot:
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
    spot_sj.propagation_options['Affine_modalities'] = ('mod1', 'mod2')
    spot_sj.propagation_options['Affine_reg_masks'] = ()  # if (), there is a single mask for all modalities
    spot_sj.propagation_options['Affine_parameters'] = ' -speeeeed '
    spot_sj.propagation_options['N_rigid_modalities'] = ('mod1', 'mod2')  # if empty, no non-rigid step.
    spot_sj.propagation_options['N_rigid_reg_masks'] = ()  # if (), same mask for all modalities
    spot_sj.propagation_options['N_rigid_slim_reg_mask'] = True
    spot_sj.propagation_options['N_rigid_mod_diff_bfc'] = ('mod2',)  # empty list no diff bfc. - put a comma!!
    spot_sj.propagation_options['N_rigid_parameters'] = ' -vel -be 0.5 -ln 6 -lp 2  -smooR 1.5 -smooF 1.5 '
    spot_sj.propagation_options['N_rigid_same_mask_moving'] = True
    spot_sj.propagation_options['Final_smoothing_factor'] = 0

    # --- Propagator controller
    spot_sj.propagation_controller['Aff_alignment'] = True
    spot_sj.propagation_controller['Propagate_aff_to_segm'] = True
    spot_sj.propagation_controller['Propagate_aff_to_mask'] = True
    spot_sj.propagation_controller['Get_N_rigid_slim_mask'] = True
    spot_sj.propagation_controller['Get_differential_BFC'] = True
    spot_sj.propagation_controller['N_rigid_alignment'] = True
    spot_sj.propagation_controller['Propagate_n_rigid'] = True
    spot_sj.propagation_controller['Smooth_results'] = True
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

    if not os.path.exists(jph(PATH_TARGETS, spot_sj.arch_segmentations_name_folder, spot_sj.arch_automatic_segmentations_name_folder)):
        spot_sj.spot_on_target_initialise()
        spot_sj.propagate()
        spot_sj.fuse()
    #
    pfi_ground_truth_segm = jph(PATH_TARGETS, spot_sj.arch_segmentations_name_folder,
                                '{0}_{1}.nii.gz'.format(target_name, spot_sj.atlas_segmentation_suffix))
    pri_result_MV         = jph(PATH_TARGETS, spot_sj.arch_segmentations_name_folder,
                                spot_sj.arch_automatic_segmentations_name_folder,
                                '{0}_{1}_{2}.nii.gz'.format(target_name, 'MV',
                                                            spot_sj.parameters_tag))
    im_segm_gt = nib.load(pfi_ground_truth_segm)
    im_segm_mv = nib.load(pri_result_MV)

    assert global_dice_score(im_segm_gt, im_segm_mv) > 0.9


def test_standard_experiments_with_phantom_broken_input_tag():

    global PATH_DIR
    generate_phantom_dataset(PATH_DIR)

    target_name = '{}01'.format(TARGET_NAME_SUFFIX)

    with assert_raises(TypeError):
        SpotDS(atlas_pfo=PATH_MULTI_ATLAS,
               target_pfo=PATH_TARGETS,
               target_name=target_name,
               parameters_tag=None)  # error here

    spot_sj = SpotDS(atlas_pfo=PATH_MULTI_ATLAS,
                     target_pfo=PATH_TARGETS,
                     target_name=target_name,
                     parameters_tag='')  # error here

    spot_sj.spot_on_target_initialise()
    with assert_raises(IOError):
        spot_sj.propagate()

    spot_sj = SpotDS(atlas_pfo=PATH_MULTI_ATLAS,
                     target_pfo=PATH_TARGETS,
                     target_name=target_name,
                     parameters_tag='a_b')  # error here

    spot_sj.spot_on_target_initialise()
    with assert_raises(IOError):
        spot_sj.propagate()

