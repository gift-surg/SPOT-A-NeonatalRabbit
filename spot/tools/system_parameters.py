import os
from os.path import join as jph


if os.path.exists('/cluster/project0'):
    # print('You are on the cluster')
    bfc_corrector_cmd = '/share/apps/cmic/NiftyMIDAS/bin/niftkMTPDbc'

elif os.path.exists('/Volumes/LC/sebastianof/rabbits/'):
    # print('You are on the external hdd')
    bfc_corrector_cmd = '/Applications/niftk-16.1.0/NiftyView.app/Contents/MacOS/niftkMTPDbc'

elif os.path.exists('/Volumes/sebastianof/'):
    # print('You are on pantopolium')
    bfc_corrector_cmd = '/Applications/niftk-16.1.0/NiftyView.app/Contents/MacOS/niftkMTPDbc'

else:
    # print('You are in local')
    bfc_corrector_cmd = '/Applications/niftk-16.1.0/NiftyView.app/Contents/MacOS/niftkMTPDbc'

if not os.path.exists(bfc_corrector_cmd):
    bfc_corrector_cmd = None
