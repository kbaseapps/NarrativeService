FROM python:3.10-slim
# FROM ghcr.io/kbase/sdkpython:0.0.1
# kbase/sdkbase2:python
LABEL MAINTAINER KBase Developer
# -----------------------------------------
COPY ./ /kb/module
RUN mkdir -p /kb/module/work
WORKDIR /kb/module
# RUN chmod -R a+rw /kb/module

# Insert apt-get instructions here to install
# any required dependencies for your module.

RUN apt-get update && apt-get install -y make

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# RUN pip install coverage

# -----------------------------------------

# RUN pip install pylru &&\
#     pip install python-dateutil

ENV PYTHONPATH="/kb/module/lib:$PYTHONPATH"

# RUN make all

# EXPOSE 5000

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
