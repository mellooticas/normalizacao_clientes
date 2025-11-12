#!/usr/bin/env python3
"""
Consolidador de Arquivos por Loja
=================================

Junta todos os arquivos base_clientes_OS de cada loja em um único arquivo consolidado.
Isso criará uma base sólida por loja para posterior normalização.
"""

import pandas as pd
import os
from pathlib import Path
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class ConsolidadorPorLoja:
    def __init__(self):
        self.base_dir = Path("data/originais/oss/base_clientes_os")
        self.output_dir = Path("data/originais/oss/consolidadas")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.consolidados = []
        self.erros = []
    
    def consolidar_loja(self, pasta_loja):
        """Consolida todos os arquivos CSV de uma loja em um único arquivo"""
        loja_nome = pasta_loja.name.upper()
        logger.info(f"🔄 Consolidando loja: {loja_nome}")
        
        # Buscar todos os arquivos CSV da loja
        arquivos_csv = list(pasta_loja.glob("*_base_clientes_OS.csv"))
        
        if not arquivos_csv:
            logger.warning(f"   ⚠️ Nenhum arquivo encontrado para {loja_nome}")
            return None
        
        logger.info(f"   📄 Encontrados {len(arquivos_csv)} arquivo(s)")
        
        dataframes = []
        total_linhas = 0
        
        for arquivo in arquivos_csv:
            try:
                logger.info(f"   📊 Lendo: {arquivo.name}")
                df = pd.read_csv(arquivo, encoding='utf-8-sig')
                
                # Adicionar coluna de origem
                df['arquivo_origem'] = arquivo.name
                
                dataframes.append(df)
                linhas = len(df)
                total_linhas += linhas
                
                logger.info(f"      ✅ {linhas} registros carregados")
                
            except Exception as e:
                erro = {
                    'loja': loja_nome,
                    'arquivo': arquivo.name,
                    'erro': str(e)
                }
                self.erros.append(erro)
                logger.error(f"      ❌ Erro ao ler {arquivo.name}: {e}")
        
        if not dataframes:
            logger.error(f"   ❌ Nenhum arquivo foi carregado com sucesso para {loja_nome}")
            return None
        
        # Consolidar todos os DataFrames
        logger.info(f"   🔄 Consolidando {len(dataframes)} arquivo(s)...")
        
        try:
            # Concatenar todos os DataFrames
            df_consolidado = pd.concat(dataframes, ignore_index=True, sort=False)
            
            # Remover linhas completamente vazias
            df_consolidado = df_consolidado.dropna(how='all')
            
            # Nome do arquivo consolidado
            arquivo_consolidado = self.output_dir / f"{loja_nome}_consolidado.csv"
            
            # Salvar arquivo consolidado
            df_consolidado.to_csv(arquivo_consolidado, index=False, encoding='utf-8-sig')
            
            info_consolidacao = {
                'loja': loja_nome,
                'arquivos_origem': len(arquivos_csv),
                'arquivo_consolidado': arquivo_consolidado.name,
                'caminho_completo': str(arquivo_consolidado),
                'registros_total': len(df_consolidado),
                'colunas': len(df_consolidado.columns),
                'tamanho_mb': round(arquivo_consolidado.stat().st_size / 1024 / 1024, 2),
                'colunas_nomes': list(df_consolidado.columns),
                'status': 'SUCESSO'
            }
            
            self.consolidados.append(info_consolidacao)
            
            logger.info(f"   ✅ Consolidado: {len(df_consolidado)} registros, {len(df_consolidado.columns)} colunas")
            logger.info(f"   💾 Salvo em: {arquivo_consolidado.name}")
            
            return info_consolidacao
            
        except Exception as e:
            erro = {
                'loja': loja_nome,
                'arquivo': 'consolidacao',
                'erro': str(e)
            }
            self.erros.append(erro)
            logger.error(f"   ❌ Erro ao consolidar {loja_nome}: {e}")
            return None
    
    def processar_todas_lojas(self):
        """Processa todas as lojas encontradas"""
        logger.info("🚀 INICIANDO CONSOLIDAÇÃO POR LOJA")
        logger.info(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        logger.info("=" * 60)
        
        if not self.base_dir.exists():
            logger.error(f"❌ Diretório não encontrado: {self.base_dir}")
            return
        
        # Buscar pastas de lojas
        pastas_lojas = [p for p in self.base_dir.iterdir() if p.is_dir()]
        
        if not pastas_lojas:
            logger.error("❌ Nenhuma pasta de loja encontrada")
            return
        
        logger.info(f"📂 Encontradas {len(pastas_lojas)} loja(s): {', '.join([p.name for p in pastas_lojas])}")
        logger.info("")
        
        # Consolidar cada loja
        for pasta_loja in sorted(pastas_lojas):
            self.consolidar_loja(pasta_loja)
            logger.info("")  # Linha em branco entre lojas
        
        self.gerar_relatorio()
    
    def gerar_relatorio(self):
        """Gera relatório da consolidação"""
        logger.info("=" * 60)
        logger.info("📊 RELATÓRIO DE CONSOLIDAÇÃO POR LOJA")
        logger.info("=" * 60)
        logger.info(f"🏪 Lojas processadas: {len(self.consolidados) + len(set(e['loja'] for e in self.erros))}")
        logger.info(f"✅ Consolidadas com sucesso: {len(self.consolidados)}")
        logger.info(f"❌ Erros: {len(self.erros)}")
        
        if self.consolidados:
            logger.info(f"\n✅ LOJAS CONSOLIDADAS ({len(self.consolidados)}):")
            logger.info("-" * 50)
            
            total_registros = 0
            total_arquivos_origem = 0
            
            for loja in sorted(self.consolidados, key=lambda x: x['loja']):
                total_registros += loja['registros_total']
                total_arquivos_origem += loja['arquivos_origem']
                
                logger.info(f"\n🏪 {loja['loja']}:")
                logger.info(f"   📄 Arquivos origem: {loja['arquivos_origem']}")
                logger.info(f"   📊 Registros: {loja['registros_total']:,}")
                logger.info(f"   📋 Colunas: {loja['colunas']}")
                logger.info(f"   💾 Tamanho: {loja['tamanho_mb']} MB")
                logger.info(f"   📍 Arquivo: {loja['arquivo_consolidado']}")
                
                # Mostrar algumas colunas principais
                colunas_principais = [col for col in loja['colunas_nomes'][:10]]
                logger.info(f"   🏷️  Principais colunas: {', '.join(colunas_principais)}...")
            
            logger.info(f"\n📈 TOTAIS CONSOLIDADOS:")
            logger.info(f"   📄 Arquivos origem: {total_arquivos_origem}")
            logger.info(f"   📊 Registros totais: {total_registros:,}")
            logger.info(f"   🏪 Lojas: {len(self.consolidados)}")
        
        if self.erros:
            logger.info(f"\n❌ ERROS ENCONTRADOS ({len(self.erros)}):")
            logger.info("-" * 30)
            for erro in self.erros:
                logger.info(f"   • {erro['loja']}: {erro['arquivo']}")
                logger.info(f"     ❌ {erro['erro']}")
        
        logger.info(f"\n📁 ARQUIVOS CONSOLIDADOS SALVOS EM:")
        logger.info(f"   📍 {self.output_dir}")
        
        logger.info(f"\n🚀 PRÓXIMOS PASSOS:")
        logger.info("-" * 30)
        logger.info("   1. Revisar arquivos consolidados")
        logger.info("   2. Definir processo de normalização")
        logger.info("   3. Implementar normalização")
        logger.info("   4. Importar dados normalizados")
        
        logger.info("\n" + "=" * 60)
        
        if self.consolidados:
            logger.info("🎉 Consolidação por loja concluída com sucesso!")
        else:
            logger.error("❌ Consolidação falhou - nenhuma loja foi processada")

def main():
    consolidador = ConsolidadorPorLoja()
    consolidador.processar_todas_lojas()

if __name__ == "__main__":
    main()