# Comment Corrector

## About

Comment Corrector is a GitHub Action that analyses source code for any discrepancies between a comment and the code it describes. Comment Corrector is predominately written in Python3, while the GumTree API is called through Java.

## Supported Languages

Comment Corrector is capable of analysing source code written in the following languages:

- Java
- Python
- C

See `supported_languages.json` for further details.

## How to Use

### 1. Standalone Application

Comment Corrector can be ran as a standalone application if the following dependencies are accounted for. NOTE: This has only been tested in a Unix environment.

#### Python Dependencies

All Python dependencies can be found in the `requirements.txt` file. Issuing the following command installs the necessary dependencies.

```
pip3 install -r requirements.txt
```

#### GumTree Dependencies

GumTree is a code differencing tool written in Java. The [GumTreeDiff](https://github.com/GumTreeDiff) project develops the parsers that [GumTree](https://github.com/GumTreeDiff/gumtree) relies on.  

The necessary GumTree API calls are made and packaged into a JAR file, refer to the src and target folders respectively. Comment Corrector calls this JAR file using the GumTreeDiff subprojects below. Each subproject must be downloaded and added to the system path. Follow the instructions provided by each subproject.

- [pythonparser](https://github.com/GumTreeDiff/pythonparser)
- [cgum](https://github.com/GumTreeDiff/cgum)
- [tree-sitter-parser](https://github.com/GumTreeDiff/tree-sitter-parser)

NOTE: It is recommended to run the command `maven clean install` to ensure the JAR file is up to date.
