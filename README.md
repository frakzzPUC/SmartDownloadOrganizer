# 🗂️ Smart Download Organizer

<p align="center">
  <strong>Organize sua pasta Downloads automaticamente com uma interface moderna</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-orange" alt="CustomTkinter">
  <img src="https://img.shields.io/badge/Monitoring-Watchdog-purple" alt="Watchdog">
</p>

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

<p align="center">
  Feito com ❤️ em Python
</p>
