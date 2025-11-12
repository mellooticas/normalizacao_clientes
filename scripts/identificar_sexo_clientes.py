"""
Identifica o sexo dos clientes baseado no primeiro nome
usando lista de nomes brasileiros comuns
"""

import pandas as pd
from pathlib import Path

# Caminhos
BASE_DIR = Path(__file__).parent.parent
CLIENTES_PATH = BASE_DIR / 'dados_processados' / 'originais' / 'clientes' / 'normalizados' / 'CLIENTES_OUTRAS_LOJAS.csv'

print("=" * 80)
print("IDENTIFICANDO SEXO DOS CLIENTES BASEADO NO PRIMEIRO NOME")
print("=" * 80)

# Listas de nomes comuns (primeiros nomes) - EXPANDIDA
NOMES_MASCULINOS = {
    'JOSE', 'JOAO', 'ANTONIO', 'FRANCISCO', 'CARLOS', 'PAULO', 'PEDRO', 'LUCAS', 
    'LUIZ', 'MARCOS', 'LUIS', 'GABRIEL', 'RAFAEL', 'DANIEL', 'MARCELO', 'BRUNO',
    'RODRIGO', 'FELIPE', 'GUSTAVO', 'EDUARDO', 'ANDRE', 'FERNANDO', 'FABIO',
    'RICARDO', 'LEONARDO', 'THIAGO', 'DIEGO', 'MATEUS', 'GUILHERME', 'HENRIQUE',
    'SERGIO', 'ROBERTO', 'ALESSANDRO', 'ALEXANDRE', 'MAURICIO', 'JULIO', 'CESAR',
    'ANDERSON', 'WELLINGTON', 'MICHEL', 'VINICIUS', 'IGOR', 'RENAN', 'CAIO',
    'HELIO', 'UELINTON', 'JOILDO', 'ROGERIO', 'GILMAR', 'FRANCISCO', 'ADEMIR',
    'GERALDO', 'VALDIR', 'WILSON', 'OSMAR', 'NELSON', 'MILTON', 'SEBASTIAO',
    'APARECIDO', 'BENEDITO', 'DOMINGOS', 'ARNALDO', 'WALDEMAR', 'JONAS', 'ELIAS',
    'SAMUEL', 'DAVI', 'BENJAMIN', 'ISAAC', 'MOISES', 'ABRAAO', 'NOE', 'EZEQUIEL',
    # NOVOS NOMES ADICIONADOS
    'JOEL', 'MANOEL', 'MANUEL', 'ANTHONY', 'WADERLEY', 'WANDERLEY', 'NAILSON',
    'ALABI', 'EDSON', 'EDER', 'ELDER', 'ELVIS', 'ELTON', 'EMERSON', 'ERIC',
    'EVERTON', 'FLAVIO', 'GERSON', 'HECTOR', 'IVAN', 'JAIR', 'JEAN', 'JEFFERSON',
    'JEFERSON', 'JONATHAN', 'JORGE', 'JUNIOR', 'LEANDRO', 'LUAN', 'LUCIANO',
    'MAICON', 'MARCIO', 'MARIO', 'MAURO', 'MICHAEL', 'MIGUEL', 'MURILO',
    'NILTON', 'ORLANDO', 'OSCAR', 'OTAVIO', 'PATRICK', 'RAUL', 'REINALDO',
    'RENATO', 'ROBSON', 'RUBENS', 'SANDRO', 'TIAGO', 'VICTOR', 'VITOR',
    'WAGNER', 'WALTER', 'WASHINGTON', 'WESLEY', 'WILLIAM', 'YURI', 'CLAUDIO',
    'CLEBER', 'CRISTIANO', 'DAVIDSON', 'DENIS', 'DJALMA', 'EDMAR', 'EDUARDO',
    'EUGENIO', 'EVERALDO', 'EZEQUIAS', 'FABRICIO', 'FAUSTO', 'FRED', 'GEOVANE',
    'GILVANE', 'HUMBERTO', 'INACIO', 'IVAL', 'JEFREY', 'JOAO', 'JOAQUIM'
}

NOMES_FEMININOS = {
    'MARIA', 'ANA', 'FRANCISCA', 'ANTONIA', 'ADRIANA', 'JULIANA', 'MARCIA',
    'FERNANDA', 'PATRICIA', 'ALINE', 'JULIANE', 'CAMILA', 'AMANDA', 'LETICIA',
    'RAQUEL', 'VANESSA', 'BEATRIZ', 'LARISSA', 'GABRIELA', 'BRUNA', 'CARLA',
    'PAULA', 'LUCIANA', 'DANIELA', 'RENATA', 'SIMONE', 'CLAUDIA', 'SANDRA',
    'ROSANGELA', 'VERA', 'SUELI', 'FABIANA', 'MONICA', 'ANDREA', 'SILVIA',
    'CRISTINA', 'TATIANA', 'ELAINE', 'KELLY', 'MICHELE', 'BARBARA', 'ANDREIA',
    'ALESSANDRA', 'JOANA', 'ROSE', 'ROSA', 'SOLANGE', 'MARIANA', 'ISABELA',
    'CAROLINA', 'VIVIANE', 'PRISCILA', 'JANAINA', 'CAROLINE', 'NATALIA',
    'APARECIDA', 'CONCEICAO', 'FATIMA', 'TEREZA', 'HELENA', 'ALICE', 'CLARA',
    'SOFIA', 'VALENTINA', 'LAURA', 'MANUELA', 'LUIZA', 'MARIA', 'JANE',
    'VITORIA', 'JENIFFER', 'NIVEA', 'GLORIA', 'VALERIA', 'NEUSA', 'ELZA',
    # NOVOS NOMES ADICIONADOS
    'ESTER', 'ESTHER', 'EMILY', 'EMILLY', 'GISELE', 'GISELLE', 'EUNICE', 'ELIZABETH',
    'ELISABETE', 'ELISA', 'ELIANE', 'ELIS', 'ELLEN', 'YUDY', 'YUDI', 'CREMILDES',
    'DEBORA', 'DENISE', 'DIANE', 'DIANA', 'DILMA', 'EDILENE', 'EDNA', 'ELIANA',
    'ERICA', 'ERIKA', 'EVELYNE', 'EVELYN', 'FRANCIELE', 'GENI', 'GEOVANA',
    'GERTRUDES', 'GIOVANA', 'GRAZIELA', 'HELLEN', 'IARA', 'INES', 'INGRID',
    'IRACEMA', 'IRANI', 'IRIS', 'IRMA', 'IVONE', 'JAQUELINE', 'JESSICA',
    'JOSEFA', 'JOICE', 'JOYCE', 'JULIA', 'JURACY', 'KATIA', 'KARINA', 'KEILA',
    'LAIS', 'LARA', 'LEILA', 'LEIA', 'LIDIA', 'LIGIA', 'LILIAN', 'LILIANE',
    'LINDA', 'LORENA', 'LOURDES', 'LUCIA', 'LUCI', 'MADALENA', 'MAGDA',
    'MARGARETE', 'MARGARIDA', 'MARILENE', 'MARINA', 'MARISA', 'MARTA',
    'MAYARA', 'MAYRA', 'MEIRE', 'MELISSA', 'MERCIA', 'MIRIAM', 'MIRIAM',
    'NADIA', 'NAIR', 'NEIDE', 'NICOLE', 'NOEMIA', 'ODETE', 'OLGA', 'OLIVIA',
    'PAMELA', 'PAOLA', 'PRATRICIA', 'REBECA', 'REGINA', 'RITA', 'ROBERTA',
    'ROSANA', 'ROSANE', 'ROSELI', 'ROSILENE', 'ROSIMAR', 'ROSIMEIRE', 'RUTH',
    'SABRINA', 'SAMARA', 'SARA', 'SARAH', 'SHEILA', 'SHIRLEY', 'SONIA',
    'SORAIA', 'SUZANA', 'SUZANE', 'SUZY', 'TALITA', 'TAMIRES', 'TANIA',
    'THAISA', 'THAIS', 'VALDIRENE', 'VALQUIRIA', 'VANIA', 'VERONICA',
    'VILMA', 'VIRGINIA', 'VITORIA', 'WANDA', 'YASMIN', 'YARA', 'ZELIA'
}

# Sufixos que geralmente indicam feminino
SUFIXOS_FEMININOS = ['A', 'E', 'I']

# 1. Ler arquivo
print(f"\n1. Lendo arquivo: {CLIENTES_PATH.name}")
df = pd.read_csv(CLIENTES_PATH, sep=';', dtype=str, encoding='utf-8')
print(f"   ✓ {len(df):,} clientes")

# 2. Função para identificar sexo
def identificar_sexo(nome):
    """Identifica sexo baseado no primeiro nome"""
    if pd.isna(nome) or str(nome).strip() == '':
        return None
    
    # Pegar primeiro nome e normalizar
    nome_completo = str(nome).strip().upper()
    primeiro_nome = nome_completo.split()[0] if ' ' in nome_completo else nome_completo
    
    # Remover acentos comuns
    primeiro_nome = (primeiro_nome
                     .replace('Á', 'A').replace('À', 'A').replace('Ã', 'A').replace('Â', 'A')
                     .replace('É', 'E').replace('È', 'E').replace('Ê', 'E')
                     .replace('Í', 'I').replace('Ì', 'I').replace('Î', 'I')
                     .replace('Ó', 'O').replace('Ò', 'O').replace('Õ', 'O').replace('Ô', 'O')
                     .replace('Ú', 'U').replace('Ù', 'U').replace('Û', 'U')
                     .replace('Ç', 'C'))
    
    # Verificar nas listas
    if primeiro_nome in NOMES_MASCULINOS:
        return 'M'
    
    if primeiro_nome in NOMES_FEMININOS:
        return 'F'
    
    # Se não encontrou, usar heurística por sufixo (menos confiável)
    if len(primeiro_nome) > 2:
        ultima_letra = primeiro_nome[-1]
        if ultima_letra == 'A' and primeiro_nome not in ['GARCIA', 'COSTA', 'SILVA']:
            return 'F'
        elif ultima_letra == 'O' and primeiro_nome not in ['AMARO']:
            return 'M'
    
    # Não conseguiu identificar
    return None

# 3. Aplicar identificação
print(f"\n2. Identificando sexo baseado nos nomes...")
df['sexo'] = df['nome'].apply(identificar_sexo)

# 4. Estatísticas
print(f"\n3. Estatísticas:")
sexo_counts = df['sexo'].value_counts()
total_identificados = df['sexo'].notna().sum()
total_nao_identificados = df['sexo'].isna().sum()

print(f"   ✓ Total de clientes: {len(df):,}")
print(f"   ✓ Identificados: {total_identificados:,} ({total_identificados/len(df)*100:.1f}%)")
print(f"   ✓ Não identificados: {total_nao_identificados:,} ({total_nao_identificados/len(df)*100:.1f}%)")

if len(sexo_counts) > 0:
    print(f"\n   Distribuição:")
    for sexo, count in sexo_counts.items():
        print(f"     - {sexo}: {count:,} ({count/len(df)*100:.1f}%)")

# 5. Mostrar exemplos não identificados
print(f"\n4. Primeiros 15 nomes NÃO identificados:")
nao_identificados = df[df['sexo'].isna()]['nome'].head(15)
if len(nao_identificados) > 0:
    for idx, nome in enumerate(nao_identificados, 1):
        primeiro_nome = str(nome).split()[0] if ' ' in str(nome) else str(nome)
        print(f"   {idx:>2}. {primeiro_nome:<20} (Nome completo: {nome})")
else:
    print("   ✓ Todos os nomes foram identificados!")

# 6. Mostrar amostras identificadas
print(f"\n5. Amostra de identificações:")
print(f"\n   MASCULINO (5 exemplos):")
masculinos = df[df['sexo'] == 'M'].head(5)
for _, row in masculinos.iterrows():
    print(f"     - {row['nome']}")

print(f"\n   FEMININO (5 exemplos):")
femininos = df[df['sexo'] == 'F'].head(5)
for _, row in femininos.iterrows():
    print(f"     - {row['nome']}")

# 7. Salvar arquivo atualizado
print(f"\n6. Salvando arquivo atualizado...")
df.to_csv(CLIENTES_PATH, sep=';', index=False, encoding='utf-8')
print(f"   ✓ Arquivo salvo: {CLIENTES_PATH.name}")
print(f"   ✓ {len(df):,} clientes")
print(f"   ✓ Coluna 'sexo' atualizada")

print("\n" + "=" * 80)
print("✅ IDENTIFICAÇÃO DE SEXO CONCLUÍDA!")
print("=" * 80)
print(f"\nResumo:")
print(f"  - Total: {len(df):,} clientes")
print(f"  - Masculino (M): {(df['sexo'] == 'M').sum():,}")
print(f"  - Feminino (F): {(df['sexo'] == 'F').sum():,}")
print(f"  - Não identificado (NULL): {df['sexo'].isna().sum():,}")
print(f"  - Taxa de sucesso: {total_identificados/len(df)*100:.1f}%")
print("=" * 80)
