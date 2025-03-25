import streamlit as st
import pandas as pd
from datetime import datetime
import os
import sys

# Adiciona o diretório atual ao sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sitai.models import ExcavationPoint
import sitai.database as db

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
                        st.success(f"Ponto de escavação atualizado com sucesso!")
                        # Limpa a sessão
                        del st.session_state.current_point
                        # Recarrega a página para atualizar os dados
                        st.experimental_rerun()
                    else:
                        st.error("Erro ao atualizar o ponto de escavação.")

def delete_point():
    st.header("Remover Ponto de Escavação")
    
    # Lista os pontos para seleção
    df = db.get_all_points()
    
    if df.empty:
        st.info("Nenhum ponto cadastrado para remover.")
        return
    
    # Exibe a tabela para visualização
    st.dataframe(df)
    
    point_id = st.number_input("ID do ponto a ser removido:", min_value=1, step=1)
    
    if st.button("Buscar Ponto"):
        point = db.get_point_by_id(point_id)
        
        if point:
            st.warning(f"Você está prestes a remover o ponto: **{point.point_type}** (ID: {point.id})")
            st.write(f"Latitude: {point.latitude}, Longitude: {point.longitude}")
            st.write(f"Responsável: {point.responsible}")
            
            if st.button("Confirmar Remoção", key="confirm_delete"):
                success = db.delete_point(point_id)
                
                if success:
                    st.success(f"Ponto de escavação removido com sucesso!")
                    # Recarrega a página para atualizar os dados
                    st.experimental_rerun()
                else:
                    st.error("Erro ao remover o ponto de escavação.")
        else:
            st.error("Ponto não encontrado.")

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
