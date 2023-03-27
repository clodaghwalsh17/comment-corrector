# Use the base image hosted on Dockerhub to create the image faster
FROM clodaghw17/comment_corrector

RUN git config --system --add safe.directory '*'

COPY . /
RUN pip3 install -r requirements.txt

ENTRYPOINT [ "/entrypoint.sh" ]