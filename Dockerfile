from brunneis/python:3.8
RUN pip install requests lxml pyyaml
COPY butler.py entrypoint.sh /
ENTRYPOINT /entrypoint.sh
