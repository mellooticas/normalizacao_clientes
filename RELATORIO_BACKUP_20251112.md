# 📊 Relatório Detalhado do Backup - 2025-11-12

## 🗂️ Informações do Backup

- **Data de Criação**: 2025-11-12 às 12:35:39
- **Localização**: `/d/projetos/normalizacao_clientes/backup_from_repo/20251112_123539/`
- **Origem**: Arquivo de dados movidos de `carne_facil` → `normalizacao_clientes`
- **Status**: ✅ Completo e seguro

---

## 📈 Estatísticas Gerais

| Métrica | Valor |
|---------|-------|
| **Arquivos Totais** | 926 |
| **Diretórios** | 100 |
| **Tamanho Total** | 719 MB |
| **Maior Arquivo** | ITENS_VENDA_SEM_DUPLICATAS_20251105_122553.csv (99.21 MB) |

---

## 📁 Distribuição por Tipo de Arquivo

| Extensão | Quantidade | Nota |
|----------|-----------|------|
| `.csv` | 789 | Dados normalizados e processados |
| `.xlsx` | 136 | Planilhas Excel originais |
| `.xls` | 1 | Legado de dados |

---

## 📊 Top 20 Maiores Arquivos

| Tamanho | Nome |
|---------|------|
| 99.21 MB | ITENS_VENDA_SEM_DUPLICATAS_20251105_122553.csv |
| 99.21 MB | ITENS_VENDA_PARA_BANCO_20251105_121504.csv |
| 12.43 MB | cilentes_uuid_completo.xlsx |
| 12.27 MB | trans_financ_consolidado_completo.csv |
| 10.79 MB | itens_venda_preparados_20251105_090114.csv |
| 10.74 MB | itens_venda_CLASSIFICADOS_20251105_094225.csv |
| 10.10 MB | ORDEM DE SERVIÇO PDV.csv |
| 7.43 MB | ordem_servico_pdv_outros_pagamentos_com_uuid_normalizado.csv |
| 6.24 MB | clientes_suzano.csv |
| 5.97 MB | clientes_master_suzano.csv |
| 5.97 MB | clientes_suzano.csv (originais) |
| 5.97 MB | clientes_suzano.csv (importacao) |
| 5.97 MB | clientes_suzano.csv (clientes_uuid) |
| 5.65 MB | clientes_suzano_final.csv |
| 5.65 MB | clientes_vixen_suzano_original.csv |
| 5.59 MB | conf_dav_normalizado_20251105_040621.csv |
| 5.45 MB | clientes_vixen_suzano.csv |
| 4.92 MB | normalizacao_clientes.xlsx |
| 4.72 MB | vendas_totais_com_uuid.csv |
| 4.71 MB | OSS_COM_IDS_CLIENTES_20251109_210100.csv |

---

## 📂 Tamanho por Subdiretório Principal

```
1_normalizacao/                           719 MB
├── dados_processados/                    719 MB (100%)
│   ├── originais/                        363 MB (50.5%)
│   ├── ITENS_VENDA_SEM_DUPLICATAS...    100 MB (13.9%)
│   ├── ITENS_VENDA_PARA_BANCO...        100 MB (13.9%)
│   ├── processados/                       40 MB (5.6%)
│   ├── vendas_para_importar/              28 MB (3.9%)
│   ├── clientes/                          15 MB (2.1%)
│   ├── importacao_clientes/               13 MB (1.8%)
│   ├── finais_banco_completo/             13 MB (1.8%)
│   ├── clientes_uuid/                     12 MB (1.7%)
│   ├── itens_venda_preparados...         11 MB (1.5%)
│   ├── itens_venda_CLASSIFICADOS...      11 MB (1.5%)
│   ├── telefones_para_importar/           3.8 MB (0.5%)
│   ├── leads_com_auditoria...            3.3 MB (0.5%)
│   ├── leads_marketing_padronizados...   3.0 MB (0.4%)
│   ├── enderecos_para_importar/           2.4 MB (0.3%)
│   └── [outros diretórios]               ~3 MB (<1%)
```

---

## 🏪 Conteúdo por Categoria

### 1️⃣ **Dados Originais (363 MB)**
- Controles gerais (conf_dav, lista_dav, mov_cx, trans_financ)
- Clientes por loja (Mauá, Perus, Rio Pequeno, São Mateus, Suzano, Suzano2)
- Ordem de Serviço (OS NOVA por loja)
- Vixen (clientes, canais, extraídos)

### 2️⃣ **Itens de Venda (199 MB)**
- ITENS_VENDA_SEM_DUPLICATAS_20251105_122553.csv (99 MB)
- ITENS_VENDA_PARA_BANCO_20251105_121504.csv (99 MB)
- Preparados e classificados para banco

### 3️⃣ **Vendas Processadas (40 MB)**
- Vendas por loja (Mauá, Perus, Rio Pequeno, São Mateus, Suzano, Suzano2)
- Todas as lojas consolidadas
- Com UUIDs enriquecidos
- Finais para importação

### 4️⃣ **Clientes e Endereços (40 MB)**
- Clientes por loja
- UUIDs e normalizados
- Endereços para importar
- Consolidação master

### 5️⃣ **Entrega e Carnes (50 MB)**
- Entrega de carnes por loja
- OS entregues por dia
- Recebimento de carnes
- Restante de entrada

---

## 🎯 Principais Estruturas de Dados

### **Clientes**
- **Suzano**: 6,410 registros
- **Mauá**: 2,852 registros
- **Perus**: 610 registros
- **Rio Pequeno**: 413 registros
- **São Mateus**: 172 registros
- **Suzano2**: 239 registros
- **Total Consolidado**: ~9,261 registros únicos com UUID

### **Ordem de Serviço (OS)**
- **Total**: 25,706 OSs processadas
- **Valor Total**: R$ 3.971.617,86
- **Com Cliente ID**: Mapeadas e validadas
- **Normalizadas**: CPF, data, vendedor validados

### **Financeiro**
- **Trans. Financeiras Consolidadas**: 27.576 registros
- **Por Origem**: VENDA, CARNE LANCASTER, REC. CORRENTISTA, SANGRIA, FUNDO DE CAIXA
- **Com UUID**: Todos os registros enriquecidos com customer_id

---

## 🔐 Integridade e Segurança

- ✅ **Backup Completo**: Todos os 926 arquivos preservados
- ✅ **Estrutura Mantida**: Diretórios e hierarquias intactas
- ✅ **Dados Normalizados**: CSVs com headers, formatação padrão
- ✅ **UUIDs Aplicados**: Registros com customer_id único
- ✅ **Tamanho Controlado**: 719 MB (comprimível se necessário)

---

## 🚀 Próximos Passos

1. **Análise de Dados**: Executar validações de integridade
2. **Importação**: Carregar dados para Supabase via scripts em `normalizacao_clientes/`
3. **Integração**: Conectar backend web com dados normalizados
4. **Versionamento**: Rastrear alterações em Git local (normalizacao_clientes)

---

## 📋 Referência de Localização

```
D:/projetos/
├── carne_facil/                         # Repo GitHub (frontend)
│   ├── 2_crm_web/                      # App web
│   ├── 3_docs/                         # Documentação
│   └── README.md                       # Atualizado 2025-11-12
│
├── normalizacao_clientes/               # Workspace local
│   ├── app/                            # Backend normalização
│   ├── scripts/                        # ETL scripts
│   ├── dados_processados/              # Dados normalizados
│   ├── backup_from_repo/               # ← Este backup
│   │   └── 20251112_123539/            # ← Localização atual
│   └── .git/                           # Git local
│
└── SIS_Vendas/                          # Preparação novo repo
    ├── LEIA_PRIMEIRO.md
    ├── SIS_VENDAS_SETUP.md
    └── [estrutura frontend/backend - a adicionar]
```

---

**Gerado**: 2025-11-12 T 12:35:39 UTC
**Versão**: 1.0
**Status**: ✅ Backup Seguro e Completo
