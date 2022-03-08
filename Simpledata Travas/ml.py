import requests
from bs4 import BeautifulSoup
import pandas as pd
from lxml import etree
import re
from datetime import datetime

class Produto:
    def __init__(self,titulo,vendidos,vendedor,preco,kit):
        
        self.titulo = titulo
        self.vendidos = vendidos
        self.vendedor = vendedor
        self.preco = preco
        self.kit = kit
        
def limpavendidos(texto):
    avend = texto.split("|")
    if(len(avend)>1):
        vendidos = avend[1].replace("<\/?\[[0-9]+>","")
        qtde = int(re.search(r'\d+',vendidos).group())
    else:
        qtde = 0
    return qtde
    
def PegaPaginas(pag1):
    HEADERS = ({'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',\
        'Accept-Language': 'en-US, en;q=0.5'})
    
    page = requests.get(pag1, headers=HEADERS)
    status = page.status_code
    if(status != 200):
        return ""
    else:
        soup = BeautifulSoup(page.content, 'html.parser')
        dom = etree.HTML(str(soup))
        xpathproximapag = '//*[contains(@class, "andes-pagination__link ui-search-link")]/@href'
        linkPROXIMAPAG = dom.xpath(xpathproximapag)
        if(len(linkPROXIMAPAG) > 0):
            print(linkPROXIMAPAG[0])
            return linkPROXIMAPAG[0]
        else:
            return ""
    
def PegaQtdeKit(texto):
    kit=0
    sem65 = texto.replace('Mm3d 654420',"")
    sem65 = sem65.replace('65',"")
    for i in range(7):
        if(sem65.find(f"{i}") >= 0):
            kit = i
            print(kit)
            break
        
    return kit
    
    
def scrap_page(pagina: str):
    """ 
    Retorna informações do estado brasileiro
    
    :param state: nome do estado
    :return state_dict: dicionario com indicadores do estado
    """
    
    #Para cada estado/uf é o mesmo link mudando somente o state
    #exemplo: state ='sp'
    #state_url = f"https://cidades.ibge.gov.br/brasil/{state}/panorama"
    HEADERS = ({'User-Agent':
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',\
        'Accept-Language': 'en-US, en;q=0.5'})
    
    tabela = pd.DataFrame()
    
    page = requests.get(pagina, headers=HEADERS)
    status = page.status_code
    print(f'Picking {pagina} info... [{status}]')
    soup = BeautifulSoup(page.content, 'html.parser')
    dom = etree.HTML(str(soup))
    
    xpathlinks = '//*[@id="root-app"]/div/div/section/ol/li/div/div/a[@title]/@href'
    
    links = dom.xpath(xpathlinks)
    #anuncio,vendidos,vendedor,preco,qtde
    for link in links:
        anuncio = requests.get(link, headers=HEADERS)
        soup2 = BeautifulSoup(anuncio.content, 'html.parser')
        dom2 = etree.HTML(str(soup2))
        print('\n')
        titulos = dom2.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "ui-pdp-title", " " ))]')
        titulo = titulos[0].text
        print(f'Anuncio: {titulo}')
        
        kit = PegaQtdeKit(titulo)
        
        
            
        novoevendidos = dom2.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "ui-pdp-subtitle", " " ))]')
        vendidos = limpavendidos(novoevendidos[0].text)
        
        print(f'{vendidos} vendidos')
        
        vendedores = dom2.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "andes-table__column--value", " " ))]')
        if(len(vendedores) == 0):
            vendedor =""
        else:
            vendedor = vendedores[0].text
        #print(vendedor)
        
        locais = dom2.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "ui-seller-info__status-info__subtitle", " " ))]')
        local = locais[0].text
        print(f'Vendedor: {vendedor} ({local})')
        vendedor = f'{vendedor} ({local})'
        
        reais = dom2.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "ui-pdp-price__second-line", " " ))]//*[contains(concat( " ", @class, " " ), concat( " ", "andes-money-amount__fraction", " " ))]')
        real = reais[0].text
        
        centavos =  dom2.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "andes-money-amount__cents--superscript-36", " " ))]')
        if(len(centavos) > 0):
            centavo = centavos[0].text
        else:
            centavo = "00"
        
        preco = f'{real}.{centavo}'
        print(f'R$ {real}.{centavo}')
        
        
        
        #item = Produto(titulo,vendidos,vendedor,preco,kit)
        item = {
            'titulo': titulo,
            'vendidos': vendidos,
            'vendedor': vendedor,
            'preco': preco,
            'kit': kit
            }
        
        #output = pd.DataFrame()
        df_dictionary = pd.DataFrame([item])
        tabela = pd.concat([tabela,df_dictionary],ignore_index=True)
        
    return tabela
        
       
#inicio
tabela = pd.DataFrame()

pag1 = "https://games.mercadolivre.com.br/games/trava-cadeira-gamer_OrderId_PRICE_NoIndex_True" 
tabelatemp = tabela
pagatual = pag1
paganterior = pag1
while True:
    tabelatemp = scrap_page(pagatual)
    tabela = pd.concat([tabela,tabelatemp], ignore_index=True)
    proximapag = PegaPaginas(pagatual)   
    if(len(proximapag) > 0):
        if(proximapag == pag1):
            break
        else:
            if(proximapag == paganterior):
                break
            else:
                paganterior = pagatual
                pagatual = proximapag
    else:
        break


datadodia = datetime.today().strftime('%Y%m%d')
print(tabela)
arquivo = f'{datadodia}.xlsx'
tabela.to_excel(arquivo)






