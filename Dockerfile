FROM ubuntu:jammy

RUN apt-get update
RUN apt-get install -y --no-install-recommends git build-essential ocaml libnum-ocaml-dev python3-pip python3-dev default-jdk

RUN git clone https://github.com/GumTreeDiff/pythonparser.git /opt/pythonparser --depth 1 --jobs 4\
    && ln -s /opt/pythonparser/pythonparser /usr/bin/pythonparser \
    && cd /opt/pythonparser \
    && pip3 install -r requirements.txt

RUN git clone https://github.com/GumTreeDiff/cgum.git /opt/cgum --depth 1 --jobs 4\
    && make -C /opt/cgum \
	&& ln -s /opt/cgum/cgum /usr/bin/cgum

RUN git clone --recurse-submodules https://github.com/GumTreeDiff/tree-sitter-parser.git /opt/tree-sitter-parser --depth 1 --jobs 4\
    && ln -s /opt/tree-sitter-parser/tree-sitter-parser.py /usr/bin/tree-sitter-parser.py \
    && cd /opt/tree-sitter-parser \
    && pip3 install -r requirements.txt

COPY . /opt/comment_corrector
WORKDIR /opt/comment_corrector
RUN pip3 install -r requirements.txt