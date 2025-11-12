#!/usr/bin/env python3
"""
Conversor Excel para CSV - Aba base_clientes_OS
===============================================

Converte especificamente a aba 'base_clientes_OS' dos arquivos Excel do OneDrive.
Esta aba contém os dados estruturados de clientes e OS que precisamos.
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

class ConversorAbaBaseClientesOS:
    def __init__(self):
        self.onedrive_base = Path("D:/OneDrive - Óticas Taty Mello/LOJAS")
        self.destino_base = Path("data/originais/oss/base_clientes_os")
        
        # Mapeamento de lojas
        self.mapeamento_lojas = {
            'MAUA': 'maua',
            'SUZANO': 'suzano', 
            'SUZANO2': 'suzano2',
            'PERUS': 'perus',
            'RIO_PEQUENO': 'rio_pequeno',
            'SAO_MATEUS': 'sao_mateus'
        }
        
        self.arquivos_convertidos = []
        self.arquivos_erro = []
    
    def verificar_onedrive(self):
        """Verifica se o OneDrive está acessível"""
        if not self.onedrive_base.exists():
            logger.error("❌ OneDrive não encontrado")
            logger.error("💡 Verifique se o OneDrive está sincronizado")
            return False
        
        logger.info(f"✅ OneDrive encontrado: {self.onedrive_base}")
        return True
    
    def encontrar_arquivos_com_aba(self):
        """Encontra arquivos Excel que possuem a aba 'base_clientes_OS'"""
        logger.info("🔍 Procurando arquivos Excel com aba 'base_clientes_OS'...")
        
        arquivos_encontrados = []
        
        for loja_onedrive, loja_projeto in self.mapeamento_lojas.items():
            pasta_loja = self.onedrive_base / loja_onedrive
            
            if pasta_loja.exists():
                logger.info(f"📂 Verificando loja: {loja_onedrive}")
                
                # Buscar recursivamente por arquivos Excel
                arquivos_excel = []
                for arquivo in pasta_loja.rglob("*.xlsx"):
                    if not arquivo.name.startswith('~'):  # Ignorar arquivos temporários
                        arquivos_excel.append(arquivo)
                for arquivo in pasta_loja.rglob("*.xlsm"):
                    if not arquivo.name.startswith('~'):
                        arquivos_excel.append(arquivo)
                
                logger.info(f"   📄 Encontrados {len(arquivos_excel)} arquivos Excel")
                
                # Verificar quais têm a aba base_clientes_OS
                for arquivo_excel in arquivos_excel:
                    try:
                        # Listar abas do arquivo
                        xl_file = pd.ExcelFile(arquivo_excel)
                        abas = xl_file.sheet_names
                        
                        if 'base_clientes_OS' in abas:
                            arquivos_encontrados.append({
                                'arquivo': arquivo_excel,
                                'loja_onedrive': loja_onedrive,
                                'loja_projeto': loja_projeto,
                                'abas': abas
                            })
                            logger.info(f"   ✅ ENCONTRADO: {arquivo_excel.name}")
                            logger.info(f"      📋 Abas: {', '.join(abas)}")
                        
                    except Exception as e:
                        logger.warning(f"   ⚠️ Erro ao verificar {arquivo_excel.name}: {e}")
            else:
                logger.warning(f"❌ Pasta não encontrada: {loja_onedrive}")
        
        return arquivos_encontrados
    
    def converter_aba_base_clientes(self, info_arquivo):
        """Converte a aba base_clientes_OS de um arquivo"""
        arquivo_excel = info_arquivo['arquivo']
        loja_projeto = info_arquivo['loja_projeto']
        loja_onedrive = info_arquivo['loja_onedrive']
        
        logger.info(f"🔄 Convertendo: {arquivo_excel.name} ({loja_onedrive})")
        
        try:
            # Criar pasta destino
            pasta_destino = self.destino_base / loja_projeto
            pasta_destino.mkdir(parents=True, exist_ok=True)
            
            # Ler a aba base_clientes_OS
            df = pd.read_excel(arquivo_excel, sheet_name='base_clientes_OS', engine='openpyxl')
            
            if df.empty:
                logger.warning(f"   ⚠️ Aba 'base_clientes_OS' está vazia em {arquivo_excel.name}")
                return None
            
            # Limpar dados básicos
            df = df.dropna(how='all')  # Remove linhas completamente vazias
            df = df.dropna(axis=1, how='all')  # Remove colunas completamente vazias
            
            # Nome do arquivo CSV
            nome_base = arquivo_excel.stem + "_base_clientes_OS"
            arquivo_csv = pasta_destino / f"{nome_base}.csv"
            
            # Salvar como CSV
            df.to_csv(arquivo_csv, index=False, encoding='utf-8-sig')
            
            info_conversao = {
                'loja': loja_onedrive,
                'arquivo_original': arquivo_excel.name,
                'arquivo_csv': arquivo_csv.name,
                'caminho_destino': str(arquivo_csv),
                'linhas': len(df),
                'colunas': len(df.columns),
                'tamanho_mb': round(arquivo_csv.stat().st_size / 1024 / 1024, 2),
                'colunas_nomes': list(df.columns),
                'status': 'SUCESSO'
            }
            
            self.arquivos_convertidos.append(info_conversao)
            
            logger.info(f"   ✅ Convertido: {len(df)} linhas, {len(df.columns)} colunas")
            logger.info(f"   📊 Colunas: {', '.join(df.columns[:5])}...")
            
            return info_conversao
            
        except Exception as e:
            erro_info = {
                'loja': loja_onedrive,
                'arquivo_original': arquivo_excel.name,
                'erro': str(e),
                'status': 'ERRO'
            }
            
            self.arquivos_erro.append(erro_info)
            logger.error(f"   ❌ Erro ao converter {arquivo_excel.name}: {e}")
            return None
    
    def processar_todos_arquivos(self):
        """Processa todos os arquivos encontrados"""
        logger.info("🚀 INICIANDO CONVERSÃO DA ABA base_clientes_OS")
        logger.info(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        logger.info("=" * 70)
        
        if not self.verificar_onedrive():
            return
        
        # Encontrar arquivos com a aba
        arquivos_encontrados = self.encontrar_arquivos_com_aba()
        
        if not arquivos_encontrados:
            logger.error("❌ Nenhum arquivo com aba 'base_clientes_OS' foi encontrado")
            return
        
        logger.info(f"\n🎯 Processando {len(arquivos_encontrados)} arquivo(s)...")
        
        # Converter cada arquivo
        for info_arquivo in arquivos_encontrados:
            self.converter_aba_base_clientes(info_arquivo)
        
        self.gerar_relatorio()
    
    def gerar_relatorio(self):
        """Gera relatório de conversão"""
        logger.info("\n" + "=" * 70)
        logger.info("📊 RELATÓRIO DE CONVERSÃO - ABA base_clientes_OS")
        logger.info("=" * 70)
        logger.info(f"📄 Arquivos processados: {len(self.arquivos_convertidos) + len(self.arquivos_erro)}")
        logger.info(f"✅ Convertidos com sucesso: {len(self.arquivos_convertidos)}")
        logger.info(f"❌ Erros: {len(self.arquivos_erro)}")
        
        if self.arquivos_convertidos:
            logger.info(f"\n✅ ARQUIVOS CONVERTIDOS ({len(self.arquivos_convertidos)}):")
            logger.info("-" * 50)
            
            total_linhas = 0
            
            # Agrupar por loja
            por_loja = {}
            for arquivo in self.arquivos_convertidos:
                loja = arquivo['loja']
                if loja not in por_loja:
                    por_loja[loja] = []
                por_loja[loja].append(arquivo)
                total_linhas += arquivo['linhas']
            
            for loja, arquivos in sorted(por_loja.items()):
                logger.info(f"\n📂 {loja} ({len(arquivos)} arquivo(s)):")
                for arquivo in arquivos:
                    logger.info(f"   • {arquivo['arquivo_csv']}")
                    logger.info(f"     📍 {arquivo['caminho_destino']}")
                    logger.info(f"     📊 {arquivo['linhas']} linhas, {arquivo['colunas']} colunas")
                    logger.info(f"     💾 {arquivo['tamanho_mb']} MB")
                    if arquivo['colunas_nomes']:
                        logger.info(f"     🏷️  Colunas: {', '.join(arquivo['colunas_nomes'][:5])}...")
            
            logger.info(f"\n📈 TOTAIS:")
            logger.info(f"   • Registros: {total_linhas:,} linhas")
            logger.info(f"   • Arquivos: {len(self.arquivos_convertidos)}")
        
        if self.arquivos_erro:
            logger.info(f"\n❌ ERROS ({len(self.arquivos_erro)}):")
            logger.info("-" * 30)
            for erro in self.arquivos_erro:
                logger.info(f"   • {erro['loja']}: {erro['arquivo_original']}")
                logger.info(f"     ❌ {erro['erro']}")
        
        logger.info(f"\n🚀 PRÓXIMOS PASSOS:")
        logger.info("-" * 30)
        logger.info("   1. Execute: python analisar_dados_originais.py")
        logger.info("   2. Verifique os dados da aba base_clientes_OS")
        logger.info("   3. Execute: python import_dados_completos.py")
        logger.info("   4. ✅ Dados importados para Supabase!")
        
        logger.info("\n" + "=" * 70)
        
        if self.arquivos_convertidos:
            logger.info("🎉 Conversão da aba base_clientes_OS concluída com sucesso!")
        else:
            logger.error("❌ Conversão falhou ou nenhum arquivo processado")

def main():
    conversor = ConversorAbaBaseClientesOS()
    conversor.processar_todos_arquivos()

if __name__ == "__main__":
    main()