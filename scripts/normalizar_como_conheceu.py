"""
Script para normalizar a coluna 'Como nos conheceu' do arquivo clientes_vixen_completo.csv

Ações:
1. Remove espaços extras no início e fim (strip)
2. Normaliza valores compostos para formato legível
3. Padroniza nomenclaturas
4. Gera relatório de mudanças
"""

import pandas as pd
from pathlib import Path
import re
from datetime import datetime

# Caminhos
BASE_DIR = Path(__file__).parent.parent
INPUT_FILE = BASE_DIR / 'dados_processados' / 'originais' / 'vixen' / 'extraidos_corrigidos' / 'clientes_vixen_completo.csv'
RELATORIO_FILE = BASE_DIR / 'relatorios' / f'normalizacao_como_conheceu_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

# Mapeamento de normalizações
NORMALIZACOES = {
    # Campanhas
    'CAMPANHAAILTON': 'Campanha - Ailton',
    'CAMPANHAANIVERSARIANTES': 'Campanha - Aniversariantes',
    'CAMPANHACBA': 'Campanha - CBA',
    'CAMPANHACOMPRE1LEVE3': 'Campanha - Compre 1 Leve 3',
    'CAMPANHAVADO': 'Campanha - Vado',
    
    # Clínicas e Médicos
    'ARKIMEDESCENTROMÉDICO': 'Arkimedes Centro Médico',
    'CLINICAALPHAVISION': 'Clínica Alpha Vision',
    'DRAMANDAAVVDECASTRO': 'Dra. Amanda A. V. V. de Castro',
    'DRRAFAELPIVATTO': 'Dr. Rafael Pivatto',
    'INSTITUTOSUELABUJAMRA': 'Instituto Suela Bujamra',
    
    # Divulgadores
    'DVDOUGLASJESUSDASILVA': 'Divulgador - Douglas Jesus da Silva',
    'DVGABRIELASILVA': 'Divulgador - Gabriela Silva',
    'DVJACIANEDINIZ': 'Divulgador - Jaciane Diniz',
    'DVJEANLEANDRO': 'Divulgador - Jean Leandro',
    'DVJOÃOPAULO': 'Divulgador - João Paulo',
    'DVNIKE': 'Divulgador - Nike',
    'DVSUELENRODRIGUES': 'Divulgador - Suelen Rodrigues',
    'DVVICTORHUGO': 'Divulgador - Victor Hugo',
    
    # Rádios
    'RADIO ATALAIA': 'Rádio Atalaia',
    'RADIOADOREFM': 'Rádio Adore FM',
    'RADIOFÉ101.5': 'Rádio Fé 101.5',
    'RADIOREDEUNÇÃO96.5': 'Rádio Rede Unção 96.5',
    'RADIOTERRA': 'Rádio Terra',
    'RADIOTROPICAL': 'Rádio Tropical',
    'RADIOÔMEGA': 'Rádio Ômega',
    
    # Convênios e Planos
    'ABMED': 'ABMED',
    'ADEASP': 'ADEASP',
    'AMEPLAN': 'Ameplan',
    'BIOSAÚDE': 'Bio Saúde',
    'CONVENIOFAN': 'Convênio FAN',
    'GUIMA': 'Guima',
    'IAMSPE': 'IAMSPE',
    'RDESP': 'RDESP',
    'SINDSINETROSV': 'Sind. Sinetro SV',
    'VALESAUDEJEQUITI': 'Vale Saúde Jequiti',
    
    # Farmácias
    'DROGARIACAMPEA': 'Drogaria Campeã',
    'DROGARIASUPERMED': 'Drogaria Supermed',
    
    # Marketing Digital
    'GOOGLE/FACE/INSTA-PATROCÍNIO': 'Google/Facebook/Instagram (Patrocínio)',
    'REDESOCIAL': 'Rede Social',
    'SITE': 'Site',
    'WHATSAPP': 'WhatsApp',
    'WHATSAPPROBÔ': 'WhatsApp Robô',
    
    # Marketing Tradicional
    'LUISFIOFOLHETOS': 'Luis Fio - Folhetos',
    'PANFLETOS': 'Panfletos',
    'PLACADELOJA': 'Placa de Loja',
    'TELEMARKETING': 'Telemarketing',
    'VITRINE': 'Vitrine',
    
    # Outros
    '1ªCOMPRA': '1ª Compra',
    'ABORDAGEM': 'Abordagem',
    'AMIGOS': 'Amigos',
    'ASSEMBLEIADEDEUS': 'Assembleia de Deus',
    'BOLIVIANOS': 'Bolivianos',
    'CARTAODETODOS': 'Cartão de Todos',
    'CARTÃOCOMPLETO': 'Cartão Completo',
    'CARTÃOINDICAÇÃO': 'Cartão Indicação',
    'CESTABÁSICA': 'Cesta Básica',
    'CLINICA': 'Clínica',
    'DIVULGADOR': 'Divulgador',
    'FLORIPARK': 'Floripark',
    'INDICAÇÃO': 'Indicação',
    'JÁ É CLIENTE': 'Já é Cliente',
    'MAGAZINELUIZA': 'Magazine Luiza',
    'ORÇAMENTO': 'Orçamento',
    'OUTROS': 'Outros',
    'PASSAGEM': 'Passagem',
    'PROSPECÇÃOMABIO': 'Prospecção - Mabio',
    'RX DE FORA': 'Receita de Fora',
    'SAÚDE DOS OLHOS': 'Saúde dos Olhos',
    'SUS': 'SUS',
    'TERMINALSANTANA': 'Terminal Santana',
    'VISIOTESTE': 'Visio Teste',
}

def normalizar_valor(valor):
    """Normaliza um valor individual"""
    if pd.isna(valor):
        return valor
    
    # Remove espaços extras
    valor = str(valor).strip()
    
    # Aplica normalização se existir no mapeamento
    if valor in NORMALIZACOES:
        return NORMALIZACOES[valor]
    
    # Se não estiver no mapeamento, retorna o valor original
    return valor

def main():
    print("="*80)
    print("NORMALIZAÇÃO - Como nos conheceu")
    print("="*80)
    print()
    
    # Criar diretório de relatórios se não existir
    RELATORIO_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Ler arquivo
    print(f"Lendo arquivo: {INPUT_FILE.name}")
    df = pd.read_csv(INPUT_FILE, sep=';', encoding='utf-8')
    print(f"  Total de registros: {len(df):,}")
    print()
    
    col_name = 'Como nos conheceu'
    
    # Estatísticas antes
    print("ANTES da normalização:")
    print(f"  Registros com valor: {df[col_name].notna().sum():,}")
    print(f"  Valores únicos: {df[col_name].nunique()}")
    print()
    
    # Backup da coluna original
    df[f'{col_name}_original'] = df[col_name].copy()
    
    # Aplicar normalização
    print("Aplicando normalizações...")
    df[col_name] = df[col_name].apply(normalizar_valor)
    print("  ✓ Concluído")
    print()
    
    # Estatísticas depois
    print("DEPOIS da normalização:")
    print(f"  Registros com valor: {df[col_name].notna().sum():,}")
    print(f"  Valores únicos: {df[col_name].nunique()}")
    print()
    
    # Gerar relatório de mudanças
    print("Gerando relatório de mudanças...")
    mudancas = []
    for original, normalizado in NORMALIZACOES.items():
        qtd = (df[f'{col_name}_original'] == original).sum()
        if qtd > 0:
            mudancas.append({
                'Original': original,
                'Normalizado': normalizado,
                'Quantidade': qtd
            })
    
    df_mudancas = pd.DataFrame(mudancas).sort_values('Quantidade', ascending=False)
    
    # Salvar relatório
    with open(RELATORIO_FILE, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("RELATÓRIO DE NORMALIZAÇÃO - Como nos conheceu\n")
        f.write(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"Arquivo: {INPUT_FILE.name}\n")
        f.write(f"Total de registros: {len(df):,}\n")
        f.write(f"Registros afetados: {len(df_mudancas):,}\n\n")
        
        f.write("MUDANÇAS REALIZADAS:\n")
        f.write("-"*80 + "\n")
        for _, row in df_mudancas.iterrows():
            f.write(f"\n{row['Original']}\n")
            f.write(f"  → {row['Normalizado']}\n")
            f.write(f"  Registros afetados: {row['Quantidade']:,}\n")
        
        f.write("\n" + "="*80 + "\n")
        f.write("\nVALORES ÚNICOS APÓS NORMALIZAÇÃO:\n")
        f.write("-"*80 + "\n")
        for valor in sorted(df[col_name].dropna().unique()):
            qtd = (df[col_name] == valor).sum()
            f.write(f"  {valor}: {qtd:,} registros\n")
    
    print(f"  ✓ Relatório salvo em: {RELATORIO_FILE.name}")
    print()
    
    # Exibir preview das mudanças
    print("Preview das principais mudanças:")
    print(df_mudancas.head(10).to_string(index=False))
    print()
    
    # Remover coluna original antes de salvar
    df = df.drop(columns=[f'{col_name}_original'])
    
    # Salvar arquivo (sobrescrever o original)
    print(f"Salvando alterações no arquivo original: {INPUT_FILE.name}")
    df.to_csv(INPUT_FILE, sep=';', index=False, encoding='utf-8')
    print("  ✓ Arquivo atualizado com sucesso")
    print()
    
    print("="*80)
    print("NORMALIZAÇÃO CONCLUÍDA COM SUCESSO!")
    print("="*80)
    print()
    print(f"📄 Arquivo atualizado: {INPUT_FILE}")
    print(f"📊 Relatório: {RELATORIO_FILE}")
    print()

if __name__ == '__main__':
    main()
