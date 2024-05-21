FROM python:3.12-slim
LABEL MAINTAINER KBase Developer
# -----------------------------------------
COPY ./ /kb/module
RUN mkdir -p /kb/module/work
WORKDIR /kb/module

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PYTHONPATH="/kb/module/lib:$PYTHONPATH"

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
