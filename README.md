# Ciclus Agro

Sistema de automação operacional para equipes do agronegócio, com fluxos via WhatsApp, painel web, controle de RDV/despesas, visitas técnicas e relatórios.

O projeto reúne captura e organização de documentos, rotinas de campo e acompanhamento administrativo em serviços persistidos em SQLite.

## Funcionalidades

### WhatsApp e documentos

- Webhook compatível com a WhatsApp Cloud API.
- Recebimento de mensagens, imagens e documentos.
- Deduplicação por identificador de mensagem e hash de mídia.
- Processamento documental com QR Code e OCR complementar.
- Classificação de nota fiscal, recibo e comprovante.
- Fluxos e respostas automatizadas quando a integração está configurada.

### RDV e despesas

- Registro de despesas e comprovantes pelo painel e pelo WhatsApp.
- Categorias, colaboradores, status de revisão e filtros operacionais.
- Consultas por colaborador e período.
- Exportações CSV e relatórios semanais/mensais em Excel e PDF.

### Visitas técnicas

- Abertura e acompanhamento de visitas pelo WhatsApp.
- Dados de propriedade, responsável, área, safra, descrição e observações.
- Registro de localização e coordenadas quando disponíveis.
- Histórico persistido de visitas e comandos de consulta.
- Relatórios individuais em PDF e exportação em Excel.

### Painel web

- Aplicação FastAPI para upload, consulta, filtros, edição e revisão de documentos.
- Painel RDV para lançamento, acompanhamento e revisão de despesas.
- Health check e rotas auxiliares para operação controlada.

## Arquitetura

```text
WhatsApp Cloud API                 Painel web
        │                              │
        └──── webhook FastAPI ─────────┘
                       │
          serviços e regras de domínio
          ├── documentos e processamento
          ├── RDV / despesas
          ├── visitas técnicas
          └── relatórios PDF e Excel
                       │
                     SQLite
```

| Camada | Responsabilidade |
|---|---|
| `web_upload.py` | Aplicação FastAPI, painel web e rotas de RDV |
| `api_whatsapp.py` | Verificação do webhook, recebimento e roteamento WhatsApp |
| `services/` | RDV, visitas, processamento documental e relatórios |
| `core/` | Persistência SQLite, armazenamento e núcleo de processamento |
| `agents/` | Agentes determinísticos de documentos |
| `tests/` | Cobertura automatizada de regras e integrações |

## Stack

- Python
- FastAPI e Uvicorn
- SQLite
- WhatsApp Cloud API
- OpenCV, PyTesseract, PyMuPDF e QR Code
- ReportLab e OpenPyXL
- Pytest

## Executar localmente

```bash
python -m venv .venv
source .venv/Scripts/activate  # Git Bash no Windows
python -m pip install -r requirements.txt
python -m uvicorn web_upload:app --reload --port 8000
```

A aplicação fica disponível, por padrão, em `http://127.0.0.1:8000`.

## Configuração segura

Crie um `.env` local a partir de `.env.example` e mantenha credenciais apenas no ambiente privado. As configurações cobrem a WhatsApp Cloud API, a URL pública do webhook e opções operacionais de relatórios.

Nunca versione:

- `.env`, tokens, senhas ou chaves privadas;
- bancos SQLite, backups e logs operacionais;
- uploads, documentos, fotografias, PDFs ou planilhas reais;
- identificadores de clientes, telefones ou payloads de produção.

## Testes

```bash
python -m pytest -q --basetemp=C:/Users/SEU_USUARIO/AppData/Local/Temp/ciclus_pytest
```

## Deploy

A arquitetura documentada utiliza FastAPI atrás de Nginx, gerenciado por systemd, com SQLite e uploads persistentes. Consulte os guias públicos de [deploy](docs/deploy-ciclus-vps.md) e [operação](docs/operacao-ciclus-rdv.md) antes de qualquer instalação controlada.

Configurações, certificados, dados e credenciais de produção permanecem fora do repositório.
