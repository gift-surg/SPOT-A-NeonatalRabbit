import os
from setuptools import setup, find_packages

from spot.__init__ import __version__ as version


info = {
        "name": "SPOT_A_NeonatalRabbit",
        "version": "0.0.0",
        "description": " - Segmentations Propagation On Target (As a Neonatal Rabbit)",
        "web_infos" : "",
        "repository": {
                       "type": "git",
                       "url": "https://github.com/gift-surg/SPOT-A-NeonatalRabbit.git"
                      },
        "author": "Sebastiano Ferraris, UCL",
        'author_email' : 's.ferraris@ucl.ac.co.uk',
        "dependencies": {
                         # requirements.txt file automatically generated using pipreqs.
                         "python" : "requirements.txt"
                         }
        }


def requirements2list(pfi_txt='requirements.txt'):
    here = os.path.dirname(os.path.realpath(__file__))
    f = open(os.path.join(here, pfi_txt), 'r')
    l = []
    for line in f.readlines():
        l.append(line.replace('\n', ''))
    return l


setup(name=info['name'],
      version=version,
      description=info['description'],
      author=info['author'],
      author_email=info['author_email'],
      license='',
      url='',
      packages=find_packages(),
      install_requires=requirements2list())
