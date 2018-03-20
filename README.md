<p align="center"> 
<img src="https://github.com/gift-surg/SPOT-A-NeonatalRabbit/blob/master/docs/software_scheme.jpg" width="650">
</p>


# SPOT-A-NeonatalRabbit

**Segmentations Propagation On Target (...as a Neonatal Rabbit)**

This is an open-source repository written in Python 2 and based on [LABelsToolkit][labelstoolkit], [NiftyReg][niftyreg], 
[NiftySeg][niftyseg] and [NifTK][niftk] 
to propagate an MRI multi-atlas on a new subject scanned with the same modalities of the multi-atlas 
(target). 
Default parameters are tuned to work in particular for the Newborn Rabbit Multi-Atlas developed within the 
[GIFT-Surg project][giftsurg] in collaboration between University College London (UK) and 
Katholische Universitat  Leuve (Belgium).
 
Via parameters tuning, this software can be used as a framework to automatise general segmentation 
propagation and label fusion pipelines.

## Material related to Neonatal Rabbit Brain Mutli-Atlas:

* [MRI Neonatal Rabbit Brain Mutli-Atlas][mrira] 
* [Repository for the Rabbit Brain Mutli-Atlas benchmarking][multiatlasonzenodo] - Coming soon on Zenodo
* Documentation with the protocol employed in creating the Rabbit Brain Mutli-Atlas - Coming soon

## Getting started

+ Requirements
    - Python 2 (**Python 2 only** for the current release)
    - Libraries in the textfile [requirements.txt][requirementstxt]
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
    - See the [examples folder][examplesfolder] and the [wiki page][wikipage]

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


[wikipage]: https://github.com/gift-surg/SPOT-A-NeonatalRabbit/wiki
[multiatlasonzenodo]: Coming-Soon
[giftsurg]: http://www.gift-surg.ac.uk
[niftyreg]: http://cmictig.cs.ucl.ac.uk/wiki/index.php/NiftyReg
[niftyseg]: http://cmictig.cs.ucl.ac.uk/research/software/software-nifty/niftyseg
[niftk]: http://cmictig.cs.ucl.ac.uk/research/software/software-nifty/niftyview
[labelstoolkit]: https://github.com/SebastianoF/LABelsToolkit
[requirementstxt]: https://github.com/gift-surg/SPOT-A-NeonatalRabbit/blob/master/requirements.txt
[examplesfolder]: https://github.com/gift-surg/SPOT-A-NeonatalRabbit/blob/master/examples
[testingfolder]: https://github.com/gift-surg/SPOT-A-NeonatalRabbit/blob/master/tests
[contributionguideline]: https://github.com/gift-surg/SPOT-A-NeonatalRabbit/blob/master/CONTRIBUTE.md
[mrira]: https://github.com/gift-surg/MRImultiAtlasForNeonatalRabbitBrain
[licence]: https://github.com/gift-surg/SPOT-A-NeonatalRabbit/blob/master/LICENCE.txt
[nosetest]: http://pythontesting.net/framework/nose/nose-introduction/
[virtualenvironment]: http://docs.python-guide.org/en/latest/dev/virtualenvs/
[wikipage]: https://github.com/gift-surg/SPOT-A-NeonatalRabbit/wiki
