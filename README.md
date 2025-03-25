# SITAI - Sistema de Catalogação de Escavações Arqueológicas

## Descrição
SITAI é um sistema CRUD (Create, Read, Update, Delete) desenvolvido para auxiliar pesquisadores na catalogação e gestão de dados de escavações arqueológicas relacionadas a antigas comunidades indígenas da Amazônia. O sistema permite catalogar pontos de escavação com suas coordenadas geográficas, tipos de artefatos, descrições detalhadas e outros dados relevantes.

## Funcionalidades
- **Cadastrar** novos pontos de escavação com informações detalhadas
- **Listar** todos os pontos cadastrados com opções de ordenação
- **Atualizar** informações de pontos existentes
- **Remover** registros obsoletos ou incorretos
- **Pesquisar** pontos com filtros por diferentes campos

## Tecnologias Utilizadas
- **Python**: Linguagem de programação principal
- **Streamlit**: Framework para criação da interface web
- **SQLite**: Banco de dados para persistência dos dados
- **Pandas**: Manipulação e análise de dados

## Estrutura de Dados
Cada ponto de escavação contém:
- ID único
- Tipo de ponto (cabana, utensílio, artefato, etc.)
- Coordenadas geográficas (latitude, longitude)
- Altitude
- Sistema de referência (SRID)
- Descrição detalhada
- Data da descoberta
- Responsável pelo registro

## Instruções de Instalação e Execução

### Pré-requisitos
- Python 3.7 ou superior instalado
- Pip (gerenciador de pacotes do Python)

### Instalação
1. Clone este repositório:
   ```
   git clone [URL_DO_REPOSITÓRIO]
   ```

2. Navegue até a pasta do projeto:
   ```
   cd sitai
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

### Execução

#### No Windows:
Execute o arquivo batch incluído:
```
run.bat
```

Ou execute diretamente:
```
python -m streamlit run app.py
```

#### No Linux/Mac:
```
python -m streamlit run app.py
```

Se o comando acima não funcionar, tente:
```
python3 -m streamlit run app.py
```

## Como Usar
1. **Listar Pontos**: Visualize todos os pontos cadastrados e seus detalhes
2. **Cadastrar Novo Ponto**: Adicione novos registros com todas as informações necessárias
3. **Atualizar Ponto**: Edite as informações de um ponto existente
4. **Remover Ponto**: Exclua pontos que não são mais necessários
5. **Pesquisar**: Busque pontos específicos por critérios como tipo, descrição ou responsável

## Persistência de Dados
Todos os dados são armazenados em um banco de dados SQLite local, garantindo que as informações permaneçam disponíveis entre diferentes execuções do programa.

---

Desenvolvido por Matheus para o Grupo de Pesquisa Arqueológica da Amazônia
