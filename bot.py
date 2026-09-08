from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from dados import Pessoa, read_file, cria_arquivo_excel, atualizaArquivo
from calcData import calculaTempo, hoje, calculaIdade
import sys
import os
import json
import threading
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from datetime import datetime

link = "https://www7.novotempo.com/Corporate1"


def get_path(filename):
    # Retorna o caminho absoluto do arquivo Excel.
    base_path = (
        os.path.dirname(sys.executable)
        if getattr(sys, "frozen", False)
        else os.path.dirname(os.path.abspath(__file__))
    )
    return os.path.join(base_path, filename)


Dadoslogin = get_path("pass.json")

with open(Dadoslogin, "r", encoding="utf-8") as f:
    dados = json.load(f)
login = dados["login"]
senha = dados["senha"]


# Caminho para o ChromeDriver

edgedriver_path = (
    Path(__file__).parent / "drivers" / "msedgedriver.exe"
)  # Coloque o chromedriver na mesma pasta do exe ou no PATH


def espera(num):
    time.sleep(num)


# Arrays para criar planilhas
feitos = []
novos = []
enviados = []
erros = []
pedidos = read_file("Inscritos")
# Variaveis
global stop_flag
stop_flag = False
lb_num = None
lb_erro = None
lb_cadastros = None
lb_novos = None
janela = None


def abre_navegador():
    global nv
    navegador = webdriver.Edge()
    navegador.get(link)
    nv = navegador


def erro_executa(pedido: Pessoa, erro):
    erros.append(pedido.pedido)
    print(erro)
    print(f"Erro ao realizar o pedido de {pedido.nome}")
    nv.get("https://www7.novotempo.com/Corporate1/attendance/attendanceWindow.zul")
    atualizar_label()


def try_maker(func, *args):
    try:
        print(func.__name__)
        func(*args)
        return True
    except Exception as e:
        erro_executa(*args, e)
        return False


def await_by_class(cls: str) -> None:
    WebDriverWait(nv, 5).until(EC.presence_of_element_located((By.CLASS_NAME, cls)))


def await_by_xpath(xpth: str) -> None:
    WebDriverWait(nv, 5).until(EC.presence_of_element_located((By.XPATH, xpth)))


def await_by_css(css: str) -> None:
    WebDriverWait(nv, 5).until(EC.presence_of_element_located((By.XPATH, css)))


def await_load():
    print("Esperando LOAD")
    espera(1)
    try:
        load = nv.find_element(By.CLASS_NAME, "z-loading")
        if load:
            print("Outro LOAD")
            await_load()
    except:
        print("Saindo LOAD")
        return


def logar_atendimento():

    campoUser = nv.find_element("class name", "z-textbox")
    campoSenha = nv.find_element("class name", "z-pass")
    campoUser.send_keys(login)
    campoSenha.send_keys(senha)

    nv.find_element("class name", "z-button-cm").click()
    WebDriverWait(nv, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "applications"))
    )
    nv.find_elements(By.CLASS_NAME, "z-a")[2].click()
    WebDriverWait(nv, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, "z-menu-popup"))
    )
    nv.find_element(By.CLASS_NAME, "z-menu-btn").click()
    nv.find_element(By.CLASS_NAME, "z-menu-btn").click()
    nv.find_elements(By.CLASS_NAME, "z-menu-item-cnt")[3].click()
    nv.maximize_window()


def acessa_user(dados: Pessoa, i):
    if i % 4 == 0 and i != 0:
        nv.refresh()
        espera(5)
    else:
        print("não é recarregar a pagina")

    nv.execute_script("window.scrollTo(0, 0);")

    print("****************************")
    print("Dados: ")
    print(f"{dados.nome}  {dados.cpf}")
    print("****************************")

    print(dados.pedido)

    await_by_xpath("//span[text()='Pessoas']")

    nv.execute_script("window.scrollTo(0, 0);")
    nv.find_element(By.XPATH, "//span[text()='Pessoas']").click()

    # await_by_css('select')
    espera(5)
    # escolhe CPF
    nv.find_element(By.CSS_SELECTOR, "select").click()
    nv.find_elements(By.CSS_SELECTOR, "option")[8].click()

    cpf = nv.find_elements(By.CLASS_NAME, "z-textbox")[5]

    cpf.send_keys(dados.cpf)

    espera(1)

    nv.find_elements(By.CLASS_NAME, "z-button-cm")[6].click()

    # tenta acessar o usuario que já existe!
    print("tenta acessar o usuario que já existe!")

    espera(3)
    # acessa cadastro 'pessoa'
    pessoa = nv.find_element(By.CLASS_NAME, "z-listitem")

    ActionChains(nv).double_click(pessoa).perform()
    await_load()


def registra_user(dados: Pessoa):
    print(f"*****************")
    print(f"CPF {dados.cpf} não registrado")
    print(f"***************")
    # registra uma nova pessoa
    print("registra uma nova pessoa")
    nv.find_element(By.XPATH, "//td[normalize-space(text())='Novo']").click()
    await_load()

    # coloca Celular
    print("coloca Celular")
    nv.find_elements(By.CLASS_NAME, "z-textbox")[34].send_keys(
        str(dados.phone).replace("+55", "")
    )

    # nv.find_elements(By.CLASS_NAME, "z-datebox-inp")[1].send_keys(dados.)
    # nv.find_elements(By.CLASS_NAME, "z-datebox-inp")[1].click()

    # nv.find_elements(By.CLASS_NAME, "z-combobox-btn")[5].click()
    # if dados["sexo"] == "Feminino":
    #     ActionChains(nv).send_keys(Keys.ARROW_DOWN).send_keys(
    #         Keys.ARROW_DOWN
    #     ).send_keys(Keys.ENTER).perform()
    # else:
    #     ActionChains(nv).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()

    # coloca o email
    print("coloca o email")

    # nv.find_elements(By.CLASS_NAME, "z-button-cm")[20].click()
    # espera(2)
    # nv.find_elements(By.CLASS_NAME, "z-textbox")[42].send_keys(dados["email"])
    # nv.find_element(
    #     By.CSS_SELECTOR, ".z-window-highlighted-icon.z-window-highlighted-close"
    # ).click()

    # coloca Nome
    print("coloca Nome")
    espera(1)
    nv.find_elements(By.CLASS_NAME, "z-textbox")[8].clear()
    nv.find_elements(By.CLASS_NAME, "z-textbox")[8].send_keys(dados.nome)

    # coloca CPF
    print("coloca CPF")
    espera(1)
    nv.find_elements(By.CLASS_NAME, "z-textbox")[6].send_keys(dados.cpf)
    espera(2)

    # nv.find_elements(By.CLASS_NAME, "z-combobox-inp")[12].send_keys(
    #     dados["estado_civil"]
    # )
    # nv.find_elements(By.CLASS_NAME, "z-combobox-btn")[12].click()
    # nv.find_elements(By.CLASS_NAME, "z-combobox-btn")[12].click()

    # acessa 'endereço escola biblica'
    print("acessa 'endereço escola biblica'")

    nv.find_elements(By.CLASS_NAME, "z-tab-text")[10].click()
    # coloca CEP e Num
    print("coloca CEP e Num")
    await_load()
    nv.find_elements(By.CLASS_NAME, "z-textbox")[26].send_keys(dados.cep)
    nv.find_elements(By.CLASS_NAME, "z-textbox")[28].send_keys(dados.num)

    # coloca complemento
    print("coloca complemento")
    await_load()
    nv.find_elements(By.CLASS_NAME, "z-textbox")[29].send_keys(dados.complemento)
    # se não puxar rua e bairro coloca eles
    print("se não puxar rua e bairro coloca eles")

    if nv.find_elements(By.CLASS_NAME, "z-textbox")[27].get_attribute("value") == "":
        if len(dados.rua) > 50:
            rua = dados.rua[0:49]
        else:
            rua = dados.rua
        nv.find_elements(By.CLASS_NAME, "z-textbox")[27].send_keys(dados.rua)
    if nv.find_elements(By.CLASS_NAME, "z-textbox")[30].get_attribute("value") == "":
        nv.find_elements(By.CLASS_NAME, "z-textbox")[30].send_keys(dados.bairro)
    espera(1)

    # salva o novo usuario
    print("salva o novo usuario")

    nv.find_elements(By.CLASS_NAME, "z-button-cm")[27].click()

    try:
        espera(5)
        ActionChains(nv).send_keys(Keys.ENTER).perform()
        ActionChains(nv).send_keys(Keys.ENTER).perform()
        espera(3)
        nv.find_elements(By.CLASS_NAME, "z-button-cm")[20].click()
        espera(1)
        nv.find_element(By.CSS_SELECTOR, "button[title]").click()
        espera(1)
        nv.find_element(
            By.CSS_SELECTOR, ".z-window-highlighted-icon.z-window-highlighted-close"
        ).click()
        espera(1)
        nv.find_elements(By.CLASS_NAME, "z-button-cm")[27].click()
        await_load()
    except:
        print("Email não duplicado!")
    espera(2)

    nv.execute_script("window.scrollTo(0, 0);")


def atualiza_user(dados: Pessoa):
    print("extrai os dados dos campos e compara com a planilha")

    campos = nv.find_elements(By.CLASS_NAME, "z-textbox")

    campo_cep = campos[26].get_attribute("value")
    campo_num = campos[28].get_attribute("value")
    campo_phone = campos[34].get_attribute("value")

    dados.cep = dados.cep.replace("-", "").replace(" ", "")
    campo_cep = campo_cep.replace("-", "")
    campo_phone = (
        campo_phone.replace("(", "").replace(")", "").replace("-", "").replace(" ", "")
    )

    dados.phone = (
        dados.phone.replace("+55", "")
        .replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
    )

    # vai para o campo escola biblica e altera dados errados
    print("vai para o campo escola biblica e altera dados errados")

    nv.find_elements(By.CLASS_NAME, "z-tab-text")[10].click()

    alterado = False

    # verifica CEP
    print("verifica CEP")
    espera(2)
    dtNascimento = nv.find_elements(By.CLASS_NAME, "z-datebox-inp")[1].get_attribute(
        "value"
    )

    if not campo_cep:

        if str(campo_cep) != str(dados.cep):

            campos[26].clear()
            campos[26].send_keys(dados.cep)
            campos[28].click()
            espera(10)
            alterado = True

            try:
                espera(2)
                nv.find_element(
                    By.CSS_SELECTOR, ".z-messagebox-btn.z-button-os"
                ).click()
                dtNascimento = "18/01/2025"
            except:
                print(f"CEP {dados.cep} Existe")

        # verifica numero
        print("verifica numero")
        if str(campo_num) != str(dados.num) or alterado:
            espera(5)
            campos[28].clear()
            campos[28].click()
            campos[28].send_keys(dados.num)

        espera(2)

        if (
            nv.find_elements(By.CLASS_NAME, "z-textbox")[27].get_attribute("value")
            == ""
        ):
            if len(dados.rua) > 50:
                rua = dados.rua[0:49]
            else:
                rua = dados.rua
            nv.find_elements(By.CLASS_NAME, "z-textbox")[27].send_keys(rua)
            alterado = True
        if (
            nv.find_elements(By.CLASS_NAME, "z-textbox")[30].get_attribute("value")
            == ""
        ):
            nv.find_elements(By.CLASS_NAME, "z-textbox")[30].send_keys(dados.bairro)
            alterado = True
        espera(1)
    #     alterado = True

    # verifica celular
    print("verifica celular")
    if campo_phone != dados.phone:

        campos[34].clear()
        espera(5)
        campos[34].send_keys(dados.phone)
        alterado = True

    campos[35].clear()

    nv.find_elements(By.CLASS_NAME, "z-tab-text")[15].click()
    espera(1)
    dados.checkbox = (
        nv.find_elements(By.CLASS_NAME, "z-checkbox")[6]
        .find_element(By.TAG_NAME, "input")
        .get_attribute("checked")
    )

    # salvar alterações
    print("salvar alterações")

    if (dtNascimento == "" or calculaIdade(dtNascimento)) and alterado:
        nv.find_elements(By.CLASS_NAME, "z-button-cm")[28].click()
    else:
        nv.find_elements(By.CLASS_NAME, "z-button-cm")[29].click()

    await_load()
    try:
        nv.find_element(By.CLASS_NAME, "z-window-highlighted-close").click()
        nv.find_element(By.CLASS_NAME, "z-window-highlighted-close").click()
    except:
        ActionChains(nv).send_keys(Keys.ESCAPE).perform()
        ActionChains(nv).send_keys(Keys.ESCAPE).perform()


def envia_lgpd(dados: Pessoa):
    nv.execute_script("window.scrollTo(0, 0);")

    listError = nv.find_elements(By.CLASS_NAME, "z-errbox-center")
    if len(listError) > 0:
        nv.find_elements(By.CLASS_NAME, "z-button-cm")[29].click()

    espera(5)

    try:
        btnPessoas = nv.find_element(By.XPATH, "//span[text()='Pessoas']")
        nv.execute_script("window.scrollTo(0, 0);")
        btnPessoas.click()
    except:
        ActionChains(nv).send_keys(Keys.ENTER).perform()
        espera(5)
        nv.execute_script("window.scrollTo(0, 0);")
        nv.find_element(By.XPATH, "//span[text()='Pessoas']").click()

    print("enviar LGPD")
    nv.execute_script("window.scrollTo(0, 0);")
    espera(1)
    nv.find_elements(By.CLASS_NAME, "z-tab-text")[15].click()

    # checkbox = (
    #     nv.find_elements(By.CLASS_NAME, "z-checkbox")[6]
    #     .find_element(By.TAG_NAME, "input")
    #     .get_attribute("checked")
    # )

    # if checkbox == "false":

    # if dados["lgpd"] == "SMS":
    nv.find_elements(By.CLASS_NAME, "blue")[1].click()
    # elif (
    #     nv.find_elements(By.CLASS_NAME, "z-textbox-real-readonly")[1].get_attribute(
    #         "value"
    #     )
    #     != ""
    # ):
    #     nv.find_elements(By.CLASS_NAME, "green")[1].click()
    espera(2)
    ActionChains(nv).send_keys(Keys.ENTER).perform()
    espera(1)
    nv.find_element(By.CLASS_NAME, "z-window-highlighted-close").click()


def envia_revista(dados: Pessoa):

    # await_by_xpath("//span[text()='Atendimento' and contains(@class, 'z-tab-text') ]")
    await_load()
    nv.execute_script("window.scrollTo(0, 0);")

    print("acessa Atendimentos")
    nv.find_element(
        By.XPATH, "//span[text()='Atendimento' and contains(@class, 'z-tab-text') ]"
    ).click()
    print("esperando 2")
    espera(2)
    print("esperando 2")

    if not dados.novo:
        # abre 'historico' 'todos'
        print("abre 'historico' 'todos'")

        # encontra Botões
        print("encontra Botões")

        btns = nv.find_elements(By.CLASS_NAME, "z-button-cm")
        espera(1)
        btns[54].click()
        await_load()

        # Filtra apenas cursos biblicos
        print("Filtra apenas cursos biblicos")

        filtro = nv.find_elements(By.CSS_SELECTOR, ".z-combobox-inp")[18].get_attribute(
            "value"
        )
        if filtro != "Curso Bíblico":
            nv.find_elements(By.CSS_SELECTOR, ".z-combobox-btn")[18].click()
            espera(1)
            ActionChains(nv).send_keys(Keys.ARROW_DOWN).send_keys(
                Keys.ARROW_DOWN
            ).send_keys(Keys.ENTER).perform()
            espera(5)
        else:
            nv.find_elements(By.CSS_SELECTOR, ".z-combobox-btn")[18].click()
            ActionChains(nv).send_keys(Keys.ARROW_DOWN).send_keys(
                Keys.ARROW_DOWN
            ).send_keys(Keys.ENTER).perform()
            espera(2)
            ActionChains(nv).send_keys(Keys.ARROW_UP).send_keys(
                Keys.ARROW_UP
            ).send_keys(Keys.ENTER).perform()
            espera(5)

        # valida data
        print("valida data ")
        tab = nv.find_elements(By.CSS_SELECTOR, ".z-listbox-body")[5]
        cels = tab.find_elements(By.CSS_SELECTOR, ".z-listcell[title]")

        try:
            data = cels[1].get_attribute("title")
        except:
            data = "05/11/2022 10:16:27"
    else:
        data = "05/11/2022 10:16:27"

    # verifica se pode enviar revista
    print("verifica se pode enviar revista")
    if calculaTempo(data):
        print("Enviar revista")

        # abre formulario revista
        print("abre form revista")
        nv.find_element(
            By.XPATH, '//td[@class="z-button-cm" and text()="Curso Bíblico"]'
        ).click()
        espera(3)

        # escolhe o campo com o nome da revista
        print("escolhe o campo com o nome da revista")
        print(f"Pedidondo revista: {dados.revista}")
        nv.find_elements(By.CLASS_NAME, "z-combobox-inp")[26].send_keys(dados.revista)
        espera(1)
        nv.find_elements(By.CLASS_NAME, "z-combobox-inp")[26].click()
        espera(2)
        tela = nv.find_elements(By.CLASS_NAME, "z-fieldset")[6]
        tela.find_elements(By.CLASS_NAME, "z-button-os")[1].click()

        try:
            espera(3)
            nv.find_elements(By.CSS_SELECTOR, ".z-messagebox-btn.z-button-os")[
                0
            ].click()
            espera(5)
        except:
            await_load()
        # continuar pedindo revista
        print("continuar pedindo revista")
        enviados.append(dados.pedido)
    else:
        print("já pediu revista")
    ## Fechar atendimento
    print("Fechar atendimento")

    # preenche INICIATIVA
    print("preenche INICIATIVA")

    nv.execute_script("window.scrollTo(0, 0);")
    nv.find_element(By.CLASS_NAME, "z-bandbox-inp").click()
    nv.find_element(By.CLASS_NAME, "z-bandbox-inp").send_keys("Rádio Florianópolis")
    espera(1)
    ActionChains(nv).send_keys(Keys.ENTER).perform()
    espera(3)
    ActionChains(nv).send_keys(Keys.ENTER).perform()
    espera(3)

    # preenche 'Rádio'
    print("preenche 'Rádio'")
    nv.find_elements(By.CLASS_NAME, "z-combobox-btn")[15].click()
    espera(3)
    ActionChains(nv).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ENTER).perform()

    # Preenche AM/FM
    print("preenche AM/FM")

    nv.find_elements(By.CLASS_NAME, "z-combobox-btn")[16].click()
    espera(3)
    ActionChains(nv).send_keys(Keys.ARROW_DOWN).send_keys(Keys.ARROW_DOWN).send_keys(
        Keys.ENTER
    ).perform()


def automacao():

    # abre navegador
    abre_navegador()
    logar_atendimento()
    # Começa o loop

    for i, pedido in enumerate(pedidos):

        try:
            campoUser = nv.find_element("class name", "z-textbox")
            if campoUser:
                logar_atendimento()
        except:
            pass

        if stop_flag:
            nv.quit()
            break
        dados = Pessoa(pedido)
        try:
            acessa_user(dados, i)
            if not try_maker(atualiza_user, dados):
                continue

        except:
            dados.novo = True
            if not try_maker(registra_user, dados):
                continue

        # enviar LGPD
        print(dados.checkbox)
        if not dados.checkbox:
            if not try_maker(envia_lgpd, dados):
                continue

        if not try_maker(envia_revista, dados):
            continue

        # salva e fecha
        print("salva e fecha")
        btnSalvar = nv.find_element(
            By.XPATH, "//td[contains(text(), 'Salvar e Fechar')]"
        )
        btnSalvar.click()

        nv.execute_script("window.scrollTo(0, 0);")

        espera(2)
        try:
            nv.find_elements(By.CSS_SELECTOR, ".z-messagebox-btn.z-button-os")[
                0
            ].click()
        except:
            ActionChains(nv).send_keys(Keys.ENTER).perform()

        await_load()
        feitos.append(dados.pedido)
        if dados.novo:
            novos.append(dados.pedido)

        # altera janela
        if janela:
            janela.after(0, atualizar_label)


def iniciar_automacao():
    thread = threading.Thread(target=automacao)
    thread.start()


def parar_automacao():
    global stop_flag
    stop_flag = True
    messagebox.showinfo("Status", "Automação será encerrada.")


def atualizar_label():
    if lb_num:
        lb_num.config(text=f"{len(feitos)}")
    if lb_erro:
        lb_erro.config(text=f"{len(erros)}")
    if lb_novos:
        lb_novos.config(text=f"{len(novos)}")
    if lb_enviado:
        lb_enviado.config(text=f"{len(enviados)}")


def criar_interface():
    global lb_num, lb_erro, lb_cadastros, lb_novos, janela, lb_enviado

    janela = tk.Tk()
    janela.title("Controle da Automação")
    janela.geometry("300x200")

    label = tk.Label(janela, text="Automação Selenium", font=("Arial", 14))
    label.pack(pady=10)

    # Frame para organizar os labels lado a lado
    frame_status = tk.Frame(janela)
    frame_status.pack(pady=5)

    # --- Coluna 1: Feitos ---
    tk.Label(frame_status, text="Feitos", font=("Arial", 11, "bold")).grid(
        row=0, column=0, padx=10
    )
    lb_num = tk.Label(frame_status, text="0", font=("Arial", 12))
    lb_num.grid(row=1, column=0)

    # --- Coluna 2: Erros ---
    tk.Label(frame_status, text="Erros", font=("Arial", 11, "bold")).grid(
        row=0, column=1, padx=10
    )
    lb_erro = tk.Label(frame_status, text="0", font=("Arial", 12))
    lb_erro.grid(row=1, column=1)

    # --- Coluna 4: Novos ---
    tk.Label(frame_status, text="Novos", font=("Arial", 11, "bold")).grid(
        row=0, column=2, padx=10
    )
    lb_novos = tk.Label(frame_status, text="0", font=("Arial", 12))
    lb_novos.grid(row=1, column=2)

    # --- Coluna 5: enviados ---
    tk.Label(frame_status, text="Enviados", font=("Arial", 11, "bold")).grid(
        row=0, column=3, padx=10
    )
    lb_enviado = tk.Label(frame_status, text="0", font=("Arial", 12))
    lb_enviado.grid(row=1, column=3)
    # --- botões ---

    btn_iniciar = tk.Button(janela, text="Iniciar", width=12, command=iniciar_automacao)
    btn_iniciar.pack(pady=5)

    btn_parar = tk.Button(janela, text="Parar", width=12, command=parar_automacao)
    btn_parar.pack(pady=5)

    janela.mainloop()


criar_interface()


print("****************")
if feitos:
    cria_arquivo_excel(feitos, f"Feitos {datetime.now().date().strftime("%d-%m")}")
if novos:
    cria_arquivo_excel(novos, f"Novos {datetime.now().date().strftime("%d-%m")}")
if erros:
    cria_arquivo_excel(erros, f"Erros {datetime.now().date().strftime("%d-%m")}")
if enviados:
    cria_arquivo_excel(enviados, f"Enviados {datetime.now().date().strftime("%d-%m")}")

try:
    atualizaArquivo(feitos, pedidos)
except:
    print("Erro ao atualizar a planilha")

print(login)
print(senha)
print(link)

# Verificar se encontra um classe, se não ele pode continuar
# z-loading
