# Contributing to SPOT-A-NeonatalRabbit

Thanks for contributing to SPOT-A-NeonatalRabbit!

## Where to start to contribute

See under [docs folder][docsfolder] as a starting point for the expected reults of the code and the selected naming convention.
Anyone that is contributing is expected to keep the same naming convention.

## Questions, bugs, issues, emails and new features 

+ For any issue bugs or question related to the code, please raise an issue in the 
[SPOT-A-NeonatalRabbit issue page][spot_issue_page].

+ **Please use a new issue for each thread:** make your issue re-usable and reachable by other users that may have 
encountered a similar problem.

+ Propose here as well improvements suggestions and new features.

+ Feel free to send an email to s.ferraris at ucl dot ac dot uk.

+ [Pull requests][pull-requests] are more than welcome. Please **check tests are all passed** 
before this (type `nosetests` in the code root folder), the new features are integrated in the record (text file
each time a new subject is spotted, keeping track of the selected parameters) and the documents under 
[docs folder][docsfolder] are up to date.

## New feature guidelines

SPOT-A-NeonatalRabbit considers subjects of the Multi-Atlas and Target already aligned in the same orientation.
We would like to keep it this way for simplicity, so any pre-processing re-orientation should happen in an external phase 
See the [wiki-page][wikipage].


## Continuous integration

Even a lightweight synthetic phantom created at runtime for testing is quite demanding in term of computational weight and time
to inegrate the framework

## Code Etiquette

+ The code follows the [PEP-8][pep8] style convention. 
+ Please follow the [ITK standard prefix commit message convention][itk_standard_commit] for commit messages. 
+ Please use the prefix `pfi_` and `pfo_` for the variable names containing path to files and path to folders respectively.

## Code of Conduct

This project adopts the [Covenant Code of Conduct][covenant]. 
By participating, you are expected to uphold this code. 



[covenant]: https://contributor-covenant.org/
[itk_standard_commit]: https://itk.org/Wiki/ITK/Git/Develop
[pep8]: https://www.python.org/dev/peps/pep-0008/ 
[docsfolder]: https://github.com/gift-surg/SPOT-A-NeonatalRabbit/tree/master/docs
[wikipage]: https://github.com/gift-surg/SPOT-A-NeonatalRabbit/wiki
[spot_issue_page]: https://github.com/gift-surg/SPOT-A-NeonatalRabbit/issues
[pull-requests]: https://yangsu.github.io/pull-request-tutorial/

