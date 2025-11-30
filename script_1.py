
from pathlib import Path
import zipfile
import os

# Criar diretório base
base_dir = Path("notebook-logic-analyzer")
base_dir.mkdir(parents=True, exist_ok=True)
(base_dir / "src" / "templates").mkdir(parents=True, exist_ok=True)
(base_dir / "src" / "capture").mkdir(parents=True, exist_ok=True)
(base_dir / "src" / "analysis").mkdir(parents=True, exist_ok=True)
(base_dir / "captures").mkdir(exist_ok=True)

# README.md
readme = """# 🔬 Notebook Logic Analyzer

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Raspberry%20Pi%203B-red?style=flat-square&logo=raspberry-pi" alt="Platform">
  <img src="https://img.shields.io/badge/Language-C%20%7C%20Python-blue?style=flat-square" alt="Language">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License">
</p>

**Analisador lógico de baixo custo para diagnóstico de sequência de boot em placas-mãe de notebooks.**

Transforme seu Raspberry Pi 3B em uma ferramenta profissional para identificar falhas em notebooks que não ligam.

---

## 🎯 Sobre o Projeto

Quando um notebook não liga, o problema geralmente está na **sequência de power**. Este projeto permite:

- **Capturar** 16 canais simultâneos de sinais digitais (EN, PG, PWROK)
- **Exportar** para formato VCD (PulseView/sigrok)
- **Comparar** automaticamente com templates de referência
- **Diagnosticar** qual componente está falhando

## ✨ Funcionalidades

- 📊 Captura de 16 canais via GPIO
- ⚡ Taxa de amostragem até 10MHz
- 🎯 Trigger configurável (rising/falling)
- 📁 Export VCD compatível com PulseView
- 🔍 Análise automática com templates
- 💡 Diagnóstico inteligente

## 📦 Requisitos

### Hardware
- Raspberry Pi 3B (ou superior)
- Circuito de proteção para GPIOs
- Garras/pontas de prova

### Software
- Raspberry Pi OS
- Python 3.7+
- GCC

## 🚀 Instalação

```bash
git clone https://github.com/seu-usuario/notebook-logic-analyzer.git
cd notebook-logic-analyzer
chmod +x setup.sh
sudo ./setup.sh
```

## 📖 Como Usar

### Capturar
```bash
sudo python3 cli.py capture -o captures/placa.bin
```

### Exportar VCD
```bash
python3 cli.py export -i captures/placa.bin -o captures/placa.vcd -t src/templates/dell_g15_5511_la_k452p.json
```

### Analisar
```bash
python3 cli.py analyze -i captures/placa.bin -t src/templates/dell_g15_5511_la_k452p.json
```

### Exemplo de saída
```
✅ PWRBTN# (0.0ms): OK
✅ 3VALW_EN (2.1ms): OK
✅ 3VALW_PG (5.3ms): OK
❌ 5VALW_PG: AUSENTE

🔍 DIAGNÓSTICO:
   → Verificar: buck converter 5V, fusível
```

## 📋 Templates Disponíveis

| Fabricante | Modelo | Placa | Arquivo |
|------------|--------|-------|---------|
| Dell | G15 5511 / Alienware M15 R6 | LA-K452P | `dell_g15_5511_la_k452p.json` |

### Adicionar novo template
```bash
python3 template_manager.py add
```

## ⚡ Circuito de Proteção

> ⚠️ **NUNCA** conecte GPIOs diretamente ao notebook!

### Componentes (8 canais)
- 8x Resistor 220Ω
- 4x BAT54S (diodo Schottky)
- Level shifter TXS0108E (para sinais 1.8V)

### Esquema
```
Notebook ──[220Ω]──┬── RPi GPIO
                   │
            BAT54S (para 3.3V e GND)
```

## 🔌 Pinagem GPIO

| Canal | GPIO | Pino | Sinal |
|-------|------|------|-------|
| CH0 | 17 | 11 | PWRBTN# |
| CH1 | 18 | 12 | 3V3_EN |
| CH2 | 27 | 13 | 3V3_PG |
| CH3 | 22 | 15 | 5V_EN |
| CH4 | 23 | 16 | 5V_PG |
| CH5 | 24 | 18 | VCORE_EN |
| CH6 | 25 | 22 | VCORE_PG |
| CH7 | 4 | 7 | SYS_PWROK |

## 🤝 Contribuindo

Contribuições são bem-vindas! Especialmente **templates de novos modelos**.

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovoTemplate`)
3. Commit (`git commit -m 'Add template'`)
4. Push (`git push origin feature/NovoTemplate`)
5. Abra um Pull Request

## 📄 Licença

MIT License - veja [LICENSE](LICENSE)

---

<p align="center">Feito com ❤️ para a comunidade de reparo</p>
"""

(base_dir / "README.md").write_text(readme, encoding="utf-8")
print("✅ README.md")

# LICENSE
license_mit = """MIT License

Copyright (c) 2025 Notebook Logic Analyzer Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
(base_dir / "LICENSE").write_text(license_mit, encoding="utf-8")
print("✅ LICENSE")

# .gitignore completo
gitignore = """# Binários
*.o
*.bin
src/capture/capture

# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
venv/
env/

# Capturas do usuário
captures/*.bin
captures/*.vcd

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
"""
(base_dir / ".gitignore").write_text(gitignore, encoding="utf-8")
print("✅ .gitignore")

# CONTRIBUTING.md
contributing = """# Contribuindo

## Templates de Novos Modelos

A melhor forma de contribuir é adicionar templates para notebooks que você tem acesso.

1. Obtenha o esquemático
2. Identifique sinais de power sequence
3. Use `python3 template_manager.py add`
4. Teste com placa funcionando
5. Envie Pull Request

## Pull Requests

1. Fork o repositório
2. Crie branch: `git checkout -b feature/nome`
3. Commit: `git commit -m "Descrição"`
4. Push: `git push origin feature/nome`
5. Abra PR

## Checklist para Templates

- [ ] Nome segue padrão: `fabricante_modelo_placa.json`
- [ ] Campos obrigatórios preenchidos
- [ ] Validado: `python3 template_manager.py validate arquivo.json`

Obrigado! 🙏
"""
(base_dir / "CONTRIBUTING.md").write_text(contributing, encoding="utf-8")
print("✅ CONTRIBUTING.md")

print("\n✅ Arquivos do GitHub criados!")
