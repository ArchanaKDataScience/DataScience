import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

st.write("Streamlit has lots of fans in the geo community. 🌍 It supports maps from PyDeck, Folium, Kepler.gl, and others.")

chart_data = pd.DataFrame(
   np.random.randn(1000, 2) / [100, 100] + [52.30, -5.29],
   np.random.randn(1000, 2) / [100, 100] + [52.30, -5.29],
   columns=['lat', 'lon'])

st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=52.30,
        longitude=-5.29,
        zoom=11,
        pitch=50,
    ),

    layers=[
        pdk.Layer(
           'HexagonLayer',
           data=chart_data,
           get_position='[lon, lat]',
           radius=200,
           elevation_scale=4,
           elevation_range=[0, 1000],
           pickable=True,
           extruded=True,
        ),
        pdk.Layer(
            'ScatterplotLayer',
            data=chart_data,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=200,
        ),
    ],
))