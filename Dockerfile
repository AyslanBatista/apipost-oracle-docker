FROM python:3.10.5-slim-buster

RUN apt-get update && apt-get upgrade -y && apt-get install libaio1 unzip -y

ADD https://download.oracle.com/otn_software/linux/instantclient/217000/instantclient-basic-linux.x64-21.7.0.0.0dbru.zip ./instantclient-basic-linux.x64-21.7.0.0.0dbru.zip

RUN unzip instantclient-basic-linux.x64-21.7.0.0.0dbru.zip && rm instantclient-basic-linux.x64-21.7.0.0.0dbru.zip && \
 mkdir /opt/oracle && mv instantclient_21_7 /opt/oracle && sh -c "echo /opt/oracle/instantclient_21_7 > /etc/ld.so.conf.d/oracle-instantclient.conf" && ldconfig

ADD https://download.oracle.com/otn_software/linux/instantclient/217000/instantclient-sdk-linux.x64-21.7.0.0.0dbru.zip ./instantclient-sdk-linux.x64-21.7.0.0.0dbru.zip

RUN cd /opt/oracle && unzip -o /instantclient-sdk-linux.x64-21.7.0.0.0dbru.zip && apt-get remove unzip -y && rm -rf /var/cache/apk/*
RUN rm ./instantclient-sdk-linux.x64-21.7.0.0.0dbru.zip

# Copiando arquivo TNSNAMES
COPY /Banco /opt/oracle/instantclient_21_7/network/admin
COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Definindo as variáveis de ambiente
ARG DB_SID

ENV ORACLE_SID=${DB_SID}
ENV LD_LIBRARY_PATH="/opt/oracle/instantclient_21_7:$LD_LIBRARY_PATH"
ENV PATH="/opt/oracle/instantclient_21_7:${PATH}"
ENV ORACLE_BASE="/opt/oracle"
ENV ORACLE_HOME="/opt/oracle/instantclient_21_7"
ENV ORACLE_TNS_ADMIN="/opt/oracle/instantclient_21_7/network/admin"
ENV TZ="America/Sao_Paulo"
ENV PYTHONUNBUFFERED=1

WORKDIR /app

CMD ["python3", "__main__.py"]