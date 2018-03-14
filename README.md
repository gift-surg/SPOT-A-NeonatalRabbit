# SPOT-A-NeonatalRabbit: 

**Segmentations Propagation On Target (...as a Neonatal Rabbit).**

This is an open-source repository written in Python 2 and based on [LABelsToolkit][labelstoolkit], [NiftyReg][niftyreg], 
[NiftySeg][niftyseg] and [NifTK][niftk] 
to propagate an MRI multi-atlas on a new subject scanned with the same modalities of the multi-atlas 
(target). 
Default parameters are tuned to work in particular for the Newborn Rabbit Multi-Atlas developed within the 
[GIFT-Surg project][giftsurg] in collaboration between University College London (UK) and 
Katholische Universitat  Leuve (Belgium).
 
Tuning the paths and the parameters the same software can be used as a framework to automatise general segmentation 
propagation and label fusion pipeline.

## Material related to Neonatal Rabbit Brain Mutli-Atlas:

* [MRI Neonatal Rabbit Brain Mutli-Atlas][mrira] - Coming soon on Zenodo
* Repository for Mutli-Atlas benchmarking - Coming soon 
* Documentation with the protocol for the Mutli-Atlas creation - Coming soon

## Nomenclatures:

**Segmentation:** (of an MRI acqusition) manual or automatic annotation of the given acquisition, where at each
 voxel is assigned a label corresponding to an anatomical region.
 
**Labels descriptor:** file containing the correspondences between the labels of a segmentation and the anatomical region.

**Atlas:** MRI acquisition (one or more modality) of the same subject with the anatomical segmentation produced according to a protocol.

**Multi-Atlas:** set of atlases sharing the acquisition and segmentation protocol.

**Target:** atlas where the segmentation is missing.

**Segmentation Propagation and Label Fusion:** algorithmic method to infer the missing segmentation
of a target propagating the segmentations of a Multi-Atlas and then fusing the labels together, to
obtain a final (deterministic or probabilistic) segmentation.

## How to use

+ Requirements
    - Python 2 (**Python 2 only** for the current release).
    - Libraries in the textfile [requirements.txt][requirementstxt].
    - [LABelsToolkit][labelstoolkit]
    - [NiftyReg][niftyreg] 
    - [NiftySeg][niftyseg] 
    - [NifTK][niftk] (only if the differential bias field correction is used in the non-rigid registration)

+ Installation
    - We recommend to install the software in development mode, inside a python [virtual-environment][virtualenvironment] with the following commands.
        ```
        cd <folder where to clone the code>
        git clone https://github.com/SebastianoF/SPOT-A-NeonatalRabbit.git
        cd SPOT-A-NeonatalRabbit
        source <virual-env with the required libraries>/bin/activate
        pip install -e .
        ```
        
+ Examples
    - Some python modules with the examples are stored under [examples folder][examplesfolder]
    - More examples can be found in the repository where this code was used to create and validate the multi-atlas segmentation.
    - To run the code with a lightweight and customisable multi-atlas, a synthetic multi-atlas can be generated with [LABelsToolkit][labelstoolkit]
    as proposed in the testing under the [testing folder][testingfolder]


## Code testing
+ Unit testing with [nosetest][nosetest]. 
Type `nosetests` in a terminal at the cloned repository.
+ Tests are based on a lightweight multi-atlas with analogous structure than the Neonatal Brain Rabbit generated with [LABelsToolkit][labelstoolkit]. 
The first test may take some minutes to create the multi-atlas.

## Support and contribution
Please see the [contribution guideline][contributionguideline] for bugs report,
feature requests and code re-factoring and re-styling.

## Copyright and licence
+ Copyright (c) 2018, University College London.
+ SPOT-A-NeonatalRabbit is available as free open-source software under [3-Clause BSD][licence]
<!---
+ To cite the code in your research please follow [this link](http://joss.theoj.org/papers/2ee6a3a3b1a4d8df1633f601bf2b0ffe).
-->

## Authors and Acknowledgments

+ The MRI Neonatal Rabbit Multi-Atlas and related code is developed within the [gift-SURG research project][giftsurg] in collaboration with KU Leuven (Belgium) and UCL (UK).
+ This work was supported by Wellcome / Engineering and Physical Sciences Research Council (EPSRC) [WT101957; NS/A000027/1; 203145Z/16/Z]. 
+ The upcomging documentation with provide the full list of authors and acknowledgments.



[giftsurg]: http://www.gift-surg.ac.uk
[niftyreg]: http://cmictig.cs.ucl.ac.uk/wiki/index.php/NiftyReg
[niftyseg]: http://cmictig.cs.ucl.ac.uk/research/software/software-nifty/niftyseg
[niftk]: http://cmictig.cs.ucl.ac.uk/research/software/software-nifty/niftyview
[labelstoolkit]: https://github.com/SebastianoF/LABelsToolkit
[requirementstxt]: https://github.com/gift-surg/SPOT-A-NeonatalRabbit/blob/master/requirements.txt
[examplesfolder]: https://github.com/gift-surg/SPOT-A-NeonatalRabbit/blob/master/examples
[testingfolder]: https://github.com/gift-surg/SPOT-A-NeonatalRabbit/blob/master/tests
[contributionguideline]: https://github.com/gift-surg/SPOT-A-NeonatalRabbit/blob/master/tests
[mrira]: https://github.com/gift-surg/MRImultiAtlasForNeonatalRabbitBrain
[licence]: https://github.com/gift-surg/SPOT-A-NeonatalRabbit/blob/master/LICENCE
[nosetest]: http://pythontesting.net/framework/nose/nose-introduction/
[virtualenvironment]: http://docs.python-guide.org/en/latest/dev/virtualenvs/