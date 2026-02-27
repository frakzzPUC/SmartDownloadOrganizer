# 🗂️ Smart Download Organizer

<p align="center">
  <strong>Organize sua pasta Downloads automaticamente com uma interface moderna</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License">
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-orange" alt="CustomTkinter">
  <img src="https://img.shields.io/badge/Monitoring-Watchdog-purple" alt="Watchdog">
</p>

---

## 📖 Sobre o Projeto

O **Smart Download Organizer** é um aplicativo desktop que monitora a pasta Downloads em tempo real e move automaticamente os arquivos para subpastas organizadas por categoria (documentos, imagens, vídeos, código, etc.).

Desenvolvido com foco em **código limpo**, **arquitetura em camadas** e **boas práticas de engenharia de software** em Python.

---

## ✨ Funcionalidades

### MVP (Implementado)
- ✅ Monitoramento em tempo real da pasta Downloads (Watchdog)
- ✅ Classificação automática por extensão (20+ categorias)
- ✅ Criação automática de subpastas
- ✅ Renomeação inteligente para evitar conflitos de nome
- ✅ Log de atividades em tempo real na interface
- ✅ Proteção contra arquivos em download (`.crdownload`, `.part`)

### Avançado (Implementado)
- ✅ Regras personalizadas (substring e regex)
- ✅ Detecção de arquivos duplicados (hash MD5)
- ✅ Dashboard com estatísticas (total, hoje, semana, por categoria)
- ✅ Histórico completo com SQLite
- ✅ Interface moderna com CustomTkinter (tema escuro/claro)
- ✅ Configurações persistentes (JSON)
- ✅ Organização batch de arquivos existentes

---

## 🏗️ Arquitetura

O projeto segue uma **arquitetura em camadas** com separação clara de responsabilidades:

```
SmartDownloadOrganizer/
├── main.py                      # Entry point
├── requirements.txt             # Dependências
├── setup.py                     # Pacote instalável
│
├── src/
│   ├── ui/                      # 🎨 Camada de Apresentação
│   │   ├── app.py               #   Janela principal + orquestração
│   │   ├── dashboard.py         #   Cards de estatísticas
│   │   ├── log_viewer.py        #   Visualizador de logs
│   │   ├── rules_editor.py      #   Editor de regras personalizadas
│   │   └── settings_panel.py    #   Painel de configurações
│   │
│   ├── services/                # ⚙️ Camada de Lógica de Negócio
│   │   ├── file_monitor.py      #   Monitoramento com Watchdog
│   │   ├── file_organizer.py    #   Orquestração da organização
│   │   ├── rule_engine.py       #   Motor de regras personalizadas
│   │   └── duplicate_detector.py#   Detecção de duplicatas
│   │
│   ├── models/                  # 📊 Camada de Dados
│   │   ├── database.py          #   Gerenciador SQLite
│   │   └── file_record.py       #   Modelos de dados (dataclass)
│   │
│   └── utils/                   # 🔧 Utilitários
│       ├── config.py            #   Gerenciamento de configuração
│       ├── constants.py         #   Constantes e mapeamentos
│       ├── helpers.py           #   Funções auxiliares puras
│       └── logger.py            #   Setup de logging
│
└── tests/                       # 🧪 Testes Automatizados
    ├── test_file_organizer.py
    ├── test_rule_engine.py
    ├── test_duplicate_detector.py
    └── test_helpers.py
```

### Diagrama de Dependências

```
┌─────────────────────────────────────────┐
│              UI Layer (app.py)           │
│   dashboard | log_viewer | rules_editor │
└───────────────────┬─────────────────────┘
                    │
┌───────────────────▼─────────────────────┐
│          Services Layer                  │
│  file_monitor → file_organizer          │
│       rule_engine  |  duplicate_detector│
└───────────────────┬─────────────────────┘
                    │
┌───────────────────▼─────────────────────┐
│         Models Layer (database.py)       │
│     FileRecord  |  CustomRule           │
└───────────────────┬─────────────────────┘
                    │
┌───────────────────▼─────────────────────┐
│         Utils Layer                      │
│  config | constants | helpers | logger  │
└─────────────────────────────────────────┘
```

---

## 🚀 Como Executar

### Pré-requisitos
- Python 3.10 ou superior
- pip (gerenciador de pacotes)

### Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/yourusername/SmartDownloadOrganizer.git
cd SmartDownloadOrganizer

# 2. Crie um ambiente virtual
python -m venv venv

# 3. Ative o ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Execute o aplicativo
python main.py
```

### Executar Testes

```bash
pip install pytest
pytest tests/ -v
```

---

## 🎯 Como Funciona

### Monitoramento de Arquivos

O sistema usa a biblioteca **Watchdog** para observar eventos do sistema de arquivos:

```python
# Watchdog detecta criação/movimentação de arquivos
on_created(event)  →  agenda processamento com delay
on_moved(event)    →  agenda processamento com delay
```

### Proteção Contra Downloads Incompletos

```
Novo arquivo detectado
      │
      ▼
  É .crdownload/.part/.tmp? ──YES──▶ Ignora
      │ NO
      ▼
  Tamanho = 0 bytes? ──YES──▶ Ignora
      │ NO
      ▼
  Aguarda estabilidade (3 checks × 1s)
      │
      ▼
  Tamanho mudou? ──YES──▶ Aguarda mais
      │ NO
      ▼
  Processa o arquivo ✅
```

### Pipeline de Organização

```
Arquivo novo
    │
    ▼
 Validação (temp? vazio? oculto?)
    │
    ▼
 Espera estabilidade do tamanho
    │
    ▼
 Verifica duplicatas (hash MD5)
    │
    ▼
 Avalia regras personalizadas
    │ (se nenhuma regra match)
    ▼
 Classifica por extensão
    │
    ▼
 Cria subpasta se necessário
    │
    ▼
 Gera nome único (evita conflitos)
    │
    ▼
 Move arquivo + registra no SQLite
    │
    ▼
 Notifica a UI ✅
```

---

## 📂 Categorias Suportadas

| Categoria | Extensões |
|-----------|-----------|
| 📄 Documents | .pdf, .doc, .docx, .txt, .odt, .rtf |
| 🖼️ Images | .jpg, .png, .gif, .svg, .webp, .bmp |
| 🎬 Videos | .mp4, .avi, .mkv, .mov, .webm |
| 🎵 Music | .mp3, .wav, .flac, .aac, .ogg |
| 📦 Archives | .zip, .rar, .7z, .tar.gz |
| 💻 Code | .py, .js, .ts, .java, .html, .css |
| ⚙️ Executables | .exe, .msi, .sh, .dmg |
| 📊 Spreadsheets | .xls, .xlsx, .csv |
| 🎨 Design | .psd, .ai, .sketch, .fig |
| 📚 Ebooks | .epub, .mobi, .azw |
| ... | +10 categorias extras |

---

## ⚙️ Regras Personalizadas

Exemplos de regras que podem ser criadas pela interface:

| Nome | Padrão | Pasta Destino | Tipo |
|------|--------|---------------|------|
| Faturas | `invoice` | Finance | Substring |
| Currículos | `resume\|cv` | Career | Regex |
| Screenshots | `screenshot` | Screenshots | Substring |
| Boletos | `boleto` | Financeiro | Substring |
| Relatórios datados | `\d{4}-\d{2}` | Dated | Regex |

---

## 🧪 Testes

O projeto inclui testes unitários abrangentes:

```
tests/
├── test_helpers.py            # 12 testes - funções utilitárias
├── test_file_organizer.py     #  7 testes - organização de arquivos
├── test_rule_engine.py        #  7 testes - motor de regras
└── test_duplicate_detector.py #  3 testes - detecção de duplicatas
```

**Total: 29 testes** cobrindo os cenários críticos do sistema.

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Propósito |
|------------|-----------|
| **Python 3.10+** | Linguagem principal |
| **CustomTkinter** | Interface gráfica moderna |
| **Watchdog** | Monitoramento do sistema de arquivos |
| **SQLite3** | Banco de dados para histórico |
| **pathlib** | Manipulação de caminhos |
| **shutil** | Operações de movimentação de arquivos |
| **hashlib** | Hash para detecção de duplicatas |
| **dataclasses** | Modelos de dados tipados |
| **threading** | Processamento assíncrono de arquivos |
| **pytest** | Framework de testes |

---

## 📝 Decisões Técnicas

1. **Watchdog vs Polling**: Watchdog usa eventos nativos do SO (inotify/FSEvents/ReadDirectoryChanges) em vez de polling, sendo muito mais eficiente.

2. **Threading para estabilidade**: Cada arquivo é processado em uma thread separada com delay, evitando travar a UI e garantindo que downloads terminem.

3. **SQLite para persistência**: Leve, sem necessidade de servidor, perfeito para uso desktop. Row factory para acesso por nome de coluna.

4. **Dataclasses como modelos**: Type hints + imutabilidade parcial + representação automática. Mais pythônico que dicts simples.

5. **Injeção de dependência**: `FileOrganizer` recebe config, database e callback por construtor, facilitando testes e desacoplamento.

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

---

<p align="center">
  Feito com ❤️ em Python
</p>
