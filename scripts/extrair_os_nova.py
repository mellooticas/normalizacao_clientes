#!/usr/bin/env python3
"""
Extrator de Dados de OS Nova
============================

Extrai dados estruturados dos formulários de OS NOVA convertidos do OneDrive.
Cada arquivo representa uma ordem de serviço com dados de cliente e venda.
"""

import pandas as pd
import os
from pathlib import Path
import logging
from datetime import datetime
import re

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class ExtratorOSNova:
    def __init__(self):
        self.base_dir = Path("data/originais/oss/por_loja")
        self.clientes_extraidos = []
        self.vendas_extraidas = []
        self.erros = []
    
    def extrair_valor_linha(self, df, termo_busca, coluna_inicial=1):
        """Extrai valor de uma linha que contém o termo de busca"""
        try:
            # Procurar linha que contém o termo
            for idx, row in df.iterrows():
                row_text = ' '.join([str(cell) for cell in row if pd.notna(cell)])
                if termo_busca.upper() in row_text.upper():
                    # Tentar diferentes colunas para encontrar o valor
                    for col in range(coluna_inicial, len(row)):
                        valor = row.iloc[col]
                        if pd.notna(valor) and str(valor).strip() and str(valor).strip() != termo_busca:
                            return str(valor).strip()
            return None
        except Exception as e:
            logger.warning(f"Erro ao extrair {termo_busca}: {e}")
            return None
    
    def extrair_dados_os(self, arquivo_csv, loja):
        """Extrai dados estruturados de uma OS NOVA"""
        try:
            df = pd.read_csv(arquivo_csv)
            
            # Dados do cliente - tentar extrair nome de forma mais robusta
            nome = None
            
            # Procurar linha com "NOME:" especificamente
            for idx, row in df.iterrows():
                row_text = ' '.join([str(cell) for cell in row if pd.notna(cell)])
                if "NOME:" in row_text.upper():
                    # Encontrar a posição do termo NOME: e pegar o próximo valor não vazio
                    for col in range(len(row)):
                        if pd.notna(row.iloc[col]) and "NOME" in str(row.iloc[col]).upper():
                            # Procurar nas próximas colunas
                            for next_col in range(col + 1, len(row)):
                                valor = row.iloc[next_col]
                                if pd.notna(valor) and str(valor).strip() and "DT NASC" not in str(valor).upper():
                                    nome = str(valor).strip()
                                    break
                            break
                    break
            
            # Se não encontrou o nome, usar método anterior
            if not nome:
                nome = self.extrair_valor_linha(df, "NOME:")
            
            cpf = self.extrair_valor_linha(df, "CPF")
            rg = self.extrair_valor_linha(df, "RG")
            dt_nasc = self.extrair_valor_linha(df, "DT NASC")
            telefone = self.extrair_valor_linha(df, "TELEFONE")
            celular = self.extrair_valor_linha(df, "CELULAR")
            email = self.extrair_valor_linha(df, "EMAIL")
            cep = self.extrair_valor_linha(df, "CEP")
            endereco = self.extrair_valor_linha(df, "END:")
            numero = self.extrair_valor_linha(df, "Nº") or self.extrair_valor_linha(df, "N")
            bairro = self.extrair_valor_linha(df, "BAIRRO")
            complemento = self.extrair_valor_linha(df, "COMP")
            
            # Dados da venda/OS
            data_compra = self.extrair_valor_linha(df, "DATA DE COMPRA")
            consultor = self.extrair_valor_linha(df, "CONSULTOR")
            os_numero = self.extrair_valor_linha(df, "OS N°")
            vixen_id = self.extrair_valor_linha(df, "VIXEN")
            venda = self.extrair_valor_linha(df, "VENDA")
            garantia = self.extrair_valor_linha(df, "GARANTIA")
            como_conheceu = self.extrair_valor_linha(df, "COMO CONHECEU")
            prev_entrega = self.extrair_valor_linha(df, "PREV DE ENTR")
            
            # Validar se temos dados mínimos
            if not nome or nome.upper() in ["DT NASC.:", "NOME:"]:
                logger.warning(f"Nome não encontrado ou inválido em {arquivo_csv.name}")
                return None, None
            
            # Montar registro do cliente
            cliente = {
                'nome': nome,
                'cpf': self.limpar_cpf(cpf),
                'rg': rg,
                'dt_nascimento': self.converter_data(dt_nasc),
                'telefone': telefone,
                'celular': celular,
                'email': email,
                'cep': cep,
                'endereco': endereco,
                'numero': numero,
                'bairro': bairro,
                'complemento': complemento,
                'loja': loja,
                'arquivo_origem': arquivo_csv.name
            }
            
            # Montar registro da venda/OS
            venda_os = {
                'os_numero': os_numero,
                'vixen_id': vixen_id,
                'data_compra': self.converter_data(data_compra),
                'consultor': consultor,
                'cliente_nome': nome,
                'cliente_cpf': self.limpar_cpf(cpf),
                'venda': venda,
                'garantia': garantia,
                'como_conheceu': como_conheceu,
                'prev_entrega': self.converter_data(prev_entrega),
                'loja': loja,
                'arquivo_origem': arquivo_csv.name
            }
            
            return cliente, venda_os
            
        except Exception as e:
            erro = {
                'arquivo': arquivo_csv.name,
                'loja': loja,
                'erro': str(e)
            }
            self.erros.append(erro)
            logger.error(f"❌ Erro ao processar {arquivo_csv.name}: {e}")
            return None, None
    
    def limpar_cpf(self, cpf):
        """Remove formatação do CPF"""
        if not cpf:
            return None
        return re.sub(r'[^\d]', '', str(cpf))
    
    def converter_data(self, data_str):
        """Converte string de data para formato padrão"""
        if not data_str or pd.isna(data_str):
            return None
        
        try:
            # Remover timestamp se presente
            data_str = str(data_str).split(' ')[0]
            
            # Tentar diferentes formatos
            formatos = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
            for formato in formatos:
                try:
                    return datetime.strptime(data_str, formato).date()
                except:
                    continue
            return None
        except:
            return None
    
    def processar_todas_oss(self):
        """Processa todos os arquivos OS NOVA de todas as lojas"""
        logger.info("🚀 INICIANDO EXTRAÇÃO DE DADOS DAS OS NOVA")
        logger.info("=" * 60)
        
        total_arquivos = 0
        total_clientes = 0
        total_vendas = 0
        
        for loja_dir in self.base_dir.iterdir():
            if loja_dir.is_dir():
                loja_nome = loja_dir.name.upper()
                logger.info(f"📂 Processando loja: {loja_nome}")
                
                arquivos_os = list(loja_dir.glob("OS NOVA*.csv"))
                logger.info(f"   📄 Encontrados {len(arquivos_os)} arquivo(s)")
                
                for arquivo in arquivos_os:
                    total_arquivos += 1
                    logger.info(f"   🔄 Processando: {arquivo.name}")
                    
                    cliente, venda = self.extrair_dados_os(arquivo, loja_nome)
                    
                    if cliente and venda:
                        self.clientes_extraidos.append(cliente)
                        self.vendas_extraidas.append(venda)
                        total_clientes += 1
                        total_vendas += 1
                        logger.info(f"      ✅ Extraído: {cliente.get('nome', 'Nome não encontrado')}")
                    else:
                        logger.warning(f"      ⚠️ Falha na extração")
        
        self.gerar_relatorio(total_arquivos, total_clientes, total_vendas)
        self.salvar_dados_extraidos()
    
    def gerar_relatorio(self, total_arquivos, total_clientes, total_vendas):
        """Gera relatório de extração"""
        logger.info("\n" + "=" * 60)
        logger.info("📊 RELATÓRIO DE EXTRAÇÃO")
        logger.info("=" * 60)
        logger.info(f"📄 Arquivos processados: {total_arquivos}")
        logger.info(f"👥 Clientes extraídos: {total_clientes}")
        logger.info(f"🛒 Vendas/OS extraídas: {total_vendas}")
        logger.info(f"❌ Erros: {len(self.erros)}")
        
        if self.erros:
            logger.info("\n⚠️ ERROS ENCONTRADOS:")
            for erro in self.erros:
                logger.error(f"   • {erro['arquivo']} ({erro['loja']}): {erro['erro']}")
        
        # Estatísticas por loja
        if self.clientes_extraidos:
            logger.info("\n📊 ESTATÍSTICAS POR LOJA:")
            lojas_stats = {}
            for cliente in self.clientes_extraidos:
                loja = cliente['loja']
                lojas_stats[loja] = lojas_stats.get(loja, 0) + 1
            
            for loja, count in sorted(lojas_stats.items()):
                logger.info(f"   🏪 {loja}: {count} cliente(s)")
    
    def salvar_dados_extraidos(self):
        """Salva dados extraídos em CSV"""
        output_dir = Path("data/clientes/_consolidado")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if self.clientes_extraidos:
            # Salvar clientes
            df_clientes = pd.DataFrame(self.clientes_extraidos)
            arquivo_clientes = output_dir / "clientes_os_nova_extraidos.csv"
            df_clientes.to_csv(arquivo_clientes, index=False, encoding='utf-8-sig')
            logger.info(f"💾 Clientes salvos em: {arquivo_clientes}")
        
        if self.vendas_extraidas:
            # Salvar vendas/OS
            df_vendas = pd.DataFrame(self.vendas_extraidas)
            arquivo_vendas = output_dir / "vendas_os_nova_extraidas.csv"
            df_vendas.to_csv(arquivo_vendas, index=False, encoding='utf-8-sig')
            logger.info(f"💾 Vendas/OS salvas em: {arquivo_vendas}")
        
        logger.info("\n🎉 EXTRAÇÃO CONCLUÍDA COM SUCESSO!")

def main():
    extrator = ExtratorOSNova()
    extrator.processar_todas_oss()

if __name__ == "__main__":
    main()