# apipost-oracle-docker


<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original-wordmark.svg" width="100" height="100"/>&nbsp;&nbsp;<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/oracle/oracle-original.svg" width="100" height="100"/>&nbsp;&nbsp;&nbsp;&nbsp;<img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-plain-wordmark.svg" width="100" height="100"/>

API de integração com qrsorteios utilizando python+oracle+docker

## Criando a image(BUILD):
```bash
docker image build --build-arg DB_SID=<sid_banco_de_dados> -t python_oracle .
```

## Executando o container:
```bash
docker container run -d --restart on-failure --mount type=volume,src=API,dst=/app --name api python_oracle
```

          