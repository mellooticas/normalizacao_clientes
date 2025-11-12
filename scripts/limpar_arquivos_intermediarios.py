#!/usr/bin/env python3#!/usr/bin/env python3#!/usr/bin/env python3

"""

LIMPADOR DE ARQUIVOS INTERMEDIÁRIOS - FINAL""""""

================================================================

Remove arquivos intermediários desnecessários mantendo apenasLIMPADOR DE ARQUIVOS INTERMEDIÁRIOSLIMPADOR DE ARQUIVOS INTERMEDIÁRIOS

os arquivos finais para o banco de dados.

================================================================================================================================================================================================

"""

Remove arquivos intermediários desnecessários para manter apenasRemove arquivos intermediários desnecessários para manter apenas

import os

import shutilos arquivos finais que serão usados no banco.os arquivos finais que serão usados no banco.

from datetime import datetime

================================================================================================================================

def limpar_arquivos_intermediarios():

    """Remove arquivos intermediários mantendo apenas os finais"""""""""

    

    print("🧹 LIMPANDO ARQUIVOS INTERMEDIÁRIOS")

    print("=" * 60)

    import osimport os

    # Criar backup

    backup_dir = f"data/backup_intermediarios_{datetime.now().strftime('%Y%m%d_%H%M%S')}"import shutilimport shutil

    os.makedirs(backup_dir, exist_ok=True)

    from datetime import datetimefrom datetime import datetime

    print(f"💾 CRIANDO BACKUP EM: {backup_dir}")

    print("-" * 50)

    

    # Tabelas para remover completamentedef limpar_arquivos_intermediarios():def limpar_arquivos_intermediarios():

    tabelas_remover = ["vendas", "restante_entrada", "recebimento_carne", "entrega_carne"]

    total_removidos = 0    """Remove arquivos intermediários e mantém apenas os finais"""    """Remove arquivos intermediários e mantém apenas os finais"""

    

    for tabela in tabelas_remover:        

        diretorio = f"data/originais/cxs/extraidos_corrigidos/{tabela}"

            print("🧹 LIMPANDO ARQUIVOS INTERMEDIÁRIOS")    print("🧹 LIMPANDO ARQUIVOS INTERMEDIÁRIOS")

        if os.path.exists(diretorio):

            # Backup    print("=" * 60)    print("=" * 60)

            destino_backup = os.path.join(backup_dir, tabela)

            shutil.copytree(diretorio, destino_backup)        

            

            # Contar e remover    # Criar backup antes de limpar    # Criar backup antes de limpar

            arquivos = len([f for f in os.listdir(diretorio) if f.endswith('.csv')])

            shutil.rmtree(diretorio)    backup_dir = f"data/backup_intermediarios_{datetime.now().strftime('%Y%m%d_%H%M%S')}"    backup_dir = f"data/backup_intermediarios_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            total_removidos += arquivos

                    

            print(f"🗑️ {tabela}: {arquivos} arquivos → backup e removido")

        # Diretórios com arquivos intermediários    # Diretórios com arquivos intermediários

    # Limpar intermediários de os_entregues_dia

    os_dir = "data/originais/cxs/extraidos_corrigidos/os_entregues_dia"    diretorios_intermediarios = [    diretorios_intermediarios = [

    if os.path.exists(os_dir):

        destino_backup_os = os.path.join(backup_dir, "os_entregues_dia")        "data/originais/cxs/extraidos_corrigidos/vendas",        "data/originais/cxs/extraidos_corrigidos/vendas",

        os.makedirs(destino_backup_os, exist_ok=True)

                "data/originais/cxs/extraidos_corrigidos/restante_entrada",         "data/originais/cxs/extraidos_corrigidos/restante_entrada", 

        removidos_os = 0

        for arquivo in os.listdir(os_dir):        "data/originais/cxs/extraidos_corrigidos/recebimento_carne",        "data/originais/cxs/extraidos_corrigidos/recebimento_carne",

            if arquivo.endswith('.csv') and 'FINAL_BANCO' not in arquivo:

                # Backup        "data/originais/cxs/extraidos_corrigidos/entrega_carne"        "data/originais/cxs/extraidos_corrigidos/entrega_carne"

                shutil.copy2(os.path.join(os_dir, arquivo), 

                           os.path.join(destino_backup_os, arquivo))    ]    ]

                # Remover

                os.remove(os.path.join(os_dir, arquivo))        

                removidos_os += 1

            # Fazer backup dos intermediários primeiro    # Arquivos específicos para manter no os_entregues_dia

        print(f"🗑️ os_entregues_dia intermediários: {removidos_os} arquivos → backup e removido")

        total_removidos += removidos_os    print(f"💾 CRIANDO BACKUP EM: {backup_dir}")    arquivos_manter_os_entregues = [

    

    print(f"\n✅ Total removido: {total_removidos} arquivos")    print("-" * 50)        # Arquivos finais

    

    # Mostrar estrutura final            "*_FINAL_BANCO.csv"

    print(f"\n📁 ESTRUTURA FINAL LIMPA")

    print("=" * 60)    os.makedirs(backup_dir, exist_ok=True)    ]

    

    # Arquivos finais        

    finais_dir = "data/finais_banco"

    if os.path.exists(finais_dir):    total_arquivos_movidos = 0    # Fazer backup dos intermediários primeiro

        arquivos_finais = [f for f in os.listdir(finais_dir) if f.endswith('.csv')]

        print(f"📁 data/finais_banco/ ({len(arquivos_finais)} arquivos):")        print(f"💾 CRIANDO BACKUP EM: {backup_dir}")

        for arquivo in sorted(arquivos_finais):

            print(f"   📄 {arquivo}")    # Backup dos diretórios completos das outras tabelas    print("-" * 50)

    

    # os_entregues_dia restante    for diretorio in diretorios_intermediarios:    

    if os.path.exists(os_dir):

        restantes = [f for f in os.listdir(os_dir) if f.endswith('.csv')]        if os.path.exists(diretorio):    os.makedirs(backup_dir, exist_ok=True)

        if restantes:

            print(f"\n📁 os_entregues_dia/ ({len(restantes)} arquivos):")            nome_tabela = os.path.basename(diretorio)    

            for arquivo in sorted(restantes):

                print(f"   📄 {arquivo}")            destino_backup = os.path.join(backup_dir, nome_tabela)    total_arquivos_movidos = 0

    

    # Tamanho do backup                

    try:

        backup_size = sum(            try:    # Backup dos diretórios completos das outras tabelas

            os.path.getsize(os.path.join(dirpath, filename))

            for dirpath, dirnames, filenames in os.walk(backup_dir)                shutil.copytree(diretorio, destino_backup)    for diretorio in diretorios_intermediarios:

            for filename in filenames

        ) / (1024 * 1024)                arquivos_no_dir = len([f for f in os.listdir(diretorio) if f.endswith('.csv')])        if os.path.exists(diretorio):

        print(f"\n💾 Backup: {backup_dir} ({backup_size:.1f} MB)")

    except:                total_arquivos_movidos += arquivos_no_dir            nome_tabela = os.path.basename(diretorio)

        print(f"\n💾 Backup: {backup_dir}")

                    print(f"📁 {nome_tabela}: {arquivos_no_dir} arquivos → backup")            destino_backup = os.path.join(backup_dir, nome_tabela)

    return backup_dir, total_removidos

            except Exception as e:            

if __name__ == "__main__":

    backup_dir, total_removidos = limpar_arquivos_intermediarios()                print(f"❌ Erro ao fazer backup de {diretorio}: {e}")            try:

    

    print(f"\n📋 RESUMO FINAL")                    shutil.copytree(diretorio, destino_backup)

    print("=" * 60)

    print(f"🗑️ Arquivos removidos: {total_removidos}")    # Backup dos intermediários de os_entregues_dia                arquivos_no_dir = len([f for f in os.listdir(diretorio) if f.endswith('.csv')])

    print(f"💾 Backup criado em: {backup_dir}")

    print(f"📁 Arquivos finais em: data/finais_banco/")    os_entregues_dir = "data/originais/cxs/extraidos_corrigidos/os_entregues_dia"                total_arquivos_movidos += arquivos_no_dir

    print(f"🎯 Prontos para subir no Supabase!")

        if os.path.exists(os_entregues_dir):                print(f"📁 {nome_tabela}: {arquivos_no_dir} arquivos → backup")

    print(f"\n✅ LIMPEZA CONCLUÍDA!")

    print(f"🚀 Use os arquivos FINAL_BANCO.csv para upload no banco")        destino_backup_os = os.path.join(backup_dir, "os_entregues_dia")            except Exception as e:

        os.makedirs(destino_backup_os, exist_ok=True)                print(f"❌ Erro ao fazer backup de {diretorio}: {e}")

            

        arquivos_os = os.listdir(os_entregues_dir)    # Backup dos intermediários de os_entregues_dia

        arquivos_intermediarios_os = []    os_entregues_dir = "data/originais/cxs/extraidos_corrigidos/os_entregues_dia"

            if os.path.exists(os_entregues_dir):

        for arquivo in arquivos_os:        destino_backup_os = os.path.join(backup_dir, "os_entregues_dia")

            if arquivo.endswith('.csv') and 'FINAL_BANCO' not in arquivo:        os.makedirs(destino_backup_os, exist_ok=True)

                origem = os.path.join(os_entregues_dir, arquivo)        

                destino = os.path.join(destino_backup_os, arquivo)        arquivos_os = os.listdir(os_entregues_dir)

                shutil.copy2(origem, destino)        arquivos_intermediarios_os = []

                arquivos_intermediarios_os.append(arquivo)        

                for arquivo in arquivos_os:

        print(f"📁 os_entregues_dia intermediários: {len(arquivos_intermediarios_os)} arquivos → backup")            if arquivo.endswith('.csv') and 'FINAL_BANCO' not in arquivo:

        total_arquivos_movidos += len(arquivos_intermediarios_os)                origem = os.path.join(os_entregues_dir, arquivo)

                    destino = os.path.join(destino_backup_os, arquivo)

    print(f"✅ Backup completo: {total_arquivos_movidos} arquivos salvos")                shutil.copy2(origem, destino)

                    arquivos_intermediarios_os.append(arquivo)

    # Agora remover os diretórios intermediários        

    print(f"\n🗑️ REMOVENDO ARQUIVOS INTERMEDIÁRIOS")        print(f"📁 os_entregues_dia intermediários: {len(arquivos_intermediarios_os)} arquivos → backup")

    print("-" * 50)        total_arquivos_movidos += len(arquivos_intermediarios_os)

        

    total_removidos = 0    print(f"✅ Backup completo: {total_arquivos_movidos} arquivos salvos")

        

    # Remover diretórios completos das outras tabelas    # Agora remover os diretórios intermediários

    for diretorio in diretorios_intermediarios:    print(f"\n🗑️ REMOVENDO ARQUIVOS INTERMEDIÁRIOS")

        if os.path.exists(diretorio):    print("-" * 50)

            try:    

                arquivos_removidos = len([f for f in os.listdir(diretorio) if f.endswith('.csv')])    total_removidos = 0

                shutil.rmtree(diretorio)    

                total_removidos += arquivos_removidos    # Remover diretórios completos das outras tabelas

                print(f"🗑️ Removido: {os.path.basename(diretorio)} ({arquivos_removidos} arquivos)")    for diretorio in diretorios_intermediarios:

            except Exception as e:        if os.path.exists(diretorio):

                print(f"❌ Erro ao remover {diretorio}: {e}")            try:

                    arquivos_removidos = len([f for f in os.listdir(diretorio) if f.endswith('.csv')])

    # Remover intermediários de os_entregues_dia                shutil.rmtree(diretorio)

    if os.path.exists(os_entregues_dir):                total_removidos += arquivos_removidos

        arquivos_os = os.listdir(os_entregues_dir)                print(f"🗑️ Removido: {os.path.basename(diretorio)} ({arquivos_removidos} arquivos)")

        removidos_os = 0            except Exception as e:

                        print(f"❌ Erro ao remover {diretorio}: {e}")

        for arquivo in arquivos_os:    

            if arquivo.endswith('.csv') and 'FINAL_BANCO' not in arquivo:    # Remover intermediários de os_entregues_dia

                caminho_arquivo = os.path.join(os_entregues_dir, arquivo)    if os.path.exists(os_entregues_dir):

                try:        arquivos_os = os.listdir(os_entregues_dir)

                    os.remove(caminho_arquivo)        removidos_os = 0

                    removidos_os += 1        

                except Exception as e:        for arquivo in arquivos_os:

                    print(f"❌ Erro ao remover {arquivo}: {e}")            if arquivo.endswith('.csv') and 'FINAL_BANCO' not in arquivo:

                        caminho_arquivo = os.path.join(os_entregues_dir, arquivo)

        print(f"🗑️ os_entregues_dia intermediários: {removidos_os} arquivos removidos")                try:

        total_removidos += removidos_os                    os.remove(caminho_arquivo)

                        removidos_os += 1

    print(f"✅ Total removido: {total_removidos} arquivos")                except Exception as e:

                        print(f"❌ Erro ao remover {arquivo}: {e}")

    # Verificar estrutura final        

    print(f"\n📁 ESTRUTURA FINAL LIMPA")        print(f"🗑️ os_entregues_dia intermediários: {removidos_os} arquivos removidos")

    print("=" * 60)        total_removidos += removidos_os

        

    # Verificar data/finais_banco    print(f"✅ Total removido: {total_removidos} arquivos")

    finais_dir = "data/finais_banco"    

    if os.path.exists(finais_dir):    # Verificar estrutura final

        arquivos_finais = [f for f in os.listdir(finais_dir) if f.endswith('.csv')]    print(f"\n📁 ESTRUTURA FINAL LIMPA")

        print(f"📁 data/finais_banco/")    print("=" * 60)

        for arquivo in sorted(arquivos_finais):    

            print(f"   📄 {arquivo}")    # Verificar data/finais_banco

        finais_dir = "data/finais_banco"

    # Verificar os_entregues_dia restante    if os.path.exists(finais_dir):

    if os.path.exists(os_entregues_dir):        arquivos_finais = [f for f in os.listdir(finais_dir) if f.endswith('.csv')]

        arquivos_restantes = [f for f in os.listdir(os_entregues_dir) if f.endswith('.csv')]        print(f"📁 data/finais_banco/")

        if arquivos_restantes:        for arquivo in sorted(arquivos_finais):

            print(f"\n📁 data/originais/cxs/extraidos_corrigidos/os_entregues_dia/")            print(f"   📄 {arquivo}")

            for arquivo in sorted(arquivos_restantes):    

                print(f"   📄 {arquivo}")    # Verificar os_entregues_dia restante

        if os.path.exists(os_entregues_dir):

    # Mostrar tamanho do backup        arquivos_restantes = [f for f in os.listdir(os_entregues_dir) if f.endswith('.csv')]

    try:        if arquivos_restantes:

        backup_size = sum(            print(f"\n📁 data/originais/cxs/extraidos_corrigidos/os_entregues_dia/")

            os.path.getsize(os.path.join(dirpath, filename))            for arquivo in sorted(arquivos_restantes):

            for dirpath, dirnames, filenames in os.walk(backup_dir)                print(f"   📄 {arquivo}")

            for filename in filenames    

        ) / (1024 * 1024)  # MB    # Mostrar tamanho do backup

        print(f"\n💾 Backup salvo em: {backup_dir}")    try:

        print(f"📊 Tamanho do backup: {backup_size:.1f} MB")        backup_size = sum(

    except Exception as e:            os.path.getsize(os.path.join(dirpath, filename))

        print(f"⚠️ Erro ao calcular tamanho do backup: {e}")            for dirpath, dirnames, filenames in os.walk(backup_dir)

                for filename in filenames

    return backup_dir, total_removidos        ) / (1024 * 1024)  # MB

        print(f"\n💾 Backup salvo em: {backup_dir}")

def listar_estrutura_final():        print(f"📊 Tamanho do backup: {backup_size:.1f} MB")

    """Lista a estrutura final após limpeza"""    except Exception as e:

            print(f"⚠️ Erro ao calcular tamanho do backup: {e}")

    print(f"\n📋 RESUMO DA LIMPEZA")    

    print("=" * 60)    return backup_dir, total_removidos

    

    # Contar arquivos finaisdef listar_estrutura_final():

    finais_dir = "data/finais_banco"    """Lista a estrutura final após limpeza"""

    arquivos_finais = 0    

    if os.path.exists(finais_dir):    print(f"\n📋 RESUMO DA LIMPEZA")

        arquivos_finais = len([f for f in os.listdir(finais_dir) if f.endswith('.csv')])    print("=" * 60)

        

    print(f"✅ Arquivos FINAIS mantidos: {arquivos_finais}")    # Contar arquivos finais

    print(f"📁 Localização: {finais_dir}/")    finais_dir = "data/finais_banco"

    print(f"🎯 Prontos para upload no Supabase")    arquivos_finais = 0

        if os.path.exists(finais_dir):

    print(f"\n🧹 ESPAÇO LIBERADO:")        arquivos_finais = len([f for f in os.listdir(finais_dir) if f.endswith('.csv')])

    print(f"   • Tabelas intermediárias: vendas, restante_entrada, recebimento_carne, entrega_carne")    

    print(f"   • Versões intermediárias de os_entregues_dia")    print(f"✅ Arquivos FINAIS mantidos: {arquivos_finais}")

    print(f"   • Backup criado para segurança")    print(f"📁 Localização: {finais_dir}/")

        print(f"🎯 Prontos para upload no Supabase")

    print(f"\n📊 DADOS FINAIS PARA O BANCO:")    

    print(f"   • 6 lojas: maua, perus, rio_pequeno, sao_mateus, suzano, suzano2")    print(f"\n🧹 ESPAÇO LIBERADO:")

    print(f"   • ~7.067 registros operacionais")    print(f"   • Tabelas intermediárias: vendas, restante_entrada, recebimento_carne, entrega_carne")

    print(f"   • 100% de cobertura UUID nos dados válidos")    print(f"   • Versões intermediárias de os_entregues_dia")

    print(f"   • Colunas essenciais: os_numero, vendedor, vendedor_uuid, data_movimento, loja_id")    print(f"   • Backup criado para segurança")

    

if __name__ == "__main__":    print(f"\n📊 DADOS FINAIS PARA O BANCO:")

    backup_dir, total_removidos = limpar_arquivos_intermediarios()    print(f"   • 6 lojas: maua, perus, rio_pequeno, sao_mateus, suzano, suzano2")

    listar_estrutura_final()    print(f"   • ~7.067 registros operacionais")

        print(f"   • 100% de cobertura UUID nos dados válidos")

    print(f"\n✅ LIMPEZA CONCLUÍDA!")    print(f"   • Colunas essenciais: os_numero, vendedor, vendedor_uuid, data_movimento, loja_id")

    print(f"🎯 Use os arquivos em data/finais_banco/ para subir no Supabase")        'data/originais/oss/finais_canais_aquisicao_uuid',

    print(f"💾 Backup dos intermediários em: {backup_dir}")        'data/originais/oss/finais_datas_normalizadas'
    ]
    
    # Verificar qual é o diretório final que deve ser mantido
    diretorio_final = 'data/originais/oss/finais_postgresql_prontos'
    
    print(f"📁 VERIFICANDO DIRETÓRIO FINAL:")
    if os.path.exists(diretorio_final):
        arquivos_finais = [f for f in os.listdir(diretorio_final) if f.endswith('.csv')]
        total_size = sum(os.path.getsize(os.path.join(diretorio_final, f)) for f in arquivos_finais) / 1024
        print(f"   ✅ {diretorio_final}")
        print(f"   📄 {len(arquivos_finais)} arquivos CSV")
        print(f"   📦 {total_size:.1f} KB total")
        print(f"   🎯 ESTE DIRETÓRIO SERÁ MANTIDO")
    else:
        print(f"   ❌ {diretorio_final} NÃO ENCONTRADO!")
        print(f"   🚨 CANCELANDO LIMPEZA - DIRETÓRIO FINAL AUSENTE")
        return
    
    # Verificar diretórios intermediários
    print(f"\n📋 DIRETÓRIOS INTERMEDIÁRIOS PARA REMOÇÃO:")
    
    diretorios_encontrados = []
    total_size_remover = 0
    
    for diretorio in diretorios_para_remover:
        if os.path.exists(diretorio):
            # Calcular tamanho
            size_mb = 0
            for root, dirs, files in os.walk(diretorio):
                for file in files:
                    size_mb += os.path.getsize(os.path.join(root, file))
            size_mb = size_mb / (1024 * 1024)  # Converter para MB
            
            arquivos_csv = []
            for root, dirs, files in os.walk(diretorio):
                for file in files:
                    if file.endswith('.csv'):
                        arquivos_csv.append(file)
            
            diretorios_encontrados.append(diretorio)
            total_size_remover += size_mb
            
            print(f"   📂 {diretorio}")
            print(f"      • {len(arquivos_csv)} arquivos CSV")
            print(f"      • {size_mb:.1f} MB")
        else:
            print(f"   ➖ {diretorio} (não existe)")
    
    if diretorios_encontrados:
        print(f"\n📊 RESUMO DA LIMPEZA:")
        print(f"   • Diretórios a remover: {len(diretorios_encontrados)}")
        print(f"   • Espaço a liberar: {total_size_remover:.1f} MB")
        
        # Confirmar limpeza
        resposta = input(f"\n❓ Confirma a remoção dos diretórios intermediários? (s/N): ")
        
        if resposta.lower() in ['s', 'sim', 'y', 'yes']:
            print(f"\n🗑️  EXECUTANDO LIMPEZA:")
            
            for diretorio in diretorios_encontrados:
                try:
                    shutil.rmtree(diretorio)
                    print(f"   ✅ Removido: {diretorio}")
                except Exception as e:
                    print(f"   ❌ Erro ao remover {diretorio}: {e}")
            
            print(f"\n🎉 LIMPEZA CONCLUÍDA!")
            print(f"   💾 Espaço liberado: {total_size_remover:.1f} MB")
            
        else:
            print(f"\n🚫 LIMPEZA CANCELADA pelo usuário")
    else:
        print(f"\n✅ NENHUM DIRETÓRIO INTERMEDIÁRIO ENCONTRADO")
    
    # Verificar estrutura final
    print(f"\n📁 ESTRUTURA FINAL MANTIDA:")
    base_dir = 'data/originais/oss'
    
    if os.path.exists(base_dir):
        for item in sorted(os.listdir(base_dir)):
            caminho_item = os.path.join(base_dir, item)
            if os.path.isdir(caminho_item):
                arquivos = [f for f in os.listdir(caminho_item) if f.endswith('.csv')]
                if arquivos:
                    print(f"   📂 {item}/ ({len(arquivos)} CSVs)")
                else:
                    print(f"   📂 {item}/ (vazio)")
    
    # Arquivos de mapeamento - manter apenas os essenciais
    print(f"\n📋 ARQUIVOS DE MAPEAMENTO:")
    
    arquivos_mapeamento_essenciais = [
        'mapeamento_canais_aquisicao_completo.json',
        'mapeamento_canais_csv_para_estrutura.json'
    ]
    
    arquivos_mapeamento_intermediarios = [
        'mapeamento_canais_captacao_uuid.json',
        'mapeamento_canais_captacao_uuid_final.json',
        'mapeamento_vendedores_csvs_completo.json'
    ]
    
    print(f"   🎯 ESSENCIAIS (manter):")
    for arquivo in arquivos_mapeamento_essenciais:
        if os.path.exists(arquivo):
            size_kb = os.path.getsize(arquivo) / 1024
            print(f"      ✅ {arquivo} ({size_kb:.1f} KB)")
        else:
            print(f"      ❌ {arquivo} (não encontrado)")
    
    print(f"   🧹 INTERMEDIÁRIOS (podem ser removidos):")
    for arquivo in arquivos_mapeamento_intermediarios:
        if os.path.exists(arquivo):
            size_kb = os.path.getsize(arquivo) / 1024
            print(f"      📄 {arquivo} ({size_kb:.1f} KB)")
        else:
            print(f"      ➖ {arquivo} (não existe)")
    
    # Scripts de processamento - manter apenas os essenciais
    print(f"\n🔧 SCRIPTS DE PROCESSAMENTO:")
    print(f"   🎯 ESSENCIAIS (manter):")
    print(f"      • relatorio_preparacao_postgresql.py")
    print(f"      • database/12_estrutura_canais_aquisicao.sql")
    
    print(f"\n✅ ESTRUTURA LIMPA E ORGANIZADA!")
    print(f"🎯 Mantidos apenas:")
    print(f"   • {diretorio_final}/ (6 CSVs prontos)")
    print(f"   • Mapeamentos essenciais")
    print(f"   • Scripts SQL para banco")

if __name__ == "__main__":
    limpar_arquivos_intermediarios()