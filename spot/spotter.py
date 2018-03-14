import os
from os.path import join as jph
from collections import OrderedDict

from .propagator import propagator
from .fuser import fuser
from .tools.records_manager import update_parameters_record
from .tools.system_parameters import bfc_corrector_cmd


class SpotDS(object):
    """
    SPOT Class is a factory / data structure containing the parameters, paths and file names of the multi-atlas
    and the target.
    This class represents the main architecture of SPOT (segmentation propagation on target).
    Every parameter of the whole process of : propagation - fusion - integration : is here.
    --
    In future version this can be refactored with a data structure parser for specific YAML file.
    --
    The input atlas modalities (T1, FA, ...) are aligned in the same space.
    of the target modalities (T1, FA, ...) are aligned in the same space.
    ---
    Options of each stage (propagation, fusion, stereotaxic_alignment) are governed by the _options attributes:
    > propagation_options, fusion_options, stereotaxic_alignment_options
    Controller of each stage (propagation, fusion, stereotaxic_alignment) are governed by the _controller attributes:
    > propagation_controller, fusion_controller, stereotaxic_alignment_controller
    These are created for debugging purposes and enable to turn on or off each step independently.
    ---
    In the propagation options, the modalities needs to corresponds to the one in the atlases:
    if T1inS0 of the target will corresponds to the S0 in the atlas.
    Masks specifying the modalities needs to be provided in the same order.
    """
    def __init__(self, atlas_pfo, target_pfo, target_name, parameters_tag):
        # atlas
        self.atlas_name = ''
        self.atlas_pfo = atlas_pfo
        self.atlas_list_charts_names = []
        self.atlas_list_suffix_modalities = ['T1', 'S0', 'V1', 'MD', 'FA']
        self.atlas_reference_chart_name = '1305'
        self.atlas_segmentation_suffix = '_approved_round3'
        # target
        self.target_pfo = target_pfo
        self.target_name = target_name
        # folder structure - naming conventions
        self.arch_modalities_name_folder     = 'mod'
        self.arch_masks_name_folder          = 'masks'
        self.arch_segmentations_name_folder  = 'segm'
        self.arch_scaffoldings_name_folder   = 'z_SPOT'
        self.arch_suffix_masks = ['roi_mask', 'reg_mask']  # first ROI, second masks out artefacts for registration.
        self.arch_automatic_segmentations_name_folder  = 'automatic'
        self.arch_approved_segmentation_prefix         = 'result_'

        # extra utils:
        self.bfc_corrector_cmd = bfc_corrector_cmd
        self.num_cores_run = 8

        # Output tagging and intermediate files
        self.parameters_tag = parameters_tag  # most important information.
        self.target_scaffoldings_folder_name = self.arch_scaffoldings_name_folder + '_' + self.parameters_tag
        self.scaffoldings_pfo = jph(target_pfo, self.target_scaffoldings_folder_name)

        # Options for propagation
        self.propagation_options = OrderedDict()

        self.propagation_options['Affine_modalities']      = ('T1', 'FA')
        self.propagation_options['Affine_reg_masks']       = ('T1', 'S0')  # if [], same mask for all modalities
        self.propagation_options['Affine_parameters']      = ' '
        self.propagation_options['N_rigid_modalities']     = ('T1', 'FA')  # if empty, no non-rigid step.
        self.propagation_options['N_rigid_reg_masks']      = ('T1', 'S0')  # if [], same mask for all modalities
        self.propagation_options['N_rigid_slim_reg_mask']  = False
        self.propagation_options['N_rigid_mod_diff_bfc']   = ('T1', )  # empty list no diff bfc.
        self.propagation_options['N_rigid_parameters']     = '  -vel -be 0.5 -ln 6 -lp 4  -smooR 0.07 -smooF 0.07 '
        self.propagation_options['Final_smoothing_factor'] = 0

        # Controller for propagation
        self.propagation_controller = OrderedDict()

        self.propagation_controller['Aff_alignment']         = True
        self.propagation_controller['Propagate_aff_to_segm'] = True
        self.propagation_controller['Propagate_aff_to_mask'] = True
        self.propagation_controller['Get_N_rigid_slim_mask'] = True
        self.propagation_controller['Get_differential_BFC']  = True
        self.propagation_controller['N_rigid_alignment']     = True
        self.propagation_controller['Propagate_n_rigid']     = True
        self.propagation_controller['Smooth_results']        = True
        self.propagation_controller['Stack_warps_and_segms'] = True

        # Option for fuser:
        self.fuser_options = OrderedDict()

        self.fuser_options['Fusion_methods'] = ['MV', 'STAPLE', 'STEPS']
        self.fuser_options['Tp_mod_to_stack'] = 1  # if multi modal, only this timepoint of the warped modality will be considered to create the stack.
        self.fuser_options['STAPLE_params'] = OrderedDict([('pr_1', None)])
        self.fuser_options['STEPS_params'] = OrderedDict([('pr_{0}_{1}'.format(k, n), [k, n, 0.4])
                                                             for n in [5, 7, 9] for k in [5,  11]])

        # Controller for fuser:
        self.fuser_controller = OrderedDict()

        self.fuser_controller['Fuse']         = True
        self.fuser_controller['Save_results'] = True

    def _check_multi_atlas_structure(self):
        if self.parameters_tag == '' or self.parameters_tag is None or '_' in self.parameters_tag:
            msg = 'parameters_tag can not be empty string or None. Can not contain underscores.'
            raise IOError(msg)
        msg = ''
        for chart_name in self.atlas_list_charts_names:
            for mod_j in self.atlas_list_suffix_modalities:
                p = jph(self.atlas_pfo, chart_name, self.arch_modalities_name_folder,
                        '{0}_{1}.nii.gz'.format(chart_name, mod_j))
                if not os.path.exists(p):
                    msg += 'File {} does not exist. \n'.format(p)
            for mask_j in self.arch_suffix_masks:
                p = jph(self.atlas_pfo, chart_name, self.arch_masks_name_folder,
                        '{0}_{1}.nii.gz'.format(chart_name, mask_j))
                if not os.path.exists(p):
                    msg += 'File {} does not exist. \n'.format(p)
            p = jph(self.atlas_pfo, chart_name, self.arch_segmentations_name_folder,
                    '{0}_{1}.nii.gz'.format(chart_name, self.atlas_segmentation_suffix))
            if not os.path.exists(p):
                msg += 'File {} does not exist. \n'.format(p)
        if msg is not '':
            raise IOError(msg)

    def _check_target_structure(self):
        msg = ''
        # Check modalities:
        list_mods = list(set(self.propagation_options['Affine_modalities'] + self.propagation_options['N_rigid_modalities']))
        for mod_j in list_mods:
            p = jph(self.target_pfo, self.arch_modalities_name_folder,
                    '{0}_{1}.nii.gz'.format(self.target_name, mod_j))
            if not os.path.exists(p):
                msg += 'File {} does not exist. \n'.format(p)
        # Check modalities are in the multi atlas:
        assert set(list_mods).union(set(self.atlas_list_suffix_modalities)) == set(self.atlas_list_suffix_modalities)
        # Check single roi mask for all modality:
        p = jph(self.target_pfo, self.arch_masks_name_folder, '{0}_{1}.nii.gz'.format(self.target_name, self.arch_suffix_masks[0]))
        if not os.path.exists(p):
            msg += 'File {} does not exist. \n'.format(p)
        # Check specific reg mask for each modality or the single reg mask:
        list_mod_reg_masks = list(set(self.propagation_options['Affine_reg_masks'] + self.propagation_options['N_rigid_reg_masks']))
        if len(list_mod_reg_masks) > 0:
            for mask_mod_j_category in list_mod_reg_masks:
                p = jph(self.target_pfo, self.arch_masks_name_folder,
                        '{0}_{1}_{2}.nii.gz'.format(self.target_name, mask_mod_j_category, self.arch_suffix_masks[1]))
                if not os.path.exists(p):
                    msg += 'File {} does not exist. \n'.format(p)
        else:
            p = jph(self.target_pfo, self.arch_masks_name_folder,
                        '{0}_{1}.nii.gz'.format(self.target_name, self.arch_suffix_masks[1]))
            if not os.path.exists(p):
                msg += 'File {} does not exist. \n'.format(p)

        if msg is not '':
            raise IOError(msg)

    def _check_propagation_options(self):
        # Sanity check, tuple where there should be:
        msg = 'Keys in propagation_options - Affine_modalities Affine_reg_masks N_rigid_modalities ' \
             'N_rigid_reg_masks N_rigid_mod_diff_bfc- must be tuples (or list) not strings.'
        for k in ['Affine_modalities', 'Affine_reg_masks', 'N_rigid_modalities', 'N_rigid_reg_masks', 'N_rigid_mod_diff_bfc']:
            if not (isinstance(self.propagation_options[k], tuple) or isinstance(self.propagation_options[k], list)):
                raise IOError(msg)
        # Sanity check:
        msg = ''
        for bfc_mod in self.propagation_options['N_rigid_mod_diff_bfc']:
            if bfc_mod not in self.propagation_options['N_rigid_modalities']:
                msg += '\n\n === The modality selected for the differential bias field is not present in ' \
                       'the stack. Turn N_rigid_mod_diff_bfc to empty list, or add its values to ' \
                       'N_rigid_modalities == \n'

        if len(self.propagation_options['Affine_reg_masks']) > 0:
            if not len(self.propagation_options['Affine_reg_masks']) == len(self.propagation_options['Affine_modalities']):
                msg += '\n== Affine_reg_masks and Affine_modalities must have the same number of parameters ==\n'

        if len(self.propagation_options['N_rigid_modalities']) > 0:
            if len(self.propagation_options['N_rigid_reg_masks']) > 0:
                if not len(self.propagation_options['N_rigid_reg_masks']) == len(self.propagation_options['N_rigid_modalities']):
                    msg += '\n== N_rigid_modalities and N_rigid_reg_masks must have the same number of parameters ==\n'
        if msg is not '':
            raise IOError(msg)

    def _check_bias_field_corrector_command(self):
        if self.bfc_corrector_cmd is None:
            print('Bias field corrector command not found. '
                  '"Get_differential_BFC" of the propagation option set to False ')
            self.propagation_controller['Get_differential_BFC'] = False

    def erase_scaffoldings(self):
        os.system('rm -r {}'.format(self.scaffoldings_pfo))

    def _spot_on_target_update_records(self):
        update_parameters_record(self)

    def spot_on_target_initialise(self):
        os.system('mkdir -p {}'.format(self.scaffoldings_pfo))
        update_parameters_record(self)

    def propagate(self):
        self._check_multi_atlas_structure()
        self._check_target_structure()
        self._check_propagation_options()
        self._spot_on_target_update_records()

        # print some information to console:
        print('Propagation steps: \nmulti-atlas {0} \non target {1} \n'.format(
            self.atlas_list_charts_names, self.target_pfo))
        print('--- Propagation options:')
        for k in self.propagation_options.keys():
            print('{0:<20} : {1}'.format(k, self.propagation_options[k]))
        print('\n--- Propagation controller')
        for k in self.propagation_controller.keys():
            print('{0:<20} : {1}'.format(k, self.propagation_controller[k]))

        # It is still possible to apply the propagator to a subject already in the atlas
        # to reinforce the segmentation, for example in iterative round of manual adjustments
        # and automatic propagation, but a warning message a message is raised and parameters are updated.
        if self.target_name in self.atlas_list_charts_names:
            print('Target {} is an element of the template!\n'.format(self.target_name))

        propagator(self)

    def fuse(self):
        """
        Access the auxiliary method fuser with the input class parameters.
        :return: performs labels fusion.
        """
        self._check_multi_atlas_structure()
        self._check_target_structure()
        self._spot_on_target_update_records()

        fuser(self)

    def save_results_by_tag(self, parameters_tag='all'):
        """
        Get all the results under tag under arch_automatic_segmentations_name_folder under segm folder of the target.
        if 'all' gathers all the tags.
        :param parameters_tag: if 'all' or None all tags are considered.
        :return:
        """
        def copy_from_folder(pfo_input):
            assert os.path.exists(pfo_input), pfo_input
            # Auxiliary
            for pfi in os.listdir(pfo_input):
                if pfi.startswith(self.arch_approved_segmentation_prefix):
                    cmd = 'cp {0} {1}'.format(pfi, jph(
                        self.target_pfo, self.target_name, self.arch_segmentations_name_folder, pfi.replace(self.arch_approved_segmentation_prefix, '')))
                    print(cmd)
                    os.system(cmd)

        if parameters_tag == 'all' or None:
            for p in os.listdir(self.target_pfo):
                if p.startswith(self.arch_scaffoldings_name_folder):
                    copy_from_folder(jph(self.target_pfo, p))
        else:
            target_scaffoldings_folder_name_tagged = self.arch_scaffoldings_name_folder + '_' + parameters_tag
            assert os.path.exists(target_scaffoldings_folder_name_tagged), target_scaffoldings_folder_name_tagged
            copy_from_folder(target_scaffoldings_folder_name_tagged)
