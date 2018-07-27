FROM alpine:3.7

ENV WORKDIR=/app

WORKDIR $WORKDIR

RUN apk --no-cache add tini python3 uwsgi uwsgi-python3

COPY requirements.txt $WORKDIR/requirements.txt

RUN pip3 install -r requirements.txt

COPY . $WORKDIR

CMD ['tini', '--', 'uwsgi', 'uwsgi.ini']
