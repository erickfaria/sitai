import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys
import locale
from typing import cast

# Configurar locale para português brasileiro
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except locale.Error:
        st.warning("Não foi possível configurar o locale para português brasileiro. Usando o padrão do sistema.")

# Configurações do Streamlit
st.set_page_config(
    page_title="SITAI - Sistema de Catalogação",
    page_icon="🏺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Adiciona o diretório atual ao sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Verifica se os módulos estão disponíveis no caminho diretamente ou na pasta sitai
try:
    from sitai.models import ExcavationPoint
    import database as db
except ModuleNotFoundError:
    try:
        from sitai.models import ExcavationPoint
        import sitai.database as db
    except ModuleNotFoundError:
        st.error("Não foi possível importar os módulos necessários. Verifique a estrutura do projeto.")
        st.stop()

# Inicializa o banco de dados
db.init_db()

# Função auxiliar para formatação de data


def format_date(date_obj):
    if date_obj:
        return date_obj.strftime('%d/%m/%Y')
    return ""


def main():
    st.title("SITAI - Sistema de Catalogação de Escavações Arqueológicas")
    st.sidebar.title("Navegação")

    # Menu de navegação
    menu = st.sidebar.radio(
        "Escolha uma opção:",
        ["Listar Pontos", "Cadastrar Novo Ponto", "Atualizar Ponto", "Remover Ponto", "Pesquisar"]
    )

    if menu == "Listar Pontos":
        list_points()
    elif menu == "Cadastrar Novo Ponto":
        create_point()
    elif menu == "Atualizar Ponto":
        update_point()
    elif menu == "Remover Ponto":
        delete_point()
    elif menu == "Pesquisar":
        search_points()

    st.sidebar.markdown("---")
    st.sidebar.info("Desenvolvido para o Grupo de Pesquisa Arqueológica da Amazônia")


def list_points():
    st.header("Pontos de Escavação Cadastrados")

    # Opções de ordenação
    sort_options = st.selectbox(
        "Ordenar por:",
        ["ID", "Tipo de Ponto", "Data de Descoberta", "Responsável"]
    )

    # Mapeamento de opções para colunas do DataFrame
    sort_mapping = {
        "ID": "id",
        "Tipo de Ponto": "point_type",
        "Data de Descoberta": "discovery_date",
        "Responsável": "responsible"
    }

    # Busca todos os pontos
    df = db.get_all_points()

    if not df.empty:
        # Ordena o DataFrame
        df = df.sort_values(by=sort_mapping[sort_options])

        # Formata a data para exibição
        df['discovery_date'] = pd.to_datetime(df['discovery_date']).dt.strftime('%d/%m/%Y')

        # Exibe a tabela
        st.dataframe(df)

        # Exibe detalhes de um ponto específico
        point_id = st.number_input("ID do ponto para ver detalhes:", min_value=1, step=1)
        if st.button("Ver Detalhes"):
            point = db.get_point_by_id(point_id)
            if point:
                st.subheader(f"Detalhes do Ponto #{point.id}")
                st.write(f"**Tipo:** {point.point_type}")
                st.write(f"**Latitude:** {point.latitude}")
                st.write(f"**Longitude:** {point.longitude}")
                st.write(f"**Altitude:** {point.altitude} metros")
                st.write(f"**Sistema de Referência:** {point.srid}")
                st.write(f"**Data da Descoberta:** {point.discovery_date.strftime('%d/%m/%Y')}")
                st.write(f"**Responsável:** {point.responsible}")
                st.write(f"**Descrição:**")
                st.write(point.description)
            else:
                st.error("Ponto não encontrado.")
    else:
        st.info("Nenhum ponto de escavação cadastrado ainda.")


def create_point():
    st.header("Cadastrar Novo Ponto de Escavação")

    with st.form("create_point_form"):
        point_type = st.selectbox(
            "Tipo de Ponto*",
            ["Antiga cabana indígena", "Utensílio indígena", "Artefato indígena",
             "Restos mortais", "Armas de caça", "Possível vestimenta", "Outro"]
        )

        if point_type == "Outro":
            point_type = st.text_input("Especifique o tipo de ponto:")

        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input("Latitude*", format="%.6f", step=0.000001, min_value=-90.0, max_value=90.0)
            altitude = st.number_input("Altitude (metros)*", min_value=0.0)

        with col2:
            longitude = st.number_input("Longitude*", format="%.6f", step=0.000001, min_value=-180.0, max_value=180.0)
            srid = st.selectbox("Sistema de Referência*", ["WGS84", "SIRGAS2000", "SAD69", "Outro"])

        if srid == "Outro":
            srid = st.text_input("Especifique o sistema de referência:")

        description = st.text_area("Descrição detalhada*", height=150)
        responsible = st.text_input("Responsável pelo registro*")

        discovery_date = st.date_input("Data da descoberta", datetime.now())

        submitted = st.form_submit_button("Cadastrar Ponto")

        if submitted:
            # Validação básica
            if not point_type or not description or not responsible:
                st.error("Preencha todos os campos obrigatórios.")
            else:
                # Tratamento mais completo para o objeto discovery_date
                actual_date = None
                if discovery_date is None:
                    actual_date = datetime.now().date()
                elif isinstance(discovery_date, tuple):
                    if discovery_date:  # Se a tupla não estiver vazia
                        actual_date = discovery_date[0]
                    else:
                        actual_date = datetime.now().date()  # Valor padrão se a tupla estiver vazia
                else:
                    # Se já for um objeto date
                    actual_date = discovery_date

                # Cria o objeto do ponto
                point = ExcavationPoint(
                    point_type=point_type,
                    latitude=latitude,
                    longitude=longitude,
                    altitude=altitude,
                    description=description,
                    discovery_date=datetime.combine(actual_date, datetime.min.time()),
                    responsible=responsible,
                    srid=srid
                )

                # Adiciona ao banco de dados
                point_id = db.create_point(point)

                if point_id:
                    st.success(f"Ponto de escavação cadastrado com sucesso! (ID: {point_id})")
                else:
                    st.error("Erro ao cadastrar o ponto de escavação.")


def update_point():
    st.header("Atualizar Ponto de Escavação")

    # Exibe mensagem de sucesso se atualização anterior foi bem-sucedida
    if 'update_success' in st.session_state:
        point_id = st.session_state.update_success
        st.success(f"✅ Ponto de escavação (ID: {point_id}) atualizado com sucesso!")
        # Exibe detalhes atualizados
        if 'updated_point_type' in st.session_state:
            st.info(f"Tipo: {st.session_state.updated_point_type} | Responsável: {st.session_state.updated_responsible}")

        # Limpa as flags da sessão
        del st.session_state.update_success
        if 'updated_point_type' in st.session_state:
            del st.session_state.updated_point_type
        if 'updated_responsible' in st.session_state:
            del st.session_state.updated_responsible

    # Lista os pontos para seleção
    df = db.get_all_points()

    if df.empty:
        st.info("Nenhum ponto cadastrado para atualizar.")
        return

    # Exibe a tabela para visualização
    st.dataframe(df)

    # Formulário de atualização
    point_id = st.number_input("ID do ponto a ser atualizado:", min_value=1, step=1)

    if st.button("Carregar Dados"):
        point = db.get_point_by_id(point_id)

        if not point:
            st.error("Ponto não encontrado.")
            return

        # Armazena o ponto na sessão para uso posterior
        st.session_state.current_point = point
        st.success("Dados carregados com sucesso!")

    if 'current_point' in st.session_state:
        point = st.session_state.current_point

        with st.form("update_point_form"):
            point_type = st.selectbox(
                "Tipo de Ponto*",
                ["Antiga cabana indígena", "Utensílio indígena", "Artefato indígena",
                 "Restos mortais", "Armas de caça", "Possível vestimenta", "Outro"],
                index=["Antiga cabana indígena", "Utensílio indígena", "Artefato indígena",
                       "Restos mortais", "Armas de caça", "Possível vestimenta", "Outro"].index(point.point_type)
                if point.point_type in ["Antiga cabana indígena", "Utensílio indígena", "Artefato indígena",
                                        "Restos mortais", "Armas de caça", "Possível vestimenta", "Outro"] else 6
            )

            if point_type == "Outro":
                point_type = st.text_input("Especifique o tipo de ponto:",
                                           value=point.point_type if point.point_type not in
                                           ["Antiga cabana indígena", "Utensílio indígena", "Artefato indígena",
                                            "Restos mortais", "Armas de caça", "Possível vestimenta"] else "")

            col1, col2 = st.columns(2)
            with col1:
                latitude = st.number_input("Latitude*", value=point.latitude, format="%.6f",
                                           step=0.000001, min_value=-90.0, max_value=90.0)
                altitude = st.number_input("Altitude (metros)*", value=point.altitude, min_value=0.0)

            with col2:
                longitude = st.number_input("Longitude*", value=point.longitude, format="%.6f",
                                            step=0.000001, min_value=-180.0, max_value=180.0)
                srid = st.selectbox("Sistema de Referência*", ["WGS84", "SIRGAS2000", "SAD69", "Outro"],
                                    index=["WGS84", "SIRGAS2000", "SAD69", "Outro"].index(point.srid)
                                    if point.srid in ["WGS84", "SIRGAS2000", "SAD69", "Outro"] else 3)

            if srid == "Outro":
                srid = st.text_input("Especifique o sistema de referência:",
                                     value=point.srid if point.srid not in ["WGS84", "SIRGAS2000", "SAD69"] else "")

            description = st.text_area("Descrição detalhada*", value=point.description, height=150)
            responsible = st.text_input("Responsável pelo registro*", value=point.responsible)

            discovery_date = st.date_input("Data da descoberta", value=point.discovery_date)

            submitted = st.form_submit_button("Atualizar Ponto")

            if submitted:
                # Validação básica
                if not point_type or not description or not responsible:
                    st.error("Preencha todos os campos obrigatórios.")
                else:
                    # Tratamento mais completo para o objeto discovery_date
                    actual_date = None
                    if discovery_date is None:
                        actual_date = point.discovery_date.date()  # Mantém a data anterior
                    elif isinstance(discovery_date, tuple):
                        if discovery_date:  # Se a tupla não estiver vazia
                            actual_date = discovery_date[0]
                        else:
                            actual_date = point.discovery_date.date()  # Mantém a data anterior se a tupla estiver vazia
                    else:
                        # Se já for um objeto date
                        actual_date = discovery_date

                    # Atualiza o objeto do ponto
                    updated_point = ExcavationPoint(
                        id=point.id,
                        point_type=point_type,
                        latitude=latitude,
                        longitude=longitude,
                        altitude=altitude,
                        description=description,
                        discovery_date=datetime.combine(actual_date, datetime.min.time()),
                        responsible=responsible,
                        srid=srid
                    )

                    # Atualiza no banco de dados
                    success = db.update_point(updated_point)

                    if success:
                        # Armazena informações sobre a atualização bem-sucedida na sessão
                        st.session_state.update_success = point.id
                        st.session_state.updated_point_type = point_type
                        st.session_state.updated_responsible = responsible

                        # Limpa a sessão do ponto atual
                        del st.session_state.current_point

                        # Exibe um spinner para indicar que a atualização está sendo processada
                        with st.spinner("Atualizando dados..."):
                            # Pequena pausa para garantir que o usuário veja o spinner
                            import time
                            time.sleep(0.5)

                        # Recarrega a página para atualizar os dados e mostrar a mensagem de sucesso
                        st.rerun()
                    else:
                        st.error("❌ Erro ao atualizar o ponto de escavação.")


def delete_point():
    st.header("Remover Ponto de Escavação")

    # Lista os pontos para seleção
    df = db.get_all_points()

    if df.empty:
        st.info("Nenhum ponto cadastrado para remover.")
        return

    # Exibe a tabela para visualização
    st.write("### Pontos disponíveis para exclusão")
    st.dataframe(df)

    # Interface de exclusão simplificada
    col1, col2 = st.columns([3, 1])

    with col1:
        point_id = st.number_input("ID do ponto a ser removido:", min_value=1, step=1)

    with col2:
        if st.button("Buscar"):
            st.session_state.selected_point_id = point_id

    # Se um ponto foi selecionado
    if 'selected_point_id' in st.session_state:
        selected_id = st.session_state.selected_point_id

        # Garantir que selected_id é um inteiro válido
        if selected_id is not None:
            selected_id = int(selected_id)
            point = db.get_point_by_id(selected_id)

            if point:
                st.warning(f"⚠️ Você está prestes a remover o seguinte ponto:")

                # Exibe informações em um formato mais estruturado
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**ID:** {point.id}")
                    st.write(f"**Tipo:** {point.point_type}")
                    st.write(f"**Responsável:** {point.responsible}")

                with col2:
                    st.write(f"**Latitude:** {point.latitude}")
                    st.write(f"**Longitude:** {point.longitude}")
                    st.write(f"**Data:** {point.discovery_date.strftime('%d/%m/%Y')}")

                st.write(f"**Descrição:** {point.description[:100]}..." if len(point.description) > 100 else f"**Descrição:** {point.description}")

                # Botão de confirmação de exclusão
                if st.button("🗑️ Confirmar Exclusão", key="confirm_delete_final"):
                    # Adicionamos feedback visual durante o processo
                    with st.spinner("Excluindo ponto..."):
                        # Tenta excluir o ponto
                        if point and point.id:
                            success = db.delete_point(point.id)

                            if success:
                                # Limpa o ponto selecionado
                                del st.session_state.selected_point_id
                                st.success(f"✅ Ponto ID: {point.id} foi removido com sucesso!")

                                # Verifica se o ponto realmente sumiu
                                if point.id:
                                    check_point = db.get_point_by_id(point.id)
                                    if check_point:
                                        st.error("⚠️ Erro: O ponto ainda existe na base de dados após a exclusão.")
                                    else:
                                        st.info("📊 A base de dados foi atualizada.")

                                        # Atualiza a lista de pontos
                                        new_df = db.get_all_points()
                                        if not new_df.empty:
                                            st.write("### Lista atualizada de pontos")
                                            st.dataframe(new_df)
                                        else:
                                            st.info("Não há mais pontos cadastrados.")

                                # Opção para retornar
                                if st.button("↩️ Voltar"):
                                    st.rerun()
                            else:
                                st.error(f"❌ Falha ao remover o ponto ID: {point.id}. Tente novamente.")

            # Botão para cancelar a exclusão
            if st.button("❌ Cancelar", key="cancel_delete"):
                del st.session_state.selected_point_id
                st.rerun()
        else:
            st.error(f"❌ Ponto com ID {selected_id} não encontrado.")
            del st.session_state.selected_point_id


def search_points():
    st.header("Pesquisar Pontos de Escavação")

    search_term = st.text_input("Termo de pesquisa:")

    col1, col2 = st.columns(2)
    with col1:
        search_field = st.selectbox(
            "Pesquisar em campo específico:",
            ["Todos os campos", "Tipo de Ponto", "Descrição", "Responsável"]
        )

    with col2:
        sort_by = st.selectbox(
            "Ordenar resultados por:",
            ["ID", "Tipo de Ponto", "Data de Descoberta"]
        )

    if st.button("Pesquisar"):
        field = None
        if search_field != "Todos os campos":
            field_mapping = {
                "Tipo de Ponto": "point_type",
                "Descrição": "description",
                "Responsável": "responsible"
            }
            field = field_mapping[search_field]

        # Se field for None, a função search_points deve lidar com isso internamente
        # convertendo-o para uma string vazia ou tratando None de forma adequada
        results = db.search_points(search_term, field if field is not None else "")

        if results:
            # Converte para DataFrame para facilitar a exibição
            df = pd.DataFrame(results)

            # Formata a data para exibição
            df['discovery_date'] = pd.to_datetime(df['discovery_date']).dt.strftime('%d/%m/%Y')

            # Ordenação
            sort_mapping = {
                "ID": "id",
                "Tipo de Ponto": "point_type",
                "Data de Descoberta": "discovery_date"
            }
            df = df.sort_values(by=sort_mapping[sort_by])

            st.subheader(f"Resultados encontrados: {len(results)}")
            st.dataframe(df)
        else:
            st.info("Nenhum resultado encontrado para a pesquisa.")


if __name__ == "__main__":
    main()
