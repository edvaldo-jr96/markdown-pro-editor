# Markdown Pro Editor

Editor Markdown desktop (offline) para Linux Mint, com exportação PDF via WeasyPrint.

## Stack
- Python 3.10+
- Tkinter (GUI)
- markdown (parser)
- WeasyPrint (PDF)
- Pygments (syntax highlight)
- Pillow (imagens)
- watchdog (monitoramento opcional)

## Rodar localmente
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m markdown_pro.app
