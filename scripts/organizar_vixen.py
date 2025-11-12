#!/usr/bin/env python3
"""
Organizar Estrutura VIXEN
=========================

Organiza dados VIXEN igual fizemos com CXS e OSS.
"""

import shutil
from pathlib import Path
import pandas as pd

def main():
    base_dir = Path("d:/projetos/carne_facil/carne_facil")
    vixen_dir = base_dir / "data" / "originais" / "vixen"
    
    print("📁 ORGANIZANDO ESTRUTURA VIXEN")
    print("=" * 50)
    
    # Criar subpastas
    planilhas_dir = vixen_dir / "planilhas_originais"
    extraidos_dir = vixen_dir / "extraidos_corrigidos"
    finais_dir = vixen_dir / "finais_postgresql_prontos"
    
    planilhas_dir.mkdir(exist_ok=True)
    extraidos_dir.mkdir(exist_ok=True)
    finais_dir.mkdir(exist_ok=True)
    
    # Mover arquivo XLSX para planilhas_originais
    arquivo_xlsx = vixen_dir / "clientes_completos_vixen.XLSX"
    if arquivo_xlsx.exists():
        destino_xlsx = planilhas_dir / arquivo_xlsx.name
        shutil.move(str(arquivo_xlsx), str(destino_xlsx))
        print(f"✅ Movido: {arquivo_xlsx.name} → planilhas_originais/")
    
    # Mover CSV para extraidos_corrigidos
    arquivo_csv = vixen_dir / "vixen_planilha1.csv"
    if arquivo_csv.exists():
        destino_csv = extraidos_dir / "clientes_vixen_completo.csv"
        shutil.move(str(arquivo_csv), str(destino_csv))
        print(f"✅ Movido: {arquivo_csv.name} → extraidos_corrigidos/clientes_vixen_completo.csv")
    
    # Carregar dados para análise de empresas
    print(f"\n🏪 SEPARANDO POR EMPRESA...")
    
    if (extraidos_dir / "clientes_vixen_completo.csv").exists():
        df = pd.read_csv(extraidos_dir / "clientes_vixen_completo.csv")
        
        # Mapear empresas para lojas conhecidas
        mapeamento_empresas = {
            42: "SUZANO",  # Baseado na análise geográfica
            48: "MAUA"     # Baseado na análise geográfica
        }
        
        # Separar por empresa e salvar
        for empresa_id, empresa_nome in mapeamento_empresas.items():
            df_empresa = df[df['Emp.origem'] == empresa_id].copy()
            
            if len(df_empresa) > 0:
                # Adicionar colunas de controle
                df_empresa['loja_id'] = empresa_id
                df_empresa['loja_nome'] = empresa_nome
                df_empresa['data_processamento'] = pd.Timestamp.now()
                
                # Salvar na pasta extraidos_corrigidos
                arquivo_empresa = extraidos_dir / f"clientes_vixen_{empresa_nome.lower()}.csv"
                df_empresa.to_csv(arquivo_empresa, index=False)
                
                print(f"   ✅ {empresa_nome}: {len(df_empresa):,} clientes → {arquivo_empresa.name}")
                
                # Preparar arquivo final para banco
                colunas_finais = [
                    'ID', 'Cliente', 'Nome Completo', 'Endereço', 'Bairro', 
                    'Cidade', 'UF', 'CEP', 'Fone', 'E-mail', 'Vendedor',
                    'Como nos conheceu', 'Sexo', 'loja_id', 'loja_nome'
                ]
                
                df_final = df_empresa[colunas_finais].copy()
                arquivo_final = finais_dir / f"clientes_{empresa_nome.lower()}_final.csv"
                df_final.to_csv(arquivo_final, index=False)
                
                print(f"      📊 Final: {len(df_final):,} registros → {arquivo_final.name}")
    
    print(f"\n📋 ESTRUTURA VIXEN ORGANIZADA:")
    
    # Verificar estrutura final
    for subdir in sorted(vixen_dir.iterdir()):
        if subdir.is_dir():
            if subdir.name == "planilhas_originais":
                count = len(list(subdir.glob("*.xlsx")))
                print(f"   📂 {subdir.name}/ ({count} planilhas)")
            elif subdir.name == "extraidos_corrigidos":
                count = len(list(subdir.glob("*.csv")))
                print(f"   📂 {subdir.name}/ ({count} arquivos)")
            elif subdir.name == "finais_postgresql_prontos":
                count = len(list(subdir.glob("*.csv")))
                print(f"   📂 {subdir.name}/ ({count} arquivos finais)")
                
                # Mostrar detalhes dos arquivos finais
                for arquivo in sorted(subdir.glob("*.csv")):
                    try:
                        df_check = pd.read_csv(arquivo)
                        print(f"      ✅ {arquivo.name}: {len(df_check):,} registros")
                    except:
                        print(f"      ❌ {arquivo.name}: Erro ao verificar")
    
    print(f"\n🎯 VIXEN ORGANIZADO IGUAL CXS E OSS!")
    print(f"   📂 planilhas_originais/ → arquivo xlsx original")
    print(f"   📂 extraidos_corrigidos/ → dados processados")
    print(f"   📂 finais_postgresql_prontos/ → dados finais para banco")

if __name__ == "__main__":
    main()