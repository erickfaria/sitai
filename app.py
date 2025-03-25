import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys

# Adiciona o diretório atual ao sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Verifica se os módulos estão disponíveis no caminho diretamente ou na pasta sitai
try:
    from models import ExcavationPoint
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
                # Cria o objeto do ponto
                point = ExcavationPoint(
                    point_type=point_type,
                    latitude=latitude,
                    longitude=longitude,
                    altitude=altitude,
                    description=description,
                    discovery_date=datetime.combine(discovery_date, datetime.min.time()),
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
                    # Atualiza o objeto do ponto
                    updated_point = ExcavationPoint(
                        id=point.id,
                        point_type=point_type,
                        latitude=latitude,
                        longitude=longitude,
                        altitude=altitude,
                        description=description,
                        discovery_date=datetime.combine(discovery_date, datetime.min.time()),
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
    st.dataframe(df)
    
    # Formulário de exclusão
    with st.form("delete_form"):
        point_id = st.number_input("ID do ponto a ser removido:", min_value=1, step=1)
        submitted = st.form_submit_button("Buscar Ponto")
    
    if submitted:
        point = db.get_point_by_id(point_id)
        
        if point:
            st.warning(f"Você está prestes a remover o ponto: **{point.point_type}** (ID: {point.id})")
            st.write(f"Latitude: {point.latitude}, Longitude: {point.longitude}")
            st.write(f"Responsável: {point.responsible}")
            st.write(f"Descrição: {point.description[:100]}..." if len(point.description) > 100 else f"Descrição: {point.description}")
            
            # Botão de confirmação fora do formulário para evitar problemas de estado
            confirm_delete = st.button("🗑️ Confirmar Exclusão", key="confirm_delete")
            
            if confirm_delete:
                # Tentativa de exclusão com feedback detalhado
                try:
                    success = db.delete_point(point.id)
                    
                    if success:
                        st.success(f"✅ Ponto de escavação (ID: {point.id}) removido com sucesso!")
                        
                        # Adicionamos um spinner para dar tempo de processar a exclusão
                        with st.spinner("Atualizando lista de pontos..."):
                            import time
                            time.sleep(1)  # Pequena pausa para garantir atualização do DB
                        
                        # Recarregamos os dados para mostrar que o item foi removido
                        updated_df = db.get_all_points()
                        if not updated_df.empty:
                            st.subheader("Lista atualizada de pontos:")
                            st.dataframe(updated_df)
                        else:
                            st.info("Não há mais pontos cadastrados.")
                        
                        # Opção para retornar ao início
                        if st.button("Voltar ao início"):
                            st.rerun()
                    else:
                        st.error("❌ Erro ao remover o ponto de escavação. Tente novamente.")
                except Exception as e:
                    st.error(f"❌ Ocorreu um erro durante a exclusão: {str(e)}")
        else:
            st.error(f"❌ Ponto com ID {point_id} não encontrado.")

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
        
        results = db.search_points(search_term, field)
        
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
