# Guia de Uso do SITAI

Este documento fornece instruções detalhadas sobre como usar o Sistema de Catalogação de Escavações Arqueológicas (SITAI).

## Sumário

1. [Iniciando o Sistema](#iniciando-o-sistema)
2. [Cadastro de Pontos](#cadastro-de-pontos)
3. [Visualização de Pontos](#visualização-de-pontos)
4. [Atualização de Pontos](#atualização-de-pontos)
5. [Remoção de Pontos](#remoção-de-pontos)
6. [Pesquisa](#pesquisa)
7. [Dicas e Solução de Problemas](#dicas-e-solução-de-problemas)

## Iniciando o Sistema

Para iniciar o SITAI, você tem duas opções:

### Windows
Execute o arquivo `run.bat` na pasta raiz do projeto, ou abra um terminal e execute:

```
python -m streamlit run app.py
```

### Linux/Mac
Abra um terminal na pasta do projeto e execute:

```
python -m streamlit run app.py
```

Após a execução, o sistema abrirá automaticamente em seu navegador padrão.

## Cadastro de Pontos

Para cadastrar um novo ponto de escavação:

1. No menu lateral, clique em "Cadastrar Novo Ponto".
2. Preencha os campos obrigatórios:
   - **Tipo de Ponto**: Selecione o tipo que melhor descreve o achado
   - **Latitude e Longitude**: Coordenadas geográficas do ponto (em graus decimais)
   - **Altitude**: Altura em metros acima do nível do mar
   - **Sistema de Referência**: Padrão geodésico utilizado (ex: WGS84)
   - **Descrição detalhada**: Informações sobre o achado
   - **Responsável**: Nome do pesquisador responsável pelo registro
   - **Data da descoberta**: Data em que o ponto foi encontrado

3. Clique em "Cadastrar Ponto" para salvar as informações.

## Visualização de Pontos

Para visualizar pontos cadastrados:

1. No menu lateral, clique em "Listar Pontos".
2. Você verá uma tabela com todos os pontos cadastrados.
3. Use o seletor "Ordenar por" para alterar a ordem de exibição dos pontos.
4. Para ver detalhes de um ponto específico, digite seu ID no campo abaixo da tabela e clique em "Ver Detalhes".

## Atualização de Pontos

Para atualizar informações de um ponto existente:

1. No menu lateral, clique em "Atualizar Ponto".
2. Digite o ID do ponto que deseja atualizar e clique em "Carregar Dados".
3. Os dados atuais do ponto serão carregados no formulário.
4. Faça as alterações necessárias nos campos.
5. Clique em "Atualizar Ponto" para salvar as mudanças.

## Remoção de Pontos

Para remover um ponto do sistema:

1. No menu lateral, clique em "Remover Ponto".
2. Digite o ID do ponto que deseja remover e clique em "Buscar".
3. Verifique os dados do ponto para confirmar que é o correto.
4. Clique em "Confirmar Exclusão" para remover permanentemente o ponto.

## Pesquisa

Para pesquisar pontos específicos:

1. No menu lateral, clique em "Pesquisar".
2. Digite um termo de pesquisa no campo apropriado.
3. Opcionalmente, selecione um campo específico para restringir a pesquisa.
4. Escolha a ordem de exibição dos resultados.
5. Clique em "Pesquisar" para visualizar os pontos que correspondem à sua busca.

## Dicas e Solução de Problemas

### Coordenadas Geográficas
- As coordenadas devem estar em formato decimal (ex: -3.1190, não 3° 7' 08" S)
- Latitude varia de -90 a 90 (negativo para Sul, positivo para Norte)
- Longitude varia de -180 a 180 (negativo para Oeste, positivo para Leste)

### Problemas Comuns

**Erro ao cadastrar ponto**: Verifique se todos os campos obrigatórios estão preenchidos.

**Ponto não aparece na listagem**: Tente atualizar a página clicando novamente em "Listar Pontos".

**Erro ao excluir ponto**: Verifique se o ID informado existe na base de dados.

**Erro ao iniciar o sistema**: Certifique-se de que todas as dependências estão instaladas corretamente.
