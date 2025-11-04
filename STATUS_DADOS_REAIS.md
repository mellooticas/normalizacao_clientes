# 🎯 AMBIENTE PREPARADO PARA DADOS REAIS

## ✅ ESTRUTURA CRIADA

```
data/originais/
├── 📂 vixen/              # Sistema Vixen
│   ├── clientes/          # Planilhas de clientes
│   ├── vendas/            # Relatórios de vendas  
│   └── produtos/          # Catálogos
│
├── 📂 oss/                # Ordens de Serviço
│   ├── por_loja/          # OS por loja individual
│   │   ├── suzano/
│   │   ├── maua/
│   │   ├── perus/
│   │   ├── rio_pequeno/
│   │   ├── sao_mateus/
│   │   └── suzano2/
│   └── consolidadas/      # OS já processadas
│
├── 📂 cxs/                # Dados Financeiros
│   ├── diario/            # Movimento diário
│   ├── mensal/            # Fechamentos mensais
│   └── anual/             # Balanços anuais
│
└── 📂 controles_geral/    # Planilhas Administrativas
    ├── inventario/        # Controle de estoque
    ├── funcionarios/      # Dados de RH
    └── campanhas/         # Marketing
```

## 🛠️ SCRIPTS PRONTOS

### 1. Analisador de Dados
```bash
python analisar_dados_originais.py
```
- 🔍 Varre todas as pastas
- 📊 Identifica tipos de arquivo
- 📋 Gera relatório completo
- 🏷️ Classifica conteúdo automaticamente

### 2. Importador Completo
```bash  
python import_dados_completos.py
```
- 📥 Processa todos os arquivos encontrados
- 🔄 Importa direto para Supabase
- ✅ Valida dados importados
- 📈 Gera estatísticas finais

### 3. Teste de Conexão
```bash
python test_supabase.py
```
- 🔗 Testa credenciais Supabase
- 📊 Verifica estrutura do banco
- ⚙️ Diagnostica problemas

## 📋 WORKFLOW RECOMENDADO

### Passo 1: Organize os Dados
1. **Coloque arquivos Excel/CSV** nas pastas apropriadas
2. **Mantenha nomes originais** dos arquivos
3. **Organize por data** quando possível

### Passo 2: Analise os Dados
```bash
python analisar_dados_originais.py
```
- Verifica se todos os arquivos foram detectados
- Identifica tipos de conteúdo
- Estima quantidade de registros

### Passo 3: Atualize Supabase (se necessário)
```bash
python test_supabase.py
```
- Se falhar, atualize credenciais no `.env`
- Siga instruções em `ATUALIZE_SUPABASE.md`

### Passo 4: Execute Importação
```bash
python import_dados_completos.py
```
- Processa todos os dados encontrados
- Importa para Supabase
- Gera relatório final

## 🎯 TIPOS DE ARQUIVO ACEITOS

### ✅ Formatos Suportados
- `.xlsx` - Excel moderno
- `.xls` - Excel legado  
- `.csv` - Valores separados por vírgula
- `.xlsm` - Excel com macros

### 🏷️ Detecção Automática
- **CLIENTES**: CPF, nome, telefone, email
- **VENDAS**: valores, datas, produtos
- **ORDENS_SERVICO**: número OS, atendimentos
- **FINANCEIRO**: caixa, pagamentos
- **INVENTARIO**: estoque, produtos
- **VIXEN_EXPORT**: exportações do sistema

## 📊 RESULTADO ESPERADO

Após importação completa:
- 🎯 **Dados reais** das 6 lojas
- 📈 **Volume correto** de registros
- ✅ **Validação completa** 
- 🔄 **Sincronização** com Supabase

## 🚨 STATUS ATUAL

- ✅ **Estrutura de pastas**: Criada e pronta
- ✅ **Scripts de análise**: Funcionais
- ✅ **Scripts de importação**: Preparados
- ⏳ **Aguardando**: Dados originais reais
- ⚠️ **Credenciais Supabase**: Precisam atualização

---

**🎯 PRÓXIMO PASSO**: Coloque os arquivos Excel/CSV nas pastas e execute `python analisar_dados_originais.py`