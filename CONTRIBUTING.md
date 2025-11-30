# Contribuindo

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
