from datetime import datetime

agora = datetime.now().date()

hoje =  agora.strftime("%d-%m-%Y")

print(hoje)
print(agora)

def calculaTempo(data):
    
# Obter a data e hora atuais

    dataold = (data).split(" ")[0]

    dataconvertida = datetime.strptime(dataold, "%d/%m/%Y").date()
    print(dataold)
    result = (agora - dataconvertida).days
    if (result > 30):
        return True
    else:
        return False

def calculaIdade(data):
    ano = agora.year
    dataold = (datetime.strptime(data, "%d/%m/%Y").date()).year
    print(ano)
    print(dataold)
    calculo = ano - dataold
    print(f'Idade: {calculo}')
    if(calculo > 18):
        return True
    else:
        return False