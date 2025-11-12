"""
Script para normalizar a coluna 'nome' do arquivo canais_aquisicao_rows.csv
usando o mesmo padrão aplicado em clientes_vixen_completo.csv
"""

import pandas as pd
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / 'dados_processados' / 'originais' / 'estruturas_do_banco' / 'canais_aquisicao_rows.csv'

# Mapeamento expandido de normalizações (incluindo valores do canais_aquisicao)
NORMALIZACOES = {
    # Do mapeamento original
    '1ª COMPRA': '1ª Compra',
    '1ªCOMPRA': '1ª Compra',
    'ABMED': 'ABMED',
    'ABORDAGEM': 'Abordagem',
    'ADEASP': 'ADEASP',
    'AMEPLAN': 'Ameplan',
    'AMIGOS': 'Amigos',
    'ARKIMEDES CENTRO MÉDICO': 'Arkimedes Centro Médico',
    'ARKIMEDESCENTROMÉDICO': 'Arkimedes Centro Médico',
    'ASSEMBLEIA DE DEUS': 'Assembleia de Deus',
    'ASSEMBLEIADEDEUS': 'Assembleia de Deus',
    'BIO SAÚDE': 'Bio Saúde',
    'BIOSAÚDE': 'Bio Saúde',
    'BOLIVIANOS': 'Bolivianos',
    
    # Campanhas
    'CAMPANHAAILTON': 'Campanha - Ailton',
    'CAMPANHAANIVERSARIANTES': 'Campanha - Aniversariantes',
    'CAMPANHACBA': 'Campanha - CBA',
    'CAMPANHACOMPRE1LEVE3': 'Campanha - Compre 1 Leve 3',
    'CAMPANHA COMPRE 1 LEVE 3': 'Campanha - Compre 1 Leve 3',
    'CAMPANHA LYOR': 'Campanha - Lyor',
    'CAMPANHA NINJAS': 'Campanha - Ninjas',
    'CAMPANHAVADO': 'Campanha - Vado',
    'CAMPANHA VADO': 'Campanha - Vado',
    
    # Cartões
    'CARTAO DE TODOS': 'Cartão de Todos',
    'CARTAODETODOS': 'Cartão de Todos',
    'CARTÃO COMPLETO': 'Cartão Completo',
    'CARTÃOCOMPLETO': 'Cartão Completo',
    'CARTÃO INDICAÇÃO': 'Cartão Indicação',
    'CARTÃOINDICAÇÃO': 'Cartão Indicação',
    
    # Outros
    'CARRETA': 'Carreta',
    'CARRO DE SOM': 'Carro de Som',
    'CESTA BÁSICA': 'Cesta Básica',
    'CESTABÁSICA': 'Cesta Básica',
    
    # Clínicas
    'CLINICA': 'Clínica',
    'CLINICA ALPHA VISION': 'Clínica Alpha Vision',
    'CLINICAALPHAVISION': 'Clínica Alpha Vision',
    'CLINICA DIMEG': 'Clínica Dimeg',
    'CLINICA MED': 'Clínica Med',
    
    # Convênios
    'CLUB GOLD STAR': 'Club Gold Star',
    'CONVENIO FAN': 'Convênio FAN',
    'CONVENIOFAN': 'Convênio FAN',
    'CONVENIO FL': 'Convênio FL',
    'CONVENIO INTERMÉDICA': 'Convênio Intermédica',
    'CONVENIO JASON': 'Convênio Jason',
    'CONVENIO MWI': 'Convênio MWI',
    'CONVENIO PARTMED': 'Convênio Partmed',
    'CRUZ AZUL': 'Cruz Azul',
    
    # Médicos
    'DR ALEXANDRE TOMIO UMINO': 'Dr. Alexandre Tomio Umino',
    'DR ALLAN GOMES DA SILVA': 'Dr. Allan Gomes da Silva',
    'DR AMANDA A VV DE CASTRO': 'Dra. Amanda A. V. V. de Castro',
    'DRAMANDAAVVDECASTRO': 'Dra. Amanda A. V. V. de Castro',
    'DR ANESIO RUIZ': 'Dr. Anesio Ruiz',
    'DR BEATRIZ NAKAGOME': 'Dra. Beatriz Nakagome',
    'DR CAROLINA REZENDE': 'Dra. Carolina Rezende',
    'DR CRISTINA FREIRE': 'Dra. Cristina Freire',
    'DR EDSON': 'Dr. Edson',
    'DR GABRIEL CASTILHO SANDOVAL': 'Dr. Gabriel Castilho Sandoval',
    'DR GILVAN VILARINHO': 'Dr. Gilvan Vilarinho',
    'DR GUILHERME  M.KAPPEL': 'Dr. Guilherme M. Kappel',
    'DR GUILHERME H J': 'Dr. Guilherme H. J.',
    'DR GUILHERME S. MOTTA': 'Dr. Guilherme S. Motta',
    'DR JOÃO VICTOR RAMOS DE TOLEDO': 'Dr. João Victor Ramos de Toledo',
    'DR KIU SUB SHIN': 'Dr. Kiu Sub Shin',
    'DR LIVIA FERRAZ': 'Dra. Livia Ferraz',
    'DR MARCELO KENDI FUJII': 'Dr. Marcelo Kendi Fujii',
    'DR MARCIA FERRARI PEREZ': 'Dra. Marcia Ferrari Perez',
    'DR MARCOS VINICIUS PRADO': 'Dr. Marcos Vinicius Prado',
    'DR MARCUS TAKATSU': 'Dr. Marcus Takatsu',
    'DR MARIA EUGENIA BUSCA': 'Dra. Maria Eugenia Busca',
    'DR MAURICIO FLANK': 'Dr. Mauricio Flank',
    'DR RAFAEL BORGES': 'Dr. Rafael Borges',
    'DR RAFAEL PIVATTO': 'Dr. Rafael Pivatto',
    'DRRAFAELPIVATTO': 'Dr. Rafael Pivatto',
    'DR RENATO MACCIONE': 'Dr. Renato Maccione',
    'DR WALTHER CAMPOS NETO': 'Dr. Walther Campos Neto',
    'DR ÁLVARO': 'Dr. Álvaro',
    
    # Farmácias
    'DROGARIA CAMPEA': 'Drogaria Campeã',
    'DROGARIACAMPEA': 'Drogaria Campeã',
    'DROGARIA DROGALIS': 'Drogaria Drogalis',
    'DROGARIA DROGASIL': 'Drogaria Drogasil',
    'DROGARIA SUPERMED': 'Drogaria Supermed',
    'DROGARIASUPERMED': 'Drogaria Supermed',
    'DROGARIA SÃO PAULO': 'Drogaria São Paulo',
    
    # Divulgadores
    'DIVULGADOR': 'Divulgador',
    'DV ALINE CRUZ': 'Divulgador - Aline Cruz',
    'DV ANDERSON': 'Divulgador - Anderson',
    'DV ANDERSON KENION': 'Divulgador - Anderson Kenion',
    'DV BARBARA MATOS': 'Divulgador - Barbara Matos',
    'DV BRUNA RAFAELLA DA SILVA': 'Divulgador - Bruna Rafaella da Silva',
    'DV BRYAN NASCIMENTO': 'Divulgador - Bryan Nascimento',
    'DV DENILSON': 'Divulgador - Denilson',
    'DV DOUGLAS JESUS DA SILVA': 'Divulgador - Douglas Jesus da Silva',
    'DVDOUGLASJESUSDASILVA': 'Divulgador - Douglas Jesus da Silva',
    'DV EMERSON DE JESUS': 'Divulgador - Emerson de Jesus',
    'DV ERICK ANJOS': 'Divulgador - Erick Anjos',
    'DV GABRIELA SILVA': 'Divulgador - Gabriela Silva',
    'DVGABRIELASILVA': 'Divulgador - Gabriela Silva',
    'DV GRAZIELA SANTOS FERREIRA': 'Divulgador - Graziela Santos Ferreira',
    'DV JACIANE DINIZ': 'Divulgador - Jaciane Diniz',
    'DVJACIANEDINIZ': 'Divulgador - Jaciane Diniz',
    'DV JEAN LEANDRO': 'Divulgador - Jean Leandro',
    'DVJEANLEANDRO': 'Divulgador - Jean Leandro',
    'DV JOÃO PAULO': 'Divulgador - João Paulo',
    'DVJOÃOPAULO': 'Divulgador - João Paulo',
    'DV LARISSA COSTA': 'Divulgador - Larissa Costa',
    'DV LARISSA SILVA': 'Divulgador - Larissa Silva',
    'DV LETICIA': 'Divulgador - Leticia',
    'DV MAICON OLIVEIRA': 'Divulgador - Maicon Oliveira',
    'DV MARIANA COSTA': 'Divulgador - Mariana Costa',
    'DV MIKELY FORTALEZA': 'Divulgador - Mikely Fortaleza',
    'DV NATALIA': 'Divulgador - Natalia',
    'DV NAYARA COSTA': 'Divulgador - Nayara Costa',
    'DV NIKE': 'Divulgador - Nike',
    'DVNIKE': 'Divulgador - Nike',
    'DV RAFAELA GOMES': 'Divulgador - Rafaela Gomes',
    'DV ROBSON OLIVEIRA': 'Divulgador - Robson Oliveira',
    'DV SUELEN RODRIGUES': 'Divulgador - Suelen Rodrigues',
    'DVSUELENRODRIGUES': 'Divulgador - Suelen Rodrigues',
    'DV TAIS CARDOSO': 'Divulgador - Tais Cardoso',
    'DV THALITA ASSIS': 'Divulgador - Thalita Assis',
    'DV VICTOR HUGO': 'Divulgador - Victor Hugo',
    'DVVICTORHUGO': 'Divulgador - Victor Hugo',
    'DV WESLLEY ABREU': 'Divulgador - Weslley Abreu',
    
    # Diversos
    'ELIS': 'Elis',
    'EMPRESA ATENTO': 'Empresa Atento',
    'FEIRA VILA AMORIM': 'Feira Vila Amorim',
    'FLORIPARK': 'Floripark',
    'GOOGLE/FACE/INSTA - PATROCÍNIO': 'Google/Facebook/Instagram (Patrocínio)',
    'GOOGLE/FACE/INSTA-PATROCÍNIO': 'Google/Facebook/Instagram (Patrocínio)',
    'GUIMA': 'Guima',
    'HOSPITAL STELLA MARIS': 'Hospital Stella Maris',
    'IAMSPE': 'IAMSPE',
    'IGREJA PLENITUDE': 'Igreja Plenitude',
    'INDICAÇÃO': 'Indicação',
    'INDICAÇÃO CONVÊNIO PREFEITURA': 'Indicação - Convênio Prefeitura',
    'INSTITUTO SUEL ABUJAMRA': 'Instituto Suela Bujamra',
    'INSTITUTOSUELABUJAMRA': 'Instituto Suela Bujamra',
    'INTERGALAXY SA': 'Intergalaxy SA',
    'INTS': 'INTS',
    'JÁ É CLIENTE': 'Já é Cliente',
    'KOMBOS': 'Kombos',
    'LOJA FECHADA': 'Loja Fechada',
    'LUIS FIO FOLHETOS': 'Luis Fio - Folhetos',
    'LUISFIOFOLHETOS': 'Luis Fio - Folhetos',
    'Landing Page - Mello Óticas Geral': 'Landing Page - Mello Óticas Geral',
    'Landing Page - Visão para Suzano': 'Landing Page - Visão para Suzano',
    'MAGAZINE LUIZA': 'Magazine Luiza',
    'MAGAZINELUIZA': 'Magazine Luiza',
    'MARTINS LOCOCO': 'Martins Lococo',
    'MEDILINE ASSISTENCIA': 'Mediline Assistência',
    'MINDBE': 'MindBe',
    'NOVA X': 'Nova X',
    'OPEN LINE': 'Open Line',
    'ORÇAMENTO': 'Orçamento',
    'OUTDOOR': 'Outdoor',
    'OUTRA LOJA': 'Outra Loja',
    'OUTROS': 'Outros',
    'PANFLETOS': 'Panfletos',
    'PASSAGEM': 'Passagem',
    'PENITENCIARIA FEM SÃO PAULO': 'Penitenciária Feminina São Paulo',
    'PLACA DE LOJA': 'Placa de Loja',
    'PLACADELOJA': 'Placa de Loja',
    'PLENA SAÚDE': 'Plena Saúde',
    'PREFEITO NO SEU BAIRRO': 'Prefeito no Seu Bairro',
    'PREFEITURA': 'Prefeitura',
    'PREVINA JORDANESIA': 'Previna Jordanésia',
    'PROGRAMA SHOW': 'Programa Show',
    'PROJETO CUIDAR': 'Projeto Cuidar',
    'PROSPECÇÃOMABIO': 'Prospecção - Mabio',
    'QUEM INDICA AMIGO É': 'Quem Indica Amigo É',
    
    # Rádios
    'RADIO ADORE FM': 'Rádio Adore FM',
    'RADIOADOREFM': 'Rádio Adore FM',
    'RADIO ATALAIA': 'Rádio Atalaia',
    'RADIO ESPERANCA': 'Rádio Esperança',
    'RADIO FÉ 101.5': 'Rádio Fé 101.5',
    'RADIOFÉ101.5': 'Rádio Fé 101.5',
    'RADIO IMPRENSA FM': 'Rádio Imprensa FM',
    'RADIO NOVA X 103.1': 'Rádio Nova X 103.1',
    'RADIO REDE UNÇÃO 96.5': 'Rádio Rede Unção 96.5',
    'RADIOREDEUNÇÃO96.5': 'Rádio Rede Unção 96.5',
    'RADIO TERRA': 'Rádio Terra',
    'RADIOTERRA': 'Rádio Terra',
    'RADIO TROPICAL': 'Rádio Tropical',
    'RADIOTROPICAL': 'Rádio Tropical',
    'RADIO ÔMEGA': 'Rádio Ômega',
    'RADIOÔMEGA': 'Rádio Ômega',
    
    # Continuação
    'RD ESP': 'RDESP',
    'RDESP': 'RDESP',
    'REDE SOCIAL': 'Rede Social',
    'REDESOCIAL': 'Rede Social',
    'RX DE FORA': 'Receita de Fora',
    'SANTA TEREZINHA ASSOCIAÇÃO': 'Santa Terezinha Associação',
    'SAÚDE DOS OLHOS': 'Saúde dos Olhos',
    'SEGUROS UNIMED': 'Seguros Unimed',
    'SIND CORREIOS': 'Sindicato - Correios',
    'SIND SINDSERVITA': 'Sindicato - Sindservita',
    'SIND SINETROSV': 'Sind. Sinetro SV',
    'SINDSINETROSV': 'Sind. Sinetro SV',
    'SIND SINTRAMMSP': 'Sindicato - Sintramm SP',
    'SITAP - LINEX': 'Sitap - Linex',
    'SITE': 'Site',
    'SUBPREFEITURA': 'Subprefeitura',
    'SUPERMERCADO SÃO JOSE': 'Supermercado São José',
    'SUS': 'SUS',
    'TELEMARKETING': 'Telemarketing',
    'TERMINAL SANTANA': 'Terminal Santana',
    'TERMINALSANTANA': 'Terminal Santana',
    'TESTE': 'Teste',
    'TRANSPPASS': 'Transppass',
    'ULTRASOM': 'Ultrasom',
    'VALE SAUDE JEQUITI': 'Vale Saúde Jequiti',
    'VALESAUDEJEQUITI': 'Vale Saúde Jequiti',
    'VISIOTESTE': 'Visio Teste',
    'VITRINE': 'Vitrine',
    'WHATSAPP': 'WhatsApp',
    'WHATSAPPROBÔ': 'WhatsApp Robô',
}

def normalizar_valor(valor):
    """Normaliza um valor individual"""
    if pd.isna(valor):
        return valor
    
    valor_original = str(valor).strip()
    
    # Aplica normalização se existir no mapeamento
    if valor_original in NORMALIZACOES:
        return NORMALIZACOES[valor_original]
    
    # Se não estiver no mapeamento, retorna o valor original
    return valor_original

def main():
    print("="*80)
    print("NORMALIZAÇÃO - Canais de Aquisição (nome)")
    print("="*80)
    print()
    
    # Ler arquivo
    print(f"Lendo arquivo: {INPUT_FILE.name}")
    df = pd.read_csv(INPUT_FILE)
    print(f"  Total de registros: {len(df):,}")
    print()
    
    # Estatísticas antes
    print("ANTES da normalização:")
    print(f"  Valores únicos: {df['nome'].nunique()}")
    print()
    
    # Backup da coluna original
    df['nome_original'] = df['nome'].copy()
    
    # Aplicar normalização
    print("Aplicando normalizações...")
    df['nome'] = df['nome'].apply(normalizar_valor)
    df['descricao'] = df['descricao'].apply(normalizar_valor)  # Normaliza também a descrição
    print("  ✓ Concluído")
    print()
    
    # Estatísticas depois
    print("DEPOIS da normalização:")
    print(f"  Valores únicos: {df['nome'].nunique()}")
    print()
    
    # Mostrar mudanças
    mudancas = df[df['nome'] != df['nome_original']][['codigo', 'nome_original', 'nome']]
    if len(mudancas) > 0:
        print(f"Total de mudanças: {len(mudancas)}")
        print("\nPrimeiras 20 mudanças:")
        print("-"*80)
        for _, row in mudancas.head(20).iterrows():
            print(f"[{row['codigo']}] {row['nome_original']}")
            print(f"     → {row['nome']}")
    else:
        print("Nenhuma mudança necessária (todos os valores já estavam normalizados)")
    print()
    
    # Remover coluna backup
    df = df.drop(columns=['nome_original'])
    
    # Salvar arquivo (sobrescrever)
    print(f"Salvando alterações no arquivo original...")
    df.to_csv(INPUT_FILE, index=False)
    print("  ✓ Arquivo atualizado com sucesso")
    print()
    
    print("="*80)
    print("NORMALIZAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*80)
    print()

if __name__ == '__main__':
    main()
