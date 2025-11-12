#!/usr/bin/env python3
"""
EXTRATOR E ANALISADOR DE PAGAMENTOS DE CARNÊ
===========================================

Este script foca especificamente nos pagamentos de carnê para:
1. Filtrar com dupla validação (histórico + segmento)
2. Extrair informações de cliente e número da parcela
3. Preparar base para cruzamento com vendas
4. Analisar completude dos pagamentos
"""

import pandas as pd
import re
from pathlib import Path
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AnalisadorPagamentosCarne:
    def __init__(self):
        self.pasta_dados = Path("d:/projetos/carne_facil/carne_facil/data/processados/movimento_caixa")
        self.pasta_final = Path("d:/projetos/carne_facil/carne_facil/data/processados/movimento_caixa/pagamentos_carne")
        self.pasta_final.mkdir(exist_ok=True)
        self.df = None
        self.df_carne_filtrado = None
    
    def carregar_dados_consolidados(self):
        """Carrega o arquivo consolidado"""
        arquivos = list(self.pasta_dados.glob("movimento_caixa_consolidado_*.csv"))
        if not arquivos:
            logging.error("Nenhum arquivo consolidado encontrado!")
            return False
        
        arquivo_mais_recente = max(arquivos, key=lambda x: x.stat().st_mtime)
        logging.info(f"Carregando: {arquivo_mais_recente.name}")
        
        self.df = pd.read_csv(arquivo_mais_recente)
        self.df['Dh_movimento'] = pd.to_datetime(self.df['Dh_movimento'])
        
        logging.info(f"Dados carregados: {len(self.df)} registros")
        return True
    
    def aplicar_filtro_duplo_carne(self):
        """Aplica filtro duplo para pagamentos de carnê"""
        logging.info("=== APLICANDO FILTRO DUPLO PARA CARNÊ ===")
        
        # Filtro 1: Histórico contém "CARNE"
        filtro_historico = self.df['Histórico'].str.contains('CARNE', case=False, na=False)
        
        # Filtro 2: Segmento é "CARNE LANCASTER" 
        filtro_segmento = self.df['Segmento'].str.contains('CARNE LANCASTER', case=False, na=False)
        
        # Aplicar filtros separadamente para análise
        apenas_historico = self.df[filtro_historico]
        apenas_segmento = self.df[filtro_segmento]
        ambos_filtros = self.df[filtro_historico & filtro_segmento]
        
        print(f"\n🔍 ANÁLISE DOS FILTROS:")
        print(f"   • Apenas histórico com 'CARNE': {len(apenas_historico):,}")
        print(f"   • Apenas segmento 'CARNE LANCASTER': {len(apenas_segmento):,}")
        print(f"   • Ambos os filtros (interseção): {len(ambos_filtros):,}")
        print(f"   • Total original: {len(self.df):,}")
        
        # Verificar se há registros que passam em apenas um filtro
        so_historico = self.df[filtro_historico & ~filtro_segmento]
        so_segmento = self.df[~filtro_historico & filtro_segmento]
        
        print(f"\n⚠️ POSSÍVEIS INCONSISTÊNCIAS:")
        print(f"   • Só histórico (sem segmento): {len(so_historico):,}")
        print(f"   • Só segmento (sem histórico): {len(so_segmento):,}")
        
        if len(so_historico) > 0:
            print(f"\n🔍 EXEMPLOS SÓ HISTÓRICO:")
            for _, row in so_historico.head(3).iterrows():
                print(f"   • {row['Histórico'][:60]}... | Segmento: '{row['Segmento']}'")
        
        if len(so_segmento) > 0:
            print(f"\n🔍 EXEMPLOS SÓ SEGMENTO:")
            for _, row in so_segmento.head(3).iterrows():
                print(f"   • {row['Histórico'][:60]}... | Segmento: '{row['Segmento']}'")
        
        # Usar união dos filtros para capturar tudo relacionado a carnê
        filtro_final = filtro_historico | filtro_segmento
        self.df_carne_filtrado = self.df[filtro_final].copy()
        
        logging.info(f"Filtro final aplicado: {len(self.df_carne_filtrado)} registros de carnê")
        
        return {
            'apenas_historico': len(apenas_historico),
            'apenas_segmento': len(apenas_segmento),
            'ambos_filtros': len(ambos_filtros),
            'filtro_final': len(self.df_carne_filtrado)
        }
    
    def extrair_informacoes_parcela(self):
        """Extrai informações detalhadas das parcelas"""
        logging.info("Extraindo informações das parcelas...")
        
        def extrair_numero_parcela(historico):
            """Extrai número da parcela do histórico"""
            if pd.isna(historico):
                return None, None
            
            historico = str(historico).upper()
            
            # Padrões possíveis:
            # "PARCELA 02/05", "PARC 4/8", "PARC. 5/7", "PARC 1", "PARCELA 10"
            patterns = [
                r'PARC(?:ELA)?\s*\.?\s*(\d+)(?:/(\d+))?',  # PARCELA 02/05, PARC 4/8, PARC. 5/7
                r'(\d+)/(\d+)',  # Formato direto: 02/05
            ]
            
            for pattern in patterns:
                match = re.search(pattern, historico)
                if match:
                    parcela_atual = int(match.group(1))
                    total_parcelas = int(match.group(2)) if match.group(2) else None
                    return parcela_atual, total_parcelas
            
            return None, None
        
        def extrair_cliente_id(cliente_str, id_str):
            """Extrai informações do cliente"""
            if pd.notna(id_str) and id_str != 1:
                return int(id_str)
            return None
        
        # Aplicar extrações
        parcela_info = self.df_carne_filtrado['Histórico'].apply(
            lambda x: extrair_numero_parcela(x)
        )
        
        self.df_carne_filtrado['parcela_numero'] = [info[0] for info in parcela_info]
        self.df_carne_filtrado['total_parcelas'] = [info[1] for info in parcela_info]
        
        # Cliente ID (usar coluna ID quando diferente de 1)
        self.df_carne_filtrado['cliente_id_extraido'] = self.df_carne_filtrado.apply(
            lambda row: extrair_cliente_id(row['Fornecedor/cliente'], row['ID']), 
            axis=1
        )
        
        # Cliente nome
        self.df_carne_filtrado['cliente_nome'] = self.df_carne_filtrado['Fornecedor/cliente'].apply(
            lambda x: x if x != 'CONSUMIDOR' else None
        )
        
        # Estatísticas das extrações
        print(f"\n📊 INFORMAÇÕES EXTRAÍDAS:")
        print(f"   • Com número de parcela: {self.df_carne_filtrado['parcela_numero'].notna().sum():,}")
        print(f"   • Com total de parcelas: {self.df_carne_filtrado['total_parcelas'].notna().sum():,}")
        print(f"   • Com cliente ID: {self.df_carne_filtrado['cliente_id_extraido'].notna().sum():,}")
        print(f"   • Com nome cliente: {self.df_carne_filtrado['cliente_nome'].notna().sum():,}")
        
        # Exemplos de parcelas extraídas
        com_parcela = self.df_carne_filtrado[self.df_carne_filtrado['parcela_numero'].notna()]
        if len(com_parcela) > 0:
            print(f"\n🔍 EXEMPLOS DE PARCELAS EXTRAÍDAS:")
            for _, row in com_parcela.head(5).iterrows():
                print(f"   • Parcela {row['parcela_numero']}/{row['total_parcelas']} - R$ {row['Vl_líquido']:.2f} - {row['cliente_nome'] or 'CONSUMIDOR'}")
    
    def analisar_distribuicao_pagamentos(self):
        """Analisa a distribuição dos pagamentos"""
        logging.info("=== ANÁLISE DE DISTRIBUIÇÃO DOS PAGAMENTOS ===")
        
        # Distribuição por número de parcela
        if self.df_carne_filtrado['parcela_numero'].notna().any():
            dist_parcelas = self.df_carne_filtrado['parcela_numero'].value_counts().sort_index()
            print(f"\n📊 DISTRIBUIÇÃO POR NÚMERO DE PARCELA:")
            for parcela, quantidade in dist_parcelas.head(10).items():
                valor_total = self.df_carne_filtrado[
                    self.df_carne_filtrado['parcela_numero'] == parcela
                ]['Vl_líquido'].sum()
                print(f"   • Parcela {parcela}: {quantidade:,} pagamentos - R$ {valor_total:,.2f}")
        
        # Distribuição por total de parcelas (planos)
        if self.df_carne_filtrado['total_parcelas'].notna().any():
            dist_planos = self.df_carne_filtrado['total_parcelas'].value_counts().sort_index()
            print(f"\n📊 DISTRIBUIÇÃO POR PLANO (total parcelas):")
            for plano, quantidade in dist_planos.items():
                valor_total = self.df_carne_filtrado[
                    self.df_carne_filtrado['total_parcelas'] == plano
                ]['Vl_líquido'].sum()
                print(f"   • Plano {plano}x: {quantidade:,} pagamentos - R$ {valor_total:,.2f}")
        
        # Análise por período
        pagamentos_por_mes = self.df_carne_filtrado.groupby([
            self.df_carne_filtrado['Dh_movimento'].dt.year,
            self.df_carne_filtrado['Dh_movimento'].dt.month
        ]).agg({
            'Vl_líquido': ['count', 'sum'],
            'cliente_id_extraido': 'nunique'
        }).round(2)
        
        print(f"\n📅 PAGAMENTOS POR MÊS (últimos 12):")
        print(pagamentos_por_mes.tail(12))
        
        # Valores estatísticos
        valores_stats = self.df_carne_filtrado['Vl_líquido'].describe()
        print(f"\n💰 ESTATÍSTICAS DOS VALORES:")
        print(f"   • Total pago: R$ {self.df_carne_filtrado['Vl_líquido'].sum():,.2f}")
        print(f"   • Valor médio: R$ {valores_stats['mean']:.2f}")
        print(f"   • Valor mediano: R$ {valores_stats['50%']:.2f}")
        print(f"   • Menor pagamento: R$ {valores_stats['min']:.2f}")
        print(f"   • Maior pagamento: R$ {valores_stats['max']:.2f}")
    
    def identificar_clientes_ativos(self):
        """Identifica clientes com pagamentos e prepara para cruzamento"""
        logging.info("Identificando clientes ativos...")
        
        # Resumo por cliente
        clientes_resumo = self.df_carne_filtrado.groupby(['cliente_id_extraido', 'cliente_nome']).agg({
            'Vl_líquido': ['count', 'sum', 'min', 'max'],
            'Dh_movimento': ['min', 'max'],
            'parcela_numero': ['min', 'max'],
            'total_parcelas': ['first', 'nunique']
        }).round(2)
        
        # Filtrar apenas clientes com ID válido
        clientes_validos = clientes_resumo[clientes_resumo.index.get_level_values(0).notna()]
        
        print(f"\n👥 RESUMO DE CLIENTES:")
        print(f"   • Total clientes únicos: {len(clientes_validos):,}")
        print(f"   • Cliente com mais pagamentos: {clientes_validos[('Vl_líquido', 'count')].max()}")
        print(f"   • Cliente com maior valor: R$ {clientes_validos[('Vl_líquido', 'sum')].max():,.2f}")
        
        # Top 10 clientes por valor
        top_clientes = clientes_validos.sort_values(('Vl_líquido', 'sum'), ascending=False)
        print(f"\n🏆 TOP 10 CLIENTES POR VALOR PAGO:")
        for i, (cliente_info, dados) in enumerate(top_clientes.head(10).iterrows(), 1):
            cliente_id, cliente_nome = cliente_info
            valor_total = dados[('Vl_líquido', 'sum')]
            num_pagamentos = dados[('Vl_líquido', 'count')]
            print(f"   {i:2d}. ID {cliente_id} - {cliente_nome or 'NOME NÃO INFORMADO'}")
            print(f"       R$ {valor_total:,.2f} ({num_pagamentos} pagamentos)")
        
        return clientes_validos
    
    def gerar_arquivo_pagamentos_carne(self):
        """Gera arquivo final com pagamentos de carnê normalizados"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Criar estrutura final
        df_final = pd.DataFrame()
        
        # IDs e identificadores
        df_final['id_movimento'] = self.df_carne_filtrado['ID_fin_']
        df_final['numero_documento'] = self.df_carne_filtrado['Nro_doc_']
        
        # Data e hora
        df_final['data_pagamento'] = self.df_carne_filtrado['Dh_movimento'].dt.date
        df_final['hora_pagamento'] = self.df_carne_filtrado['Dh_movimento'].dt.time
        df_final['timestamp_pagamento'] = self.df_carne_filtrado['Dh_movimento']
        
        # Informações do cliente
        df_final['cliente_id'] = self.df_carne_filtrado['cliente_id_extraido']
        df_final['cliente_nome'] = self.df_carne_filtrado['cliente_nome']
        
        # Informações da parcela
        df_final['parcela_numero'] = self.df_carne_filtrado['parcela_numero']
        df_final['total_parcelas'] = self.df_carne_filtrado['total_parcelas']
        df_final['valor_pago'] = self.df_carne_filtrado['Vl_líquido']
        
        # Informações operacionais
        df_final['loja_codigo'] = self.df_carne_filtrado['ID_emp_']
        df_final['caixa_codigo'] = self.df_carne_filtrado['ID_caixa']
        df_final['historico_completo'] = self.df_carne_filtrado['Histórico']
        df_final['segmento'] = self.df_carne_filtrado['Segmento']
        
        # Metadados
        df_final['arquivo_origem'] = self.df_carne_filtrado['arquivo_origem']
        df_final['periodo_origem'] = self.df_carne_filtrado['periodo_origem']
        
        # Flags para análise
        df_final['tem_parcela_info'] = df_final['parcela_numero'].notna()
        df_final['tem_cliente_id'] = df_final['cliente_id'].notna()
        df_final['is_consumidor'] = df_final['cliente_nome'].isna()
        
        # Timestamps
        df_final['created_at'] = datetime.now()
        
        # Salvar arquivo
        arquivo_final = self.pasta_final / f"pagamentos_carne_extraidos_{timestamp}.csv"
        df_final.to_csv(arquivo_final, index=False, encoding='utf-8')
        
        logging.info(f"Arquivo de pagamentos de carnê salvo: {arquivo_final}")
        
        return arquivo_final, df_final
    
    def gerar_relatorio_final(self, df_final):
        """Gera relatório final da extração"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        relatorio = f"""
=== RELATÓRIO DE EXTRAÇÃO - PAGAMENTOS DE CARNÊ ===
Data/Hora: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

RESUMO EXECUTIVO:
- Total de registros originais: {len(self.df):,}
- Pagamentos de carnê identificados: {len(self.df_carne_filtrado):,}
- Taxa de captura: {(len(self.df_carne_filtrado) / len(self.df) * 100):.2f}%
- Valor total em pagamentos: R$ {df_final['valor_pago'].sum():,.2f}

QUALIDADE DOS DADOS:
- Com informação de parcela: {df_final['tem_parcela_info'].sum():,} ({(df_final['tem_parcela_info'].mean() * 100):.1f}%)
- Com cliente identificado: {df_final['tem_cliente_id'].sum():,} ({(df_final['tem_cliente_id'].mean() * 100):.1f}%)
- Pagamentos "CONSUMIDOR": {df_final['is_consumidor'].sum():,} ({(df_final['is_consumidor'].mean() * 100):.1f}%)

DISTRIBUIÇÃO TEMPORAL:
- Período: {df_final['data_pagamento'].min()} até {df_final['data_pagamento'].max()}
- Clientes únicos: {df_final['cliente_id'].nunique()}
- Dias com pagamentos: {df_final['data_pagamento'].nunique()}

PRÓXIMOS PASSOS SUGERIDOS:
1. Cruzar com tabela de vendas para identificar carnês em aberto
2. Calcular valor total de cada carnê vs pagamentos recebidos
3. Identificar clientes inadimplentes
4. Reconciliar entradas + pagamentos = valor total da venda

PREPARAÇÃO PARA CRUZAMENTO:
- Campo cliente_id: pronto para JOIN com vendas
- Campo parcela_numero: permite sequenciamento
- Campo valor_pago: permite soma por cliente
- Campo data_pagamento: permite análise temporal

=== FIM DO RELATÓRIO ===
        """
        
        arquivo_relatorio = self.pasta_final / f"relatorio_extracao_{timestamp}.txt"
        with open(arquivo_relatorio, 'w', encoding='utf-8') as f:
            f.write(relatorio)
        
        print(relatorio)
        logging.info(f"Relatório salvo: {arquivo_relatorio}")
    
    def executar_extracao_completa(self):
        """Executa todo o processo de extração"""
        logging.info("=== INICIANDO EXTRAÇÃO DE PAGAMENTOS DE CARNÊ ===")
        
        if not self.carregar_dados_consolidados():
            return False
        
        filtros_stats = self.aplicar_filtro_duplo_carne()
        self.extrair_informacoes_parcela()
        self.analisar_distribuicao_pagamentos()
        clientes = self.identificar_clientes_ativos()
        arquivo, df_final = self.gerar_arquivo_pagamentos_carne()
        self.gerar_relatorio_final(df_final)
        
        print(f"\n✅ EXTRAÇÃO CONCLUÍDA!")
        print(f"📁 Arquivo gerado: {arquivo.name}")
        print(f"📊 {len(df_final):,} pagamentos de carnê identificados")
        print(f"💰 R$ {df_final['valor_pago'].sum():,.2f} em valores")
        
        logging.info("=== EXTRAÇÃO DE PAGAMENTOS DE CARNÊ CONCLUÍDA ===")
        return True

def main():
    """Função principal"""
    extrator = AnalisadorPagamentosCarne()
    sucesso = extrator.executar_extracao_completa()
    
    if not sucesso:
        print("\n❌ Erro na extração!")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())