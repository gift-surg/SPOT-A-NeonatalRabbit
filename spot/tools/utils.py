import os
import nibabel as nib
import logging

from nilabel.tools.aux_methods.utils import print_and_run
from nilabel.tools.image_shape_manipulations.merger import substitute_volume_at_timepoint
from nilabel.main import Nilabel as NiL

def substitute_volume_at_timepoint_by_path(pfi_im_input_4d, pfi_im_input_3d, timepoint, pfi_output):
    im_input_4d = nib.load(pfi_im_input_4d)
    im_input_3d = nib.load(pfi_im_input_3d)
    new_im = substitute_volume_at_timepoint(im_input_4d, im_input_3d, timepoint)
    nib.save(new_im, pfi_output)


def get_timepoint_by_path(pfi_im_input_4d, timepoint, pfi_output):
    """
    :param pfi_im_input_4d:
    :param timepoint:
    :param pfi_output:
    :return:
    Handle base case: If the input 4d volume is actually a 3d and timepoint is 0, then just return the same input
    in the new file.
    """
    im = nib.load(pfi_im_input_4d)
    shape_im_input = im.shape
    if timepoint == 0 and len(shape_im_input) == 3:
        cmd = 'cp {} {}'.format(pfi_im_input_4d, pfi_output)
    elif len(shape_im_input) == 4 and timepoint < shape_im_input[-1]:
        cmd = 'seg_maths {} -tp {} {}'.format(pfi_im_input_4d, timepoint, pfi_output)
    else:
        raise IOError
    print_and_run(cmd)


def stack_a_list_of_images_from_list_pfi(list_pfi, pfi_stack, stack_dim=4):
    for p in list_pfi:
        assert os.path.exists(p), p

    if len(list_pfi) == 1:
        cmd = 'cp {} {}'.format(list_pfi[0], pfi_stack)
        print_and_run(cmd)
    else:
        print('stack {0} in {1}'.format(list_pfi, pfi_stack))
        pfi_first = list_pfi[0]
        num_images_to_merge = len(list_pfi) - 1
        cmd = 'seg_maths {0} -merge {1} {2}'.format(pfi_first, num_images_to_merge, stack_dim)
        for p in list_pfi[1:]:
            cmd += ' {0} '.format(p)
        cmd += ' {0} '.format(pfi_stack)
        print_and_run(cmd)


def get_list_pfi_images_3d_from_list_images_4d(list_pfi_4d_images, tp):
    list_new = []
    for p in list_pfi_4d_images:
        p_new = p.replace('.nii.gz', '_tp{}.nii.gz'.format(tp))
        cmd = 'seg_maths {0} -tp {1} {2}'.format(p, tp, p_new)
        print_and_run(cmd)
        list_new.append(p_new)
    return list_new

def prepare_slim_mask_from_path_to_stack(pfi_target_reg_mask_input, pfi_brain_mask, pfi_target_reg_mask_output):
    """
    Very simple for the moment:
    slim_mask = reg_mask * brain_mask
    :param pfi_target_reg_mask_input:
    :param pfi_brain_mask:
    :param pfi_target_reg_mask_output:
    :return:
    """
    lab = NiL()
    lab.manipulate_shape.cut_4d_volume_with_a_1_slice_mask(pfi_target_reg_mask_input, pfi_brain_mask, pfi_target_reg_mask_output)


def create_log(pfo_where_to_save, log_name='log.txt'):

    if not os.path.exists(pfo_where_to_save):
        here = os.path.dirname(os.path.abspath(__file__))
        w = '{} does not exist. Log file created in the code root'.format(pfo_where_to_save, here)
        print(w)
        pfo_where_to_save = here

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename=os.path.join(pfo_where_to_save, log_name),
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
