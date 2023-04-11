# Comment Corrector

## About

Comment Corrector is a GitHub Action that analyses source code for any discrepancies between a comment and the code it describes. Comment Corrector is predominately written in Python3, while the GumTree API is called through Java.

## Supported Languages

Comment Corrector is capable of analysing source code written in Python.

The tool is designed to easily extend to support Java and C.

See `supported_languages.json` for further details.

## How to Use

### 1. GitHub Action

Comment Corrector is intended to be ran as a GitHub Action. Simply add the action to a `.yaml` file defining a workflow.

**NOTE**
For the tool to operate as expected the checkout step preceding the step calling the tool must set the input `fetch-depth` to 0 as follows.

```
name: 'Check comments using Comment Corrector'

on: workflow_dispatch

jobs:
  job1:
    runs-on: ubuntu-latest
    name: Use Comment Corrector Action
    steps:
      - name: Checkout
        uses: actions/checkout@v3
        with:
          fetch-depth: 0
      - name: Check Comments
        uses: clodaghwalsh17/comment-corrector@beta
        with:
          custom-words-file: 'my_dictionary.txt'
          
```

The optional input `custom-words-file` if used must point to a file in the `.github/workflows` directory of the repository in which the workflow is run.

### 2. Standalone Application

Comment Corrector can be ran as a standalone application if the following dependencies are accounted for, assuming the tool is ran in a Unix environment.

#### Running Comment Corrector

Comment Corrector can be ran by issuing the command below. The argument `-v2` is optional and may be specified when the user wishes to compare two versions of a file for comments that may be outdated. If the user simply requires cosmetic analysis of the comments this argument may be omitted.

```
python3 -m comment_corrector path/v1.py -v2 path/v2.py
```

#### Python Dependencies

All Python dependencies can be found in the `requirements.txt` file. Issuing the following command installs the necessary dependencies.

```
pip3 install -r requirements.txt
```

To operate effectively the `pyenchant` package relies on the `Enchant C` library. Follow the instructions in the [documentation](http://pyenchant.github.io/pyenchant/install.html) to download the library for your system.

#### GumTree Dependencies

GumTree is a code differencing tool written in Java. The [GumTreeDiff](https://github.com/GumTreeDiff) project develops the parsers that [GumTree](https://github.com/GumTreeDiff/gumtree) relies on.  

The necessary GumTree API calls are made and packaged into a JAR file, refer to the src and target folders respectively. Comment Corrector calls this JAR file using the GumTreeDiff subprojects below. Each subproject must be downloaded and added to the system path. Follow the instructions provided by each subproject.

- [pythonparser](https://github.com/GumTreeDiff/pythonparser)
- [cgum](https://github.com/GumTreeDiff/cgum)
- [tree-sitter-parser](https://github.com/GumTreeDiff/tree-sitter-parser)

NOTE: It is recommended to run the command `maven clean install` to ensure the JAR file is up to date.
