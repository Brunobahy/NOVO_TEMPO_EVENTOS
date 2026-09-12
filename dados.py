import pandas as pd
import sys
import os
from pathlib import Path

# Função para localizar arquivos do Excel ao rodar como .exe ou script Python


class Pessoa:
    def __init__(self, pedido) -> None:
        print(pedido)
        self.nome = pedido["NOME DO USUARIO"]
        self.phone = pedido["CELULAR DO USUARIO"]
        self.revista = "Eu no Universo"
        self.cpf = str(pedido["CPF"]).zfill(11)
        self.cep = ""
        self.num = ""
        self.rua = ""
        self.bairro = ""
        self.complemento = ""
        self.pedido = pedido
        self.checkbox = None
        self.atualizaEndereco()
        self.novo = False

    def atualizaEndereco(self):
        igrejas = read_file("Endereço igrejas.xlsx")

        for igreja in igrejas:
            endereco = igreja["Endereço"].split()
            try:
                self.num = igreja["Número"]
            except:
                pass
            for parte in endereco:
                if parte.isdigit() is None:
                    self.num = parte
                else:
                    self.rua += f" {parte}"
            self.cep = igreja["CEP"]
            self.bairro = igreja["Bairro"]
            self.complemento = igreja["Complemento "]
            break


def get_name(name_part: str) -> str:
    base_path = os.getcwd()
    arquivos_list = os.listdir(base_path)
    nome_arquivo = None
    for arquivo in arquivos_list:
        if (
            name_part in arquivo
            and ".csv" in arquivo
            or name_part in arquivo
            and ".xlsx" in arquivo
        ):
            return arquivo


def get_excel_path(filename: str) -> str:
    """
    Retorna o caminho absoluto do arquivo Excel.
    - Se rodando como .exe, pega a pasta do executável
    - Se rodando como script Python, pega a pasta do script
    """
    try:
        file = Path(filename)
        if file.exists():
            return file
    except:
        pass

    base_path = (
        os.path.dirname(sys.executable)
        if getattr(sys, "frozen", False)
        else os.path.dirname(os.path.abspath(__file__))
    )
    arquivo = get_name(filename)
    return os.path.join(base_path, arquivo)


# Função para localizar arquivos csv ao rodar como .exe ou script Python
def get_csv_path(filename: str) -> str:
    base_path = os.getcwd()
    arquivo = get_name(filename)
    return os.path.join(base_path, arquivo)


# Lendo o Excel com pandas
def read_file(namePart):

    try:
        df = pd.read_csv(get_csv_path(namePart), delimiter=";")
        print("CSV")
        # df.to_excel('teste.xlsx',index=False)
    except:
        df = pd.read_excel(get_excel_path(namePart))
        print("EXCEL")

    file = df.to_dict("records")
    print(f"Total de pedidos: {len(file)}")
    return file


# Função para criar um novo arquivo Excel
def cria_arquivo_excel(lista, nome):
    df_novo = pd.DataFrame(lista)
    df_novo.to_excel(os.path.join(os.getcwd(), f"{nome}.xlsx"), index=False)
    print(f'Arquivo "{nome}.xlsx" criado com sucesso.')


def cria_arquivo_csv(lista, nome):
    df_novo = pd.DataFrame(lista)
    df_novo.to_csv(os.path.join(os.getcwd(), f"{nome}.csv"), index=False)
    print(f'Arquivo "{nome}.csv" criado com sucesso.')


# Função para atualizar o arquivo principal
def atualizaArquivo(lista: list[Pessoa], arquivo: list[dict]):
    print(f"Foram feitos: {len(lista)}")
    if len(lista) > 0:
        print("Excluindo os seguintes nomes:")
        for i in lista:
            print(i.get("NOME DO USUARIO", "N/A"))
            # Remove do pedido original se existir
            if i in arquivo:
                arquivo.remove(i)

        # Salva o arquivo atualizado ao lado do .exe
        df_atualizado = pd.DataFrame(arquivo)
        nome = get_name("Inscritos")
        if ".csv" in nome:
            df_atualizado.to_csv(nome, index=False)
        else:
            df_atualizado.to_excel(nome, index=False)
        print(f"Arquivo atualizado com sucesso!")
    else:
        print("Nenhum item para atualizar.")


# Exemplo de uso:
# criaArquivo(pedidos, 'novos_pedidos')
# atualizaArquivo([pedidos[0]])  # Exclui o primeiro pedido, por exemplo

if __name__ == "__main__":
    arquivo = read_file("Inscritos")
