import os
import leafmap.foliumap as leafmap
import streamlit as st
import requests

# Set page title and layout
st.set_page_config(page_title='Night Light', layout='wide')

st.title('Night Light Dashboard')

# Sidebar information
st.sidebar.title('About')
st.sidebar.info('Explore the Night Lights using an address.')

# COG URL for night light data
gcs_bucket = 'https://storage.googleapis.com/spatialthoughts-public-data/ntl/viirs/'
cog_url = os.path.join(gcs_bucket, 'viirs_ntl_2021_global.tif')

# API key for OpenRouteService
ORS_API_KEY = st.secrets['ORS_API_KEY']

# Geocoding function
@st.cache_data
def geocode(query):
    parameters = {
        'api_key': ORS_API_KEY,
        'text': query
    }
    response = requests.get('https://api.openrouteservice.org/geocode/search', params=parameters)
    if response.status_code == 200:
        data = response.json()
        if data['features']:
            x, y = data['features'][0]['geometry']['coordinates']
            return y, x
    return None

# Input for address
address = st.sidebar.text_input('Enter an Address(City):')
if address:
    geocoded_coords = geocode(address)
    if geocoded_coords:
        st.sidebar.success(f'Coordinates: {geocoded_coords[0]}, {geocoded_coords[1]}')
        central_lat, central_lon = geocoded_coords

        # Input for buffer size
        buffer = st.sidebar.number_input("Buffer (degrees)", value=0.5, step=0.1)

        # Create Leafmap map
        m = leafmap.Map(width=900, height=450)

        # Sidebar input for color style
        cmap_list = ['viridis', 'plasma', 'inferno', 'magma', 'cool']
        color_style = st.sidebar.selectbox('Select a Color Style', cmap_list)

        # Add COG layer
        m.add_cog_layer(
            cog_url, name='Night Light', zoom_to_layer=False,
            rescale='0,60', colormap_name=color_style
        )

        # Calculate bounding box from central point and buffer
        minx = central_lon - buffer
        miny = central_lat - buffer
        maxx = central_lon + buffer
        maxy = central_lat + buffer
        bounds = [minx, miny, maxx, maxy]

        # Zoom the map to bounds
        m.zoom_to_bounds(bounds)

        # Convert the map to HTML and display it in Streamlit
        map_html = m.to_html()
        st.components.v1.html(map_html, height=500)
    else:
        st.sidebar.error('Failed to geocode the address. Please try again.')
else:
    st.warning('Please enter an address to display the map.')
