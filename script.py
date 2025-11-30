
from pathlib import Path

base_dir = Path("notebook-logic-analyzer")

# README.md completo e profissional para GitHub
readme_content = """# 🔬 Notebook Logic Analyzer

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Raspberry%20Pi%203B-red?style=flat-square&logo=raspberry-pi" alt="Platform">
  <img src="https://img.shields.io/badge/Language-C%20%7C%20Python-blue?style=flat-square" alt="Language">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square" alt="Status">
</p>

**Analisador lógico de baixo custo para diagnóstico de sequência de boot em placas-mãe de notebooks.**

Transforme seu Raspberry Pi 3B em uma ferramenta profissional de diagnóstico para identificar falhas em notebooks que não ligam, comparando a sequência de power com templates de referência.

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
- [Templates Disponíveis](#-templates-disponíveis)
- [Circuito de Proteção](#-circuito-de-proteção)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

---

## 🎯 Sobre o Projeto

Quando um notebook não liga, o problema geralmente está na **sequência de power** - a ordem em que os diferentes rails de tensão são ativados. Este projeto permite:

1. **Capturar** sinais digitais (EN, PG, PWROK) durante a tentativa de boot
2. **Exportar** para formato VCD (visualização no PulseView/sigrok)
3. **Comparar** automaticamente com sequências conhecidas de placas funcionando
4. **Diagnosticar** qual componente ou rail está falhando

### Por que usar?

| Método Tradicional | Com Este Projeto |
|-------------------|------------------|
| Multímetro manual, um ponto por vez | 16 canais simultâneos |
| Sem registro de timing | Captura com timestamps precisos |
| Experiência necessária para interpretar | Comparação automática com templates |
| Sem histórico | Salva capturas para análise posterior |

---

## ✨ Funcionalidades

- 📊 **Captura de 16 canais** simultâneos via GPIO
- ⚡ **Taxa de amostragem** configurável (100kHz - 10MHz)
- 🎯 **Trigger configurável** (rising/falling edge)
- 📁 **Export VCD** compatível com PulseView, GTKWave, sigrok
- 🔍 **Análise automática** comparando com templates
- 📝 **Templates prontos** para Dell, Lenovo, HP e outros
- 🛠️ **Gerenciador de templates** para adicionar novos modelos
- 💡 **Diagnóstico inteligente** com sugestões de reparo

---

## 📦 Requisitos

### Hardware

- **Raspberry Pi 3B** (ou superior)
- **Circuito de proteção** para GPIOs (ver seção específica)
- **Garras/pontas de prova** para conexão com test points
- **Jumpers** e protoboard

### Software

- Raspberry Pi OS (32 ou 64-bit)
- Python 3.7+
- GCC (build-essential)
- NumPy

---

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/notebook-logic-analyzer.git
cd notebook-logic-analyzer
```

### 2. Execute o setup

```bash
chmod +x setup.sh
sudo ./setup.sh
```

### 3. Verifique a instalação

```bash
python3 cli.py templates
```

---

## 📖 Como Usar

### Capturar sequência de boot

```bash
# Conecte as pontas de prova e execute:
sudo python3 cli.py capture -o captures/minha_placa.bin

# Aguarde o trigger (pressione power no notebook)
```

### Exportar para visualização

```bash
python3 cli.py export \\
  -i captures/minha_placa.bin \\
  -o captures/minha_placa.vcd \\
  -t src/templates/dell_g15_5511_la_k452p.json
```

### Analisar e comparar

```bash
python3 cli.py analyze \\
  -i captures/minha_placa.bin \\
  -t src/templates/dell_g15_5511_la_k452p.json
```

### Exemplo de saída

```
============================================================
ANÁLISE DE SEQUÊNCIA DE BOOT
============================================================

✅ PWRBTN# (0.0ms): OK
✅ 3VALW_EN (2.1ms): OK (esperado 2±2ms)
✅ 3VALW_PG (5.3ms): OK (esperado 5±3ms)
❌ 5VALW_PG: AUSENTE

🔍 DIAGNÓSTICO:
   → Primeiro sinal ausente: 5VALW_PG
   → Verificar: buck converter 5V, fusível, carga excessiva
============================================================
```

---

## 📋 Templates Disponíveis

| Fabricante | Modelo | Placa | Arquivo |
|------------|--------|-------|---------|
| Dell | G15 5511 / Alienware M15 R6 | LA-K452P | `dell_g15_5511_la_k452p.json` |
| Generic | Notebook genérico | - | `generic_notebook.json` |

### Adicionar novo template

```bash
# Modo interativo
python3 template_manager.py add

# Ou copie um existente
python3 template_manager.py copy dell_g15_5511_la_k452p.json meu_modelo.json
```

---

## ⚡ Circuito de Proteção

> ⚠️ **IMPORTANTE:** Nunca conecte GPIOs do Raspberry Pi diretamente ao notebook!

### Componentes necessários (8 canais)

| Qtd | Componente | Valor |
|-----|------------|-------|
| 8x | Resistor | 220Ω 1/4W |
| 4x | Diodo Schottky | BAT54S |
| 1x | Protoboard | 400 pontos |
| 8x | Garra jacaré | Mini |

### Esquema básico por canal

```
Notebook ──[220Ω]──┬── Raspberry Pi GPIO
                   │
            ┌──────┴──────┐
            │   BAT54S    │
           GND          3.3V
```

Para sinais 1.8V, adicione level shifter **TXS0108E**.

---

## 🔌 Pinagem GPIO

| Canal | GPIO BCM | Pino | Sinal Sugerido |
|-------|----------|------|----------------|
| CH0 | GPIO17 | 11 | PWRBTN# |
| CH1 | GPIO18 | 12 | 3V3_EN |
| CH2 | GPIO27 | 13 | 3V3_PG |
| CH3 | GPIO22 | 15 | 5V_EN |
| CH4 | GPIO23 | 16 | 5V_PG |
| CH5 | GPIO24 | 18 | VCORE_EN |
| CH6 | GPIO25 | 22 | VCORE_PG |
| CH7 | GPIO4 | 7 | SYS_PWROK |

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Especialmente:

- 📝 **Novos templates** para diferentes modelos de notebooks
- 🐛 **Bug fixes** e melhorias de código
- 📚 **Documentação** e tutoriais
- 🌐 **Traduções**

### Como contribuir

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovoTemplate`)
3. Commit suas mudanças (`git commit -m 'Add template Lenovo T480'`)
4. Push para a branch (`git push origin feature/NovoTemplate`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🙏 Agradecimentos

- Projetos open-source: [Panalyzer](https://github.com/richardghirst/Panalyzer), [sigrok](https://sigrok.org/)
- Comunidade de reparo de notebooks
- Contribuidores de esquemáticos

---

<p align="center">
  Feito com ❤️ para a comunidade de reparo de eletrônicos
</p>
"""

with open(base_dir / "README.md", "w", encoding="utf-8") as f:
    f.write(readme_content)

print("✅ README.md criado")

# LICENSE - MIT
license_content = """MIT License

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

with open(base_dir / "LICENSE", "w", encoding="utf-8") as f:
    f.write(license_content)

print("✅ LICENSE (MIT) criado")

# .gitignore atualizado
gitignore_content = """# Binários compilados
*.o
*.so
*.bin
src/capture/capture

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
env/
venv/
ENV/

# Capturas (dados do usuário)
captures/*.bin
captures/*.vcd

# IDE e editores
.vscode/
.idea/
*.swp
*.swo
*~
.project
.pydevproject
.settings/

# Sistema operacional
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Arquivos temporários
*.tmp
*.temp
.cache/
"""

with open(base_dir / ".gitignore", "w", encoding="utf-8") as f:
    f.write(gitignore_content)

print("✅ .gitignore atualizado")

# CONTRIBUTING.md
contributing_content = """# Contribuindo para o Notebook Logic Analyzer

Obrigado por considerar contribuir! Este documento explica como você pode ajudar.

## 📝 Tipos de Contribuição

### 1. Templates de Novos Modelos

A forma mais valiosa de contribuir é adicionar templates para modelos de notebooks que você tem acesso.

**Como fazer:**

1. Obtenha o esquemático do notebook
2. Identifique os sinais de power sequence (EN, PG, PWROK)
3. Use o `template_manager.py` para criar o template
4. Teste com uma placa funcionando para calibrar os tempos
5. Envie um Pull Request

**Formato do arquivo:**
```
src/templates/[fabricante]_[modelo]_[placa].json
```

### 2. Correções de Bugs

Se encontrar um bug:

1. Verifique se já não foi reportado nas Issues
2. Crie uma Issue descrevendo o problema
3. Se souber corrigir, envie um Pull Request

### 3. Melhorias de Código

- Otimizações de performance
- Novos recursos
- Melhorias na interface

### 4. Documentação

- Correções de erros
- Traduções
- Tutoriais e exemplos

## 🔄 Processo de Pull Request

1. Fork o repositório
2. Clone seu fork: `git clone https://github.com/seu-user/notebook-logic-analyzer`
3. Crie uma branch: `git checkout -b minha-feature`
4. Faça suas alterações
5. Teste localmente
6. Commit: `git commit -m "Descrição clara da mudança"`
7. Push: `git push origin minha-feature`
8. Abra um Pull Request

## 📋 Checklist para Templates

- [ ] Nome do arquivo segue o padrão
- [ ] Campos obrigatórios preenchidos (name, manufacturer, model, channels)
- [ ] Sequência de eventos definida
- [ ] Tempos aproximados (podem ser ajustados depois)
- [ ] Validado com `python3 template_manager.py validate`

## 💬 Dúvidas?

Abra uma Issue com a tag `question`.

Obrigado por contribuir! 🙏
"""

with open(base_dir / "CONTRIBUTING.md", "w", encoding="utf-8") as f:
    f.write(contributing_content)

print("✅ CONTRIBUTING.md criado")
