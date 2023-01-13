FROM ubuntu:22.04

RUN apt-get update
RUN apt-get install -y --no-install-recommends git build-essential ocaml libnum-ocaml-dev python3-pip python3-dev

RUN git clone https://github.com/GumTreeDiff/pythonparser.git /opt/pythonparser --depth 1 \
    && ln -s /opt/pythonparser/pythonparser /usr/bin/pythonparser \
    && cd /opt/pythonparser \
    && pip3 install -r requirements.txt

RUN git clone https://github.com/GumTreeDiff/cgum.git /opt/cgum --depth 1 \
    && make -C /opt/cgum \
	&& ln -s /opt/cgum/cgum /usr/bin/cgum

RUN git clone --recurse-submodules https://github.com/GumTreeDiff/tree-sitter-parser.git /opt/tree-sitter-parser --depth 1 \
    && ln -s /opt/tree-sitter-parser/tree-sitter-parser.py /usr/bin/tree-sitter-parser.py \
    && /opt/tree-sitter-parser \
    && pip3 install -r requirements.txt

COPY comment_corrector /opt/comment_corrector
RUN cd /opt/comment_corrector && pip3 install -r requirements.txt

COPY target/ target/

ENTRYPOINT ["comment_corrector"]