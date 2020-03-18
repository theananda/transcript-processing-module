# transcript-processing-module
Python module to process Parliamentary Transcripts (လွှတ်တော် အစည်းအဝေးမှတ်တမ်းများ). Refactored version of concept scripts ("https://github.com/theananda/Digitizing-Parliamentary-Transcripts")



## Install Dependencies
```
pip -r install requirement.txt
```
## Workflow

* Rename the transcripts to standartized format like 02-02-02.pdf and put it in a directory
* Run the script
```
python automation.py --path /path/to/pdf/dir --house lower
args --path 'path to pdf directory'
args --house 'lower,upper,union'
```
* Delete front cover, back cover etc when the script ask to do so.
* Clean text junks when the script ask
* When the script ends, XML files will be generated in the output directory inside pdf directory
* The XML files will still need to clean up/ fix manually afterwards.


# Credit
* [MyParser for Syllabification](https://github.com/thantthet/MyanmarParser-Py)
* [MM String Normalizer](https://github.com/ayehninnkhine/MMStringNormalizer)
