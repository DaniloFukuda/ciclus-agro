# Ciclus Agro

Sistema operacional para equipes do agronegócio que centraliza interações pelo WhatsApp, controle de RDV/despesas, visitas técnicas e relatórios. O projeto combina automação conversacional, painel web e persistência local para apoiar o registro auditável de atividades de campo.

> **Status:** MVP operacional em evolução. A aplicação possui testes automatizados e documentação de deploy para VPS; antes de uso produtivo, revise controle de acesso, dados pessoais, backup e retenção conforme o ambiente.

## Problema resolvido

Rotinas de campo normalmente chegam por mensagens, mídias e anotações dispersas. O Ciclus Agro transforma esses registros em fluxos persistidos e consultáveis:

- despesas e comprovantes de RDV;
- visitas técnicas com dados da propriedade, descrição, observações e localização;
- fotos, vídeos e comentários vinculados a visitas;
- relatórios para acompanhamento administrativo e técnico.

## Funcionalidades

### Automação via WhatsApp

- Webhook compatível com a WhatsApp Cloud API.
- Menus e fluxos conversacionais persistidos para RDV e visitas técnicas.
- Recebimento de mensagens, documentos, imagens, localização, áudios e mídias de visita.
- Controle de deduplicação e tratamento de falhas de mídia.
- Prévia e entrega de relatórios no canal quando autorizadas pelo fluxo.

### RDV e despesas

- Registro de despesas, comprovantes, categoria, colaborador e status de revisão.
- Painel web para consulta, filtros, aprovação e rejeição.
- Exportações CSV e relatórios semanais/mensais em Excel e PDF.

### Visitas técnicas

- Abertura e acompanhamento de visitas pelo WhatsApp.
- Dados de propriedade, responsável, área, safra, localização, descrição e observações.
- Fotos e vídeos vinculados à visita, com comentários ou legendas opcionais.
- Coordenadas GPS e referências de localização quando disponíveis.
- Hub de revisão, prévia sob demanda e finalização confirmada.
- Relatório técnico em PDF e exportação de visitas em Excel.

### Painel e processamento documental legado

- Aplicação FastAPI com health check, painel de RDV e telas administrativas.
- O repositório preserva fluxos históricos de upload e processamento de documentos para compatibilidade e aprendizado; eles não representam o foco principal atual do produto.

## Arquitetura

```text
WhatsApp Cloud API                 Painel web
        │                              │
        └──── webhook FastAPI ─────────┘
                       │
          roteamento de fluxos e serviços
          ├── RDV / despesas
          ├── Visitas técnicas e mídias
          ├── Relatórios PDF e Excel
          └── Processamento documental legado
                       │
             SQLite + armazenamento local
```

## Stack

- **Python** e **FastAPI**
- **SQLite** para persistência local
- **WhatsApp Cloud API** para mensageria e mídia
- **ReportLab** para relatórios PDF
- **OpenPyXL** para relatórios Excel
- **Pytest** para testes automatizados
- **Uvicorn**, **Nginx** e **systemd** para a arquitetura documentada de VPS

## Módulos principais

| Módulo | Responsabilidade | Pontos de entrada |
|---|---|---|
| Aplicação web | Health check, telas administrativas, RDV e exportações | `web_upload.py` |
| WhatsApp | Verificação de webhook, recebimento e roteamento de mensagens | `api_whatsapp.py` |
| RDV | Despesas, comprovantes, revisão e relatórios | `services/rdv_service.py` |
| Visitas técnicas | Fluxo, persistência, mídia, localização e histórico | `services/visitas_service.py` e serviços relacionados |
| Relatórios | PDF de visita; Excel/PDF de RDV; Excel de visitas | `services/*_pdf_service.py`, `services/*_excel_service.py` |
| Persistência | Banco SQLite e armazenamento de arquivos | `core/` e `data/` |

## Fluxos operacionais

### WhatsApp

1. A Meta envia eventos para `GET`/`POST /webhook/whatsapp`.
2. O sistema valida e roteia a mensagem conforme o contexto persistido.
3. O módulo de RDV, visita técnica ou processamento documental recebe a entrada.
4. Dados e referências de mídia são persistidos no SQLite e no armazenamento configurado.
5. O usuário recebe a próxima orientação, a confirmação ou o relatório aplicável.

### RDV

1. O colaborador registra uma despesa e, quando aplicável, envia o comprovante.
2. O fluxo coleta valor e categoria, mantendo o lançamento para revisão.
3. A equipe consulta e revisa o lançamento no painel.
4. Relatórios semanais e mensais podem ser exportados em Excel ou PDF.

### Visitas técnicas

1. O técnico inicia uma visita pelo WhatsApp.
2. O fluxo registra dados da propriedade, área, localização, descrição e observações conforme informados.
3. Fotos, vídeos, comentários e coordenadas podem ser anexados à visita persistida.
4. O hub de revisão permite corrigir dados, administrar mídias e gerar prévia explícita.
5. Após confirmação, o sistema gera o relatório final em PDF.

## Relatórios

- **Visita técnica:** relatório PDF com dados da visita, localização, descrição, observações, registro fotográfico e referências de vídeo.
- **Visitas técnicas:** planilha Excel para consulta e consolidação.
- **RDV:** exportações CSV, planilhas Excel e relatórios PDF semanais/mensais.

## Como executar localmente

### Pré-requisitos

- Python 3.11 ou compatível
- Ambiente virtual Python
- Dependências de sistema exigidas opcionalmente pelos recursos de OCR, áudio ou mídia

```bash
python -m venv .venv
source .venv/Scripts/activate  # Git Bash no Windows
python -m pip install -r requirements.txt
python -m uvicorn web_upload:app --reload --port 8000
```

Em PowerShell, a ativação do ambiente virtual é:

```powershell
.\.venv\Scripts\Activate.ps1
```

A aplicação fica disponível, por padrão, em `http://127.0.0.1:8000`.

## Configuração

Copie `.env.example` para `.env` e preencha as variáveis necessárias no ambiente seguro. Os principais grupos de configuração são:

- credenciais e IDs da WhatsApp Cloud API;
- URL pública para webhooks e links de mídia;
- limites de áudio, foto, vídeo e visitas;
- armazenamento de objetos opcional;
- recursos opcionais de transcrição e assistência.

**Nunca versione `.env`, tokens, IDs de conta, bancos SQLite, uploads, backups ou documentos reais.**

## Testes

```bash
python -m pytest -q --basetemp=C:/Users/SEU_USUARIO/AppData/Local/Temp/ciclus_pytest
```

O `--basetemp` externo evita misturar artefatos temporários de teste com o repositório. Consulte `pytest.ini` para a configuração base da suíte.

## Segurança e privacidade

Este projeto pode tratar dados pessoais, financeiros e operacionais. Antes de publicar ou implantar:

- mantenha tokens, senhas, chaves privadas e arquivos `.env` fora do Git;
- não versione bancos SQLite, uploads, comprovantes, fotos, vídeos, PDFs, planilhas ou backups reais;
- proteja o painel administrativo com autenticação adequada;
- mantenha apenas o webhook necessário exposto publicamente;
- aplique política de backups, retenção e recuperação testada;
- revise `git status --ignored`, `git diff --check` e os arquivos staged antes de cada push.

## Deploy em VPS

A arquitetura de referência usa FastAPI atrás de Nginx, gerenciado por systemd, com SQLite e uploads persistentes. Os guias operacionais estão em:

- [Guia de deploy](README_DEPLOY.md)
- [Deploy de Ciclus/RDV na VPS](docs/deploy-ciclus-vps.md)
- [Operação e recuperação](docs/operacao-ciclus-rdv.md)

Os exemplos de Nginx e systemd são somente modelos e não devem conter credenciais, certificados ou dados reais.

## Estrutura do projeto

```text
agents/       Fluxos e agentes históricos de processamento documental
core/         Persistência SQLite, núcleo e armazenamento
services/     Regras de RDV, visitas, mídia, relatórios e integrações
tests/        Testes automatizados
docs/         Operação e deploy
deploy*/      Exemplos de infraestrutura para VPS
scripts/      Diagnósticos e ferramentas operacionais
web_upload.py Aplicação FastAPI e painel web
api_whatsapp.py Webhook e fluxos da WhatsApp Cloud API
```

## Status e próximos passos

O foco atual é a evolução controlada dos módulos de RDV e visitas técnicas, preservando compatibilidade e cobertura automatizada. Próximos passos de produto devem incluir validação com dados reais autorizados, endurecimento de autenticação/autorização, governança de dados e revisão periódica da infraestrutura de produção.

## Documentação histórica

O projeto nasceu de um MVP de processamento documental. Código e dependências históricas — como leitura de documentos, QR Code e OCR — foram preservados para compatibilidade e não devem ser removidos apenas pelo nome. Alterações nesses componentes exigem rastreamento de chamadas, rotas e testes antes de qualquer descontinuação.