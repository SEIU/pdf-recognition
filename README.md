# PDF Recognition

Checks cards for signatures

## Description

Analyzes cards or forms downloaded from VAN as PDFs. Assuming two signature boxes,
this code will determine the locations of the boxes and output a pixel density, 
along with a determination of the existence of a signature or not. 

Converts to a rasterized image then looks for a box.

## Getting Started

### Dependencies

* Python 3.12.3 (latest) via Bash Command Line
* Git
* [uv](https://docs.astral.sh/uv/getting-started/installation/) 0.10.8 (latest)

### Installing

* Clone repo [(how to clone a repo)](https://www.geeksforgeeks.org/git/how-to-git-clone-a-remote-repository/)
* ```uv sync``` (create the .venv directory)
* ```source .venv/bin/activate``` (activate the .venv enviornment)
* cd to the repo

### Executing program

* For single card
```
./check_sigs ../location_of_card/card.pdf
```
* For multiple cards
```
ls ../location_of_files/* | xargs ./check_sigs
```

## Help

Any advise for common problems or issues.
* Input Welcome!

## Authors

David Mertz
[@DomPizzie](https://securityreflections.substack.com/about)

## Version History

* 0.2
    * ReadMe Added
    * See [commit change]() or See [release history]()
* 0.1
    * Initial Release


## Acknowledgments

* [Readme Template](https://gist.github.com/DomPizzie/7a5ff55ffa9081f2de27c315f5018afc)
* [Raziq Noorali (for the ReadMe)](https://github.com/Provider10)
