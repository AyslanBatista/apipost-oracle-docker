# apipost-oracle-docker


<code><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original-wordmark.svg" width="40" height="40"/></code>+<code><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/oracle/oracle-original.svg" width="40" height="40"/></code>+<code><img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-plain-wordmark.svg" width="40" height="40"/></code>

API de integração com qrsorteios utilizando python+oracle+docker

## Criando a imagem(BUILD):
```bash
docker image build --build-arg DB_SID=<sid_banco_de_dados> -t python_oracle .
```

## Executar o container:
```bash
docker container run -d --restart on-failure --mount type=volume,src=API,dst=/app --name api python_oracle
```

          