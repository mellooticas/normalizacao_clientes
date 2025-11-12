"""
Script de Importação de Vendas para o Banco de Dados
Importa dados do arquivo vendas_oss.csv para a tabela vendas.vendas
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime
import os

# =====================================================
# CONFIGURAÇÕES
# =====================================================

# Configurações do banco (ajuste conforme necessário)
DB_CONFIG = {
    'host': 'localhost',  # ou seu host Supabase
    'port': 5432,
    'database': 'postgres',
    'user': 'postgres',
    'password': 'sua_senha_aqui'
}

# Arquivo de entrada
ARQUIVO_CSV = 'd:/projetos/carne_facil/carne_facil/1_normalizacao/dados_processados/vendas_para_importar/vendas_oss.csv'

# Tamanho do batch para inserção
BATCH_SIZE = 500

# =====================================================
# FUNÇÕES
# =====================================================

def conectar_banco():
    """Conecta ao banco de dados"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✓ Conexão estabelecida com sucesso!")
        return conn
    except Exception as e:
        print(f"✗ Erro ao conectar: {e}")
        raise

def carregar_csv():
    """Carrega o arquivo CSV"""
    print(f"\nCarregando arquivo: {ARQUIVO_CSV}")
    
    if not os.path.exists(ARQUIVO_CSV):
        raise FileNotFoundError(f"Arquivo não encontrado: {ARQUIVO_CSV}")
    
    df = pd.read_csv(ARQUIVO_CSV, sep=';', encoding='utf-8')
    print(f"✓ Arquivo carregado: {len(df)} registros")
    
    return df

def validar_dados(df):
    """Valida os dados antes da importação"""
    print("\n" + "="*60)
    print("VALIDAÇÕES PRÉ-IMPORTAÇÃO")
    print("="*60)
    
    # Verificar colunas obrigatórias
    colunas_obrigatorias = ['numero_venda', 'loja_id', 'data_venda', 'valor_total']
    faltando = [col for col in colunas_obrigatorias if col not in df.columns]
    
    if faltando:
        print(f"✗ Colunas faltando: {faltando}")
        return False
    
    print(f"✓ Todas as colunas obrigatórias presentes")
    
    # Verificar valores nulos em campos obrigatórios
    nulos = df[colunas_obrigatorias].isnull().sum()
    if nulos.any():
        print("\n⚠ Valores nulos encontrados:")
        print(nulos[nulos > 0])
    
    # Verificar valores negativos
    negativos_total = (df['valor_total'] < 0).sum()
    negativos_entrada = (df['valor_entrada'] < 0).sum()
    
    if negativos_total > 0:
        print(f"✗ {negativos_total} registros com valor_total negativo")
        return False
    
    if negativos_entrada > 0:
        print(f"✗ {negativos_entrada} registros com valor_entrada negativo")
        return False
    
    # Verificar entrada maior que total
    entrada_maior = (df['valor_entrada'] > df['valor_total']).sum()
    if entrada_maior > 0:
        print(f"⚠ {entrada_maior} registros com entrada maior que total")
    
    # Estatísticas
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   Total de vendas: {len(df)}")
    print(f"   Lojas únicas: {df['loja_id'].nunique()}")
    print(f"   Clientes com ID: {df['cliente_id'].notna().sum()}")
    print(f"   Clientes sem ID: {df['cliente_id'].isna().sum()}")
    print(f"   Período: {df['data_venda'].min()} a {df['data_venda'].max()}")
    print(f"   Valor total: R$ {df['valor_total'].sum():,.2f}")
    
    # Distribuição por tipo
    if 'tipo_operacao' in df.columns:
        print(f"\n📋 POR TIPO DE OPERAÇÃO:")
        print(df['tipo_operacao'].value_counts())
    
    return True

def preparar_dados(df):
    """Prepara os dados para inserção"""
    print("\n" + "="*60)
    print("PREPARANDO DADOS")
    print("="*60)
    
    # Preencher valores padrão
    df['valor_entrada'] = df['valor_entrada'].fillna(0)
    df['cancelado'] = df['cancelado'].fillna(False)
    df['version'] = df['version'].fillna(1)
    df['tipo_operacao'] = df['tipo_operacao'].fillna('VENDA')
    df['status'] = 'ATIVO'
    
    # Converter datas
    df['data_venda'] = pd.to_datetime(df['data_venda'])
    
    # Substituir NaN por None (NULL no SQL)
    df = df.where(pd.notna(df), None)
    
    print(f"✓ Dados preparados: {len(df)} registros prontos")
    
    return df

def importar_vendas(conn, df):
    """Importa as vendas para o banco"""
    print("\n" + "="*60)
    print("IMPORTANDO VENDAS")
    print("="*60)
    
    cursor = conn.cursor()
    
    # SQL de inserção
    insert_sql = """
        INSERT INTO vendas.vendas (
            numero_venda,
            cliente_id,
            loja_id,
            vendedor_id,
            data_venda,
            valor_total,
            valor_entrada,
            nome_cliente_temp,
            observacoes,
            status,
            cancelado,
            data_cancelamento,
            motivo_cancelamento,
            created_at,
            updated_at,
            created_by,
            updated_by,
            deleted_at,
            version,
            tipo_operacao
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::public.status_type,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (loja_id, numero_venda) DO NOTHING
    """
    
    # Preparar dados para inserção
    registros = []
    for _, row in df.iterrows():
        registro = (
            row['numero_venda'],
            row['cliente_id'],
            row['loja_id'],
            row['vendedor_id'],
            row['data_venda'],
            row['valor_total'],
            row['valor_entrada'],
            row['nome_cliente_temp'],
            row['observacoes'],
            'ATIVO',  # status
            row['cancelado'],
            row.get('data_cancelamento'),
            row.get('motivo_cancelamento'),
            row.get('created_at') or datetime.now(),
            row.get('updated_at') or datetime.now(),
            row.get('created_by'),
            row.get('updated_by'),
            row.get('deleted_at'),
            int(row['version']),
            row['tipo_operacao']
        )
        registros.append(registro)
    
    # Inserir em batches
    total = len(registros)
    importados = 0
    
    try:
        for i in range(0, total, BATCH_SIZE):
            batch = registros[i:i+BATCH_SIZE]
            execute_batch(cursor, insert_sql, batch)
            importados += len(batch)
            
            # Progresso
            percentual = (importados / total) * 100
            print(f"   Progresso: {importados}/{total} ({percentual:.1f}%)")
        
        conn.commit()
        print(f"\n✓ Importação concluída: {importados} registros inseridos")
        
    except Exception as e:
        conn.rollback()
        print(f"\n✗ Erro durante importação: {e}")
        raise
    
    finally:
        cursor.close()

def verificar_importacao(conn):
    """Verifica os dados importados"""
    print("\n" + "="*60)
    print("VERIFICAÇÃO PÓS-IMPORTAÇÃO")
    print("="*60)
    
    cursor = conn.cursor()
    
    # Total de vendas
    cursor.execute("SELECT COUNT(*) FROM vendas.vendas")
    total = cursor.fetchone()[0]
    print(f"\n✓ Total de vendas no banco: {total}")
    
    # Por loja
    cursor.execute("""
        SELECT 
            l.codigo,
            l.nome,
            COUNT(*) as qtd,
            SUM(v.valor_total) as total
        FROM vendas.vendas v
        JOIN core.lojas l ON v.loja_id = l.id
        GROUP BY l.codigo, l.nome
        ORDER BY l.codigo
    """)
    
    print(f"\n📊 VENDAS POR LOJA:")
    for row in cursor.fetchall():
        print(f"   Loja {row[0]} - {row[1]}: {row[2]} vendas | R$ {row[3]:,.2f}")
    
    # Por tipo de operação
    cursor.execute("""
        SELECT 
            tipo_operacao,
            COUNT(*) as qtd,
            SUM(valor_total) as total
        FROM vendas.vendas
        GROUP BY tipo_operacao
        ORDER BY tipo_operacao
    """)
    
    print(f"\n📋 POR TIPO DE OPERAÇÃO:")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]} vendas | R$ {row[2]:,.2f}")
    
    cursor.close()

# =====================================================
# EXECUÇÃO PRINCIPAL
# =====================================================

def main():
    """Função principal"""
    print("="*60)
    print("IMPORTAÇÃO DE VENDAS - BANCO DE DADOS")
    print("="*60)
    
    try:
        # 1. Carregar CSV
        df = carregar_csv()
        
        # 2. Validar dados
        if not validar_dados(df):
            print("\n✗ Validação falhou. Corrija os erros e tente novamente.")
            return
        
        # 3. Preparar dados
        df = preparar_dados(df)
        
        # 4. Conectar ao banco
        conn = conectar_banco()
        
        # 5. Confirmar importação
        print("\n" + "="*60)
        resposta = input("Deseja prosseguir com a importação? (s/n): ")
        if resposta.lower() != 's':
            print("Importação cancelada pelo usuário.")
            conn.close()
            return
        
        # 6. Importar
        importar_vendas(conn, df)
        
        # 7. Verificar
        verificar_importacao(conn)
        
        # 8. Fechar conexão
        conn.close()
        
        print("\n" + "="*60)
        print("✓ PROCESSO CONCLUÍDO COM SUCESSO!")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ ERRO: {e}")
        raise

if __name__ == "__main__":
    main()
