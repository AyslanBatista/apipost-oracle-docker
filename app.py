import json
import sys
from time import sleep
from typing import Any

import httpx
from httpx import ConnectTimeout
from httpx import ReadTimeout
from pydantic import BaseModel

from config import settings

from dados import ajustar_data_cpf
from dados import arquivo_json
from dados import connect_oracle
from dados import gravar_valor
from dados import ler_valor
from dados import log


class Token(BaseModel):
    """Classe para armazenar o token de autenticação no atributo `token`
    e informações secundarias referente ao token no atributo `ativo`.
    """

    ativo: str
    token: str


def get_token() -> Token:
    """Essa função recupera um token de autenticação, através da url
    informada na variável `URL_TOKEN` que está em um arquivo `secrets`,
    utilizando as informações necessárias para autenticação em formato
    json que está na variável `AUTENTICACAO` no mesmo arquivo `secrets`.

    Raises:
        RuntimeError: Erro ao tentar recuperar o token

    Returns:
        Token: Função retorna o token solicitado
    """
    with httpx.Client() as client:
        response = client.post(
            url=settings.URL_TOKEN, json=settings.AUTENTICACAO
        )
        status = response.status_code
        if status == 200:
            data = response.json()["retorno"]
            return_data = Token(**data)
            return print(return_data.token)
        else:
            log.error(f"{status}")
            raise RuntimeError(f"Erro ao tentar solicitar o token: {status}")


def enviar_via_api(arquivo: json) -> int:
    """Essa função recebe um arquivo `JSON` para ser enviado via API post
    para o link contido na variavel `URL_DADOS` informada em um arquivo
    `secrets`, utilizando o token para autenticação informado na variavel
    `HEADERS` no mesmo arquivo `secrets`.

    Args:
        arquivo (json): Arquivo Json com os dados para serem enviados

    Raises:
        RuntimeError: Erro ao tentar fazer envio via API

    Returns:
        int: Retorna o valor 1 se foi enviado com sucesso, caso contrario
        retorna o valor 0
    """
    # Total de tentativas caso tome um timeout
    tries = 10
    for i in range(tries):
        try:
            with httpx.Client() as client:
                response = client.post(
                    url=settings.URL_DADOS,
                    headers=settings.HEADERS,
                    json=arquivo,
                )
                if response.status_code == 201:
                    print("informação enviada com sucesso")
                    gravar_valor(
                        valor=arquivo["dadosNaoFiscal"]["numeroDocumento"]
                    )
                    return 1
                elif response.text == settings.MSG_DUPLICADO:
                    print("Documento já foi enviado")
                    gravar_valor(
                        valor=arquivo["dadosNaoFiscal"]["numeroDocumento"]
                    )
                    return 0
                elif response.text == settings.MSG_CPF:
                    print("CPF da compra está com restrição(funcionario)")
                    gravar_valor(
                        valor=arquivo["dadosNaoFiscal"]["numeroDocumento"]
                    )
                    log.warning(
                        "msg:%s \nNumeroDocumento:%s \nCPF:%s",
                        str(response.text),
                        str(arquivo["dadosNaoFiscal"]["numeroDocumento"]),
                        str(arquivo["dadosNaoFiscal"]["cnpjCpf"]),
                    )
                    return 0
                else:
                    raise RuntimeError("Ocorreu um Erro")
        except (ReadTimeout, ConnectTimeout, TimeoutError) as e:
            if i < tries - 1:
                log.error("%s", str(e), exc_info=True)
                # Tempo de espera para fazer uma nova tentativa
                sleep(15)
                continue
            else:
                log.error(
                    "Programa finalizado. Todas tentativas de Timeout falharam"
                )
                sys.exit(1)
        except RuntimeError:
            log.error("%s", str(response.text), exc_info=True)
            sys.exit(1)
        break


def ajustar_e_enviar(tupla_dados: tuple, produtos: list) -> Any:
    """Função faz a junção de outras duas funções `ajustar_data_cpf`
    e `aquivo_json` responsáveis por organizar a documentação, depois
    transformar tudo em um JSON.
    Após a organização da documentação ele chama a função `enviar_via_api`
    que faz o envio via API.

    Args:
        tupla_dados (tuple): Dados recentes que contem informação do SQL
        produtos (list): Lista de todos os produtos que será acrescentado
        ao arquivo JSON
    """
    ajuste_data_cpf = ajustar_data_cpf(tupla=tupla_dados)
    json_file = arquivo_json(
        lista_json=ajuste_data_cpf,
        lista_produtos=produtos,
    )
    return enviar_via_api(arquivo=json_file)


def juntar_produtos(new_dados: tuple) -> int:
    """Função recebe os dados que serão enviados e faz a junção de
    todos os produtos da mesma compra com base na chavesat, acumulando
    os produtos em uma tupla, após fazer a junção de todos os produtos
    ele chama a função `ajustar_e_enviar`.

    Args:
        new_dados (tuple): Dados recentes que contem informação do SQL

    Returns:
        int: Retorna a quantidade de envios efetuados com sucesso
    """
    quantiade_envios = 0
    cupom_anterior = 0
    lista_produtos = []
    loops = 0
    try:
        for row in new_dados:
            loops += 1
            adicionado = False
            cupom = row[2].split("|")
            produto = {
                "descricao": row[5],
                "unidade": row[6],
                "quantidade": row[7],
                "valor": row[8],
                "codigo": str(row[10]),
                "codigoEAN": str(row[10]),
            }
            if cupom_anterior == 0:
                cupom_anterior = cupom[0]
                row_dados = row
                lista_produtos.append(produto)
                if loops == len(new_dados) and int(row[1]) == int(
                    produto["valor"]
                ):
                    quantiade_envios += ajustar_e_enviar(
                        tupla_dados=row_dados, produtos=lista_produtos
                    )

            elif cupom_anterior == cupom[0]:
                for item in lista_produtos:
                    if item["codigoEAN"] == str(row[10]):
                        item["quantidade"] += row[7]
                        item["valor"] += row[8]
                        adicionado = True
                if adicionado is False:
                    lista_produtos.append(produto)
                if loops == len(new_dados):
                    quantiade_envios += ajustar_e_enviar(
                        tupla_dados=row_dados, produtos=lista_produtos
                    )
                row_dados = row

            else:
                quantiade_envios += ajustar_e_enviar(
                    tupla_dados=row_dados, produtos=lista_produtos
                )
                if loops == len(new_dados):
                    quantiade_envios += ajustar_e_enviar(
                        tupla_dados=row, produtos=lista_produtos
                    )
                lista_produtos.clear()
                lista_produtos.append(produto)
                row_dados = row
                cupom_anterior = cupom[0]
        return quantiade_envios
    except Exception as error:
        log.error("%s test", str(error), exc_info=True)
        sys.exit(1)


def main() -> bool:
    """Função principal responsável por chamar as demais funções,
    inicia extraindo os dados através da função `connect_oracle` utilizando
    uma variável `SELECT` que está contida em um arquivo secrets.
    Recebendo os dados direto do banco ele faz um for em cada linha para
    verificar se a chavesat está gravada no arquivo `valor_log.log` caso não
    esteja, ele acumula as informações em uma lista para ser enviado para a
    função `juntar_produtos` que irá fazer o envio via API e retornará a
    quantidade de envios com sucesso.

    Returns:
        bool: Retorna valor true para que o schedule prossiga com a próxima
        tarefa
    """
    dados_recentes = []
    try:
        dados = connect_oracle(select=settings.SELECT)
        for row in dados:
            cupom = row[2].split("|")
            if len(cupom) > 1:
                if cupom[0] in ler_valor():
                    continue
                else:
                    if cupom[3] != "":
                        dados_recentes.append(row)
                    else:
                        continue
            else:
                continue
        envio = juntar_produtos(new_dados=dados_recentes)
    except Exception as error:
        log.error("%s test", str(error), exc_info=True)
        sys.exit(1)
    if envio == 1:
        print(f"Total de {envio} registro enviado com sucesso!")
    elif envio > 1:
        print(f"Total de {envio} registros enviados com sucesso!")
    else:
        print(f"Nenhum registro disponível para ser enviado {envio}")
    return True
