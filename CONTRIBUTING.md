# Contribuindo para o SITAI

Agradecemos pelo seu interesse em contribuir com o SITAI! Este documento fornece diretrizes para contribuir com o projeto.

## Código de Conduta

Por favor, leia nosso [Código de Conduta](CODE_OF_CONDUCT.md) antes de contribuir.

## Como Contribuir

### Reportando Bugs

Se você encontrou um bug, por favor, crie uma issue usando o modelo de bug report fornecido. Inclua:

1. Uma descrição clara do bug
2. Passos para reproduzir o problema
3. Comportamento esperado vs. comportamento observado
4. Capturas de tela, se aplicável
5. Informações sobre seu ambiente (SO, versão do Python, etc.)

### Sugerindo Melhorias

Para sugerir melhorias:

1. Crie uma issue usando o modelo de feature request
2. Descreva claramente a funcionalidade desejada
3. Explique por que essa melhoria seria útil para o projeto

### Enviando Pull Requests

1. Bifurque (fork) o repositório
2. Crie um branch para sua alteração (`git checkout -b feature/minha-nova-funcionalidade`)
3. Implemente suas alterações
4. Adicione testes para suas alterações, se aplicável
5. Execute os testes para garantir que estão passando
6. Faça commit das suas alterações (`git commit -am 'Adiciona nova funcionalidade'`)
7. Faça push para o branch (`git push origin feature/minha-nova-funcionalidade`)
8. Abra um Pull Request

## Padrões de Código

- Siga o PEP 8 para estilo de código Python
- Use docstrings no estilo Google para documentação
- Escreva testes para novas funcionalidades
- Mantenha a cobertura de testes alta

## Processo de Desenvolvimento

1. Escolha uma issue para trabalhar
2. Implemente suas alterações
3. Escreva/atualize testes
4. Atualize a documentação
5. Envie um Pull Request
6. Aborde quaisquer revisões de código

## Estrutura do Projeto

```
sitai/                # Código-fonte principal
├── __init__.py       # Torna o diretório um pacote Python
├── models/           # Modelos de dados
├── database/         # Operações de banco de dados
└── ui/               # Componentes da interface
```

## Setup de Desenvolvimento

1. Clone o repositório
2. Instale as dependências de desenvolvimento:
   ```
   pip install -r requirements-dev.txt
   ```
3. Configure os hooks de pré-commit:
   ```
   pre-commit install
   ```

## Executando Testes

```
pytest
```

## Linting e Formatação

```
# Verificar estilo de código
flake8 sitai tests

# Formatar código
black sitai tests
```

Agradecemos sua contribuição!
