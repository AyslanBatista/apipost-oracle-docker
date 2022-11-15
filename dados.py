import json
import sys
from typing import Dict

import cx_Oracle

from config import settings
from utils import get_logger
from utils import LOG_PATH

# Armazenando a função de log em um variavel
log = get_logger()


def connect_oracle(select: str) -> list:
    """Função faz a conexão com banco de dados oracle utilizando as
    variáveis de autenticação `USER`, `PASSWORD`, `BANCO`, que estão
    armazenadas em um arquivo `secrets`, com a autenticação efetuado a
    função faz um select com base no argumento em que foi passado `select`.
    Recebendo a consulta do banco ela é organizada e retorna os dados.
    
    Args:
        select (str): String contendo o select que será feito no banco

    Returns:
        list: Retorna dados em formato de tupla com base no `select`
    """
    try:
        # Fazendo conexão com o banco de dados
        with cx_Oracle.connect(
            user=settings.USER,
            password=settings.PASSWORD,
            dsn=settings.BANCO,
            encoding="UTF-8"
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(select)
                rows = cursor.fetchall()
                organizar = sorted(rows)
                print(len(organizar))
                return organizar
    except Exception as error:
        log.error("%s", str(error), exc_info=True)
        sys.exit(1)


def ajustar_data_cpf(tupla: tuple) -> list:
    """Função recebe uma tupla com todos os campos que serão enviados,
    a tupla é transformado em uma lista para pegar o valor 0, 2 e 3,
    valor 0 é feito a formatação data conforme o solicitante,
    valor 2 é descompactado e retirado a informação do cpf de uma string
    e retornado essa informação ao valor 2,
    valor 3 é alterado para ser utilizado o número de chave SAT como
    numero do documento.

    Args:
        tupla (tuple): tupla com as informações do campo que será enviado

    Returns:
        list: Retorna uma lista com os dados para o Json
    """
    try:
        lista = list(tupla)
        valores = lista[2].split("|")
        data, hora = str(lista[0]).split(" ")
        dia, mes, ano = data.split("/")
        data_formatada = '20{}-{}-{} {}'.format(ano, mes, dia, hora)
        lista[3] = valores[0]
        lista[2] = valores[3]
        lista[0] = data_formatada
    except Exception as error:
        log.error("%s test", str(error), exc_info=True)
        sys.exit(1)
    return lista


def gravar_valor(valor: str):
    """Função recebe o valor único que está sendo utilizado no número
    do documento, grava esse valor em um arquivo de log onde esse
    arquivo é mapeado na variável `LOG_PATH` no documento `utils.py`.
    Intuito da função é armazenar todos os números de documentos em
    que foi enviado para não ter tentativa de envio de documentos
    em duplicidade.

    Args:
        valor (str): Valor do número do documento em que foi enviado
    """
    try:
        with open(LOG_PATH, "a") as file_:
            file_.write(f"{valor}\n")
    except FileNotFoundError as e:
        log.error("%s", str(e), exc_info=True)
        sys.exit(1)


def ler_valor():
    """Função serve para ler um arquivo com o nome guardado na variável
    `LOG_PATH` no arquivo utils.py, ao ler esse arquivo a função irá
    acumular as informações de cada linha em uma lista e retornar
    essa lista convertida em um set.

    Returns:
        set: Retorna uma base de dados contendo valores que já foram enviados.
    """
    try:
        with open(LOG_PATH, "r") as file_:
            arquivo = file_.read().strip().split("\n")
            return set(arquivo)
    except FileNotFoundError as e:
        log.error("%s", str(e), exc_info=True)
        sys.exit(1)


def arquivo_json(lista_json: list, lista_produtos: list) -> Dict:
    """Função recebe uma `lista_json` com as informações dos campos referente
    a compra, `lista_produtos` com todos os produtos da compra e informações
    da campanha que está armazenado em um arquivo `secrets`.
    Após estruturar todas as informações ele retorna um dicionario que
    poder ser usado como JSON.

    Args:
        lista_json (list): Lista com os detalhes da compra
        lista_produtos (list): Lista com todos os produtos da compra

    Returns:
        Dict: Dicionario com a formatação do JSON
    """

    json_file = {
        "campanha": {
            "ano": settings.campanha["ano"],
            "identificacao": settings.campanha["identificacao"],
        },
        "usuario": lista_json[2],
        "tipo": settings.campanha["tipo"],
        "uf": settings.campanha["uf"],
        "extra": settings.campanha["extra"],
        "dadosNaoFiscal": {
            "cnpjEmitente": settings.campanha["cnpjEmitente"],
            "nomeEmitente": settings.campanha["nomeEmitente"],
            "dataHoraEmissao": lista_json[0],
            "valorTotal": lista_json[1],
            "cnpjCpf": lista_json[2],
            "numeroDocumento": lista_json[3],
            "formaPagamento": lista_json[4],
            "produtosServicos": lista_produtos,
            "vendedor": {
                "codigo": str(lista_json[9]),
                "nome": settings.campanha["nome"],
            }
        }
    }
    print(json.dumps(json_file))
    return json_file
