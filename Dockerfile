FROM kbase/sdkbase2:python
MAINTAINER KBase Developer
# -----------------------------------------

# Insert apt-get instructions here to install
# any required dependencies for your module.

RUN pip install coverage

# -----------------------------------------

RUN pip install pylru &&\
    pip install python-dateutil

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

EXPOSE 5000

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
