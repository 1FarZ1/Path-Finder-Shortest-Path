import osmnx as ox
import networkx as nx
import pandas as pd
from geopy.geocoders import Nominatim
import streamlit as st
import os

geolocator = Nominatim(user_agent="my_geocoder")

data = {
    "id": [],
    "lat": [],
    "lon": [],
    "name": []
}
df: pd.DataFrame = None

def is_data_exists():
    if os.path.exists("data/el_achour_nodes.csv"):
        return True
    else:
        return False


def get_last_item_node_id():
    if os.path.exists("data/el_achour_nodes.csv"):
        return pd.read_csv("data/el_achour_nodes.csv").index.values[-1]
    else:
        return 0

def need_skip_in_df():
    if os.path.exists("data/el_achour_nodes.csv"):
        return len(pd.read_csv("data/el_achour_nodes.csv"))
    else:
        return 0

def fill_df():
    global df
    if os.path.exists("data/el_achour_nodes.csv"):
        df = pd.read_csv("data/el_achour_nodes.csv",index_col=0)
    else:
        df = pd.DataFrame(data)

def create_csv(data_frame: pd.DataFrame):
    data_frame.to_csv("data/el_achour_nodes.csv")


def get_place_name(lat, lon):
    location = geolocator.reverse((lat, lon))
    return location.address.split(',')[0]

def df_construct(g):
    last_node_id = df['id'].max() 
    i = need_skip_in_df()
    print(f"Last Node ID: {last_node_id}")
    for node in g.nodes(data=True):
        lat = node[1]['y']
        lon = node[1]['x']
        
        if node[0] <= last_node_id:
            continue
        
        place_name = get_place_name(lat, lon)
        print(f"Node: {node[0]} - Place Name: {place_name}")
        if not place_name.isdigit() and not place_name.startswith(('CW', 'RN', 'RU')):
            if place_name not in df['name'].values:
                df.loc[i] = [node[0], lat, lon, place_name]
                i += 1

            create_csv(df)

def get_map_data(name):
    place_name = name + ', Draria District, Algiers, Algeria'
    g = ox.graph_from_place(
        place_name,
        network_type='drive',
    )
    return g


def a_star_search(g, source, target):
    path = nx.astar_path(g, source, target, weight='length')
    return path


def main():
    fill_df()
    graph = None
    graph = get_map_data('El Achour')
    
    ## ONLY FOR FIRST TIME
    # df_construct(graph)

    st.title("Easy Path Finder")
    col1, col2= st.columns(2,gap='large')

    figure = None
    st.session_state.canShow = False
    with col1:
        source = st.selectbox("Source", options=df["name"].values)
        destination = st.selectbox("Destination", options=df["name"].values)

        color_list = ['#008000' if item == source or item == destination else '#FF0000' for item in df['name'].values]
        size_list = [50 if item == source or item == destination else 1 for item in df['name'].values]

        df['color'] = color_list
        df['size'] = size_list


        if st.button('Get Shortest Path'):
            if source != destination:
                src = df[df['name'] == source]['id'].values[0]
                dest = df[df['name'] == destination]['id'].values[0]
                shortest_path = a_star_search(graph, src, dest)

                fig, ax = ox.plot_graph_route(
                    graph,
                    shortest_path,
                    route_color='r',
                    route_linewidth=3,
                    node_size=0,
                    figsize=(15, 15),
                    show=False,
                    close=False
                )
                figure = fig
                st.session_state.canShow = True
        with col2:
            if not st.session_state.canShow:
                    map_data = pd.DataFrame(df, columns=['lat', 'lon', 'color', 'size'])
                    st.map(map_data, color='color', size='size')
            else:
                st.pyplot(fig=figure)

main()