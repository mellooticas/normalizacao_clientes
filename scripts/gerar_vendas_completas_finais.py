#!/usr/bin/env python3
"""
Gera arquivo final de vendas completas para importação no banco
8.975 vendas prontas com valor de R$ 4.451.770,25
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

def gerar_vendas_completas_finais():
    """Gera arquivos finais de vendas completas"""
    
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    
    print("🔄 === GERANDO VENDAS COMPLETAS FINAIS === 🔄")
    
    # 1. Carrega arquivo completo
    arquivo_completo = base_dir / "data" / "originais" / "controles_gerais" / "trans_financ" / "separados_por_pagamento" / "ordem_servico_pdv_outros_pagamentos_com_uuid_normalizado.csv"
    
    vendas_completas = pd.read_csv(arquivo_completo)
    print(f"📊 Carregados: {len(vendas_completas)} registros")
    
    # 2. Agrupamento por venda
    vendas_agrupadas = vendas_completas.groupby('ID operação').agg({
        'Nro.operação': 'first',
        'ID emp.': 'first',
        'ID': 'first',  # Cliente ID
        'Cliente': 'first',
        'Dh.emissão': 'first',
        'Dh.transação': 'first',
        'Vl.movimento': 'sum',  # Soma todos os pagamentos
        'ID.5': 'first',  # Vendedor
        'Vendedor': 'first',
        'arquivo_origem': 'first',
        'mes_origem': 'first',
        'Nro.operacao_original': 'first'  # OS original
    }).reset_index()
    
    print(f"✅ Vendas agrupadas: {len(vendas_agrupadas)}")
    
    # 3. Padronização de lojas
    lojas_map = {
        42: {
            'loja_id': '52f92716-d2ba-441a-ac3c-94bdfabd9722',
            'nome': 'SUZANO'
        },
        48: {
            'loja_id': 'aa7a5646-f7d6-4239-831c-6602fbabb10a',
            'nome': 'MAUA'
        }
    }
    
    vendas_agrupadas['loja_id'] = vendas_agrupadas['ID emp.'].map(lambda x: lojas_map.get(x, {}).get('loja_id'))
    vendas_agrupadas['loja_nome'] = vendas_agrupadas['ID emp.'].map(lambda x: lojas_map.get(x, {}).get('nome'))
    
    # 4. Ligação com clientes UUID
    uuid_consolidado = pd.read_csv(base_dir / "data" / "clientes_uuid" / "todos_clientes_uuid_consolidado.csv")
    uuid_consolidado['id_legado_str'] = uuid_consolidado['id_legado'].astype(str).str.replace('.0', '')
    cliente_para_uuid = dict(zip(uuid_consolidado['id_legado_str'], uuid_consolidado['cliente_id']))
    
    vendas_agrupadas['cliente_id_str'] = vendas_agrupadas['ID'].astype(str)
    vendas_agrupadas['cliente_uuid'] = vendas_agrupadas['cliente_id_str'].map(cliente_para_uuid)
    
    # 5. Padronização de números de OS
    def padronizar_numero_os(numero_original):
        """Padroniza número da OS removendo prefixos de loja"""
        if pd.isna(numero_original):
            return None
        
        numero_str = str(numero_original)
        
        # Remove prefixos 42000 ou 48000
        if numero_str.startswith('420'):
            return numero_str[3:]  # Remove 420
        elif numero_str.startswith('480'):
            return numero_str[3:]  # Remove 480
        else:
            return numero_str
    
    vendas_agrupadas['numero_os_padronizado'] = vendas_agrupadas['Nro.operacao_original'].apply(padronizar_numero_os)
    
    # 6. Preparação campos para banco
    vendas_agrupadas['vendedor_id'] = '2fec96c8-d492-49ab-b38a-a5d5452af4d2'  # UUID que funcionou
    vendas_agrupadas['data_venda'] = pd.to_datetime(vendas_agrupadas['Dh.emissão']).dt.strftime('%Y-%m-%d')
    vendas_agrupadas['numero_venda'] = vendas_agrupadas['numero_os_padronizado']
    vendas_agrupadas['valor_total'] = vendas_agrupadas['Vl.movimento'].abs()
    vendas_agrupadas['valor_entrada'] = 0
    vendas_agrupadas['nome_cliente_temp'] = vendas_agrupadas['Cliente']
    vendas_agrupadas['observacoes'] = 'Importado VIXEN outros pagamentos - Dataset completo 14k linhas'
    vendas_agrupadas['status'] = 'ATIVO'
    vendas_agrupadas['cancelado'] = False
    vendas_agrupadas['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    vendas_agrupadas['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 7. Separação prontas vs pendentes
    vendas_prontas = vendas_agrupadas[vendas_agrupadas['cliente_uuid'].notna()].copy()
    vendas_pendentes = vendas_agrupadas[vendas_agrupadas['cliente_uuid'].isna()].copy()
    
    print(f"✅ Prontas: {len(vendas_prontas)}")
    print(f"⏳ Pendentes: {len(vendas_pendentes)}")
    
    # 8. Seleção de campos para banco
    campos_banco = [
        'cliente_uuid',
        'vendedor_id', 
        'loja_id',
        'data_venda',
        'numero_venda',
        'valor_total',
        'valor_entrada',
        'nome_cliente_temp',
        'observacoes',
        'status',
        'cancelado',
        'created_at',
        'updated_at'
    ]
    
    # 9. Renomeia campos
    vendas_finais_prontas = vendas_prontas[campos_banco].copy()
    vendas_finais_prontas.rename(columns={
        'cliente_uuid': 'cliente_id',
        'nome_cliente_temp': 'nome_cliente'
    }, inplace=True)
    
    # 10. Remove duplicatas por cliente + data + valor
    print(f"\n🔍 Verificando duplicatas...")
    antes_duplicatas = len(vendas_finais_prontas)
    
    vendas_finais_prontas = vendas_finais_prontas.drop_duplicates(
        subset=['cliente_id', 'data_venda', 'valor_total'],
        keep='first'
    )
    
    depois_duplicatas = len(vendas_finais_prontas)
    duplicatas_removidas = antes_duplicatas - depois_duplicatas
    
    print(f"🧹 Removidas {duplicatas_removidas} duplicatas")
    print(f"✅ Final limpo: {depois_duplicatas} vendas")
    
    # 11. Salva arquivos
    output_dir = base_dir / "data" / "vendas_para_importar"
    output_dir.mkdir(exist_ok=True)
    
    # Arquivo principal
    arquivo_prontas = output_dir / "vendas_COMPLETAS_PRONTO_PARA_IMPORTAR.csv"
    vendas_finais_prontas.to_csv(arquivo_prontas, index=False)
    print(f"💾 Salvo: {arquivo_prontas}")
    
    # Arquivo pendentes
    if len(vendas_pendentes) > 0:
        vendas_pendentes_campos = vendas_pendentes[['ID', 'Cliente', 'loja_nome', 'valor_total', 'data_venda']].copy()
        arquivo_pendentes = output_dir / "vendas_COMPLETAS_PENDENTES.csv"
        vendas_pendentes_campos.to_csv(arquivo_pendentes, index=False)
        print(f"⏳ Pendentes: {arquivo_pendentes}")
    
    # 12. Estatísticas finais
    print(f"\n📊 === ESTATÍSTICAS FINAIS ===")
    print(f"✅ Vendas prontas: {len(vendas_finais_prontas)}")
    print(f"💰 Valor total: R$ {vendas_finais_prontas['valor_total'].sum():,.2f}")
    print(f"📅 Período: {vendas_finais_prontas['data_venda'].min()} a {vendas_finais_prontas['data_venda'].max()}")
    
    # Por loja
    por_loja = vendas_finais_prontas.groupby('loja_id').agg({
        'valor_total': ['count', 'sum']
    }).round(2)
    
    print(f"\n🏪 Por loja:")
    print(f"   SUZANO: {len(vendas_finais_prontas[vendas_finais_prontas['loja_id'] == '52f92716-d2ba-441a-ac3c-94bdfabd9722'])} vendas")
    print(f"   MAUÁ: {len(vendas_finais_prontas[vendas_finais_prontas['loja_id'] == 'aa7a5646-f7d6-4239-831c-6602fbabb10a'])} vendas")
    
    print(f"\n🎯 ARQUIVO PRONTO PARA IMPORTAÇÃO!")
    print(f"📂 {arquivo_prontas}")
    
    return vendas_finais_prontas

if __name__ == "__main__":
    vendas_finais = gerar_vendas_completas_finais()
    print(f"\n🎉 PROCESSAMENTO CONCLUÍDO!")
    print(f"✅ {len(vendas_finais)} vendas prontas para importar")