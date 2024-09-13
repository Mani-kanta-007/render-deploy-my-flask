import pandas as pd
from api import api_call
from tsp import tsp
from geopy.distance import geodesic
import folium
from IPython.display import HTML, display
import webbrowser,os

def main(df_cities,start_city):
    # api calling
    origin = ''
    for cord in df_cities.itertuples():
        origin += f'{cord.latitude},{cord.longitude};'
    origin = origin[0:len(origin)-1]
    #api-calling
    #--distance,duration = api_call(origin)
    #tsp-calculation
    #--order_of_visit , distance_of_journey = tsp(distance, start_city)
    # remove last for adjusting size
    order_of_visit = [0,3,1,4,2,0]
    order_of_visit = order_of_visit[0:len(order_of_visit)-1]
    #Create a list of indices as integers
    df_cities['city_index'] = list(range(len(df_cities)))
    df_cities = changeOrderOfDataFrame(order_of_visit,df_cities)

    """"
    cities          place_name  latitude  longitude  order_of_visit / stops
0                    hotel   48.8527     2.3542               0
3               Montmartre   48.8872     2.3388               1
1              Sacre Coeur   48.8867     2.3431               2
5          Arc de Triomphe   48.8739     2.2950               3
6       Av. Champs Élysées   48.8710     2.3036               4
8              Tour Eiffel   48.8585     2.2945               5
4          Port de Suffren   48.8577     2.2902               6
2                   Louvre   48.8607     2.3376               7
7               Notre Dame   48.8531     2.3498               8
    """
    #original
    display(df_cities)



def display(df_sites):

    #for calculating avg_location for displaying . Center of the map
    avg_location = df_sites[['latitude','longitude']].mean().tolist()
    map = folium.Map(location=avg_location,zoom_start=14)

    df_routes = df_sites.copy()
    df_routes_segments = df_routes.join(
        df_routes.shift(-1),  # map each stop to its next stop
        rsuffix = '_next'
    ).dropna()   # last stop has no "next one", so drop it
    # Cast 'city_index_next' back to integer
    df_routes_segments['city_index_next'] = df_routes_segments['city_index_next'].astype(int)

    df_routes_segments['Distance_Segment'] = df_routes_segments.apply(
        lambda place : round (
            geodesic(
                (place.latitude,place.longitude),
                (place.latitude_next,place.longitude_next)
            ).kilometers,
            2),
        axis = 1
    )
    # adding marker and lines
    for place in df_routes_segments.itertuples():
        initial_stop = place.Index == 0
        icon = folium.Icon(icon='home' if initial_stop else 'info-sign',
                       color='cadetblue' if initial_stop else 'red')
        marker = folium.Marker(location=(place.latitude,place.longitude),icon=icon,tooltip=f"<b>Name</b>: {place.place_name} <br>" \
                                                                                       + f"<b>Stop number</b>: {place.Index} <br>")
        line = folium.PolyLine(
            locations=[(place.latitude,place.longitude),(place.latitude_next,place.longitude_next)],
            tooltip = f"<b>From</b>: {place.place_name} <br>" \
                      + f"<b>To</b>: {place.place_name_next} <br>" \
                      + f"<b>Distance</b>: {place.Distance_Segment:.0f} km",
        )
        marker.add_to(map)
        line.add_to(map)

    folium.Marker(location=(place.latitude_next,place.longitude_next),
                  tooltip=f"<b>Name</b>: {place.place_name_next} <br>" \
                          + f"<b>Stop number</b>: {place.Index} <br>",
                  icon = folium.Icon(icon='info-sign', color='red')
                  ).add_to(map)

    print_html_content_on_map(df_routes_segments,map)

def print_html_content_on_map(df_routes_segments,map):
    TAG_ROUTE_NAME = "Name"
    TAG_NUMBER_STOPS = "Num stops"
    TAG_TOTAL_DISTANCE = "Distance"
    _SPACE_HTML = "&nbsp"  # needed to add empty spaces between KPIs

    # get summary info to display on map
    name = df_routes_segments.columns.name.capitalize()
    n_stops = df_routes_segments['place_name'].size
    route_distance = df_routes_segments['Distance_Segment'].sum().round(0)

    _html_text_summary = f"""
    <b>{TAG_NUMBER_STOPS}</b> <b>{TAG_TOTAL_DISTANCE}</b>
    <br>
    {n_stops} {16 * _SPACE_HTML} {route_distance:.0f} km
    """


    STYLE_SUMMARY = (
        "position:absolute;z-index:100000;font-size:20px;"
        "right:0;bottom:0;color:black;"
        "text-shadow:-1px 0 white, 0 1px white, 0 1px white"
    )
    html_summary = f'<h2 style="{STYLE_SUMMARY}">{_html_text_summary}</h2>'

    # let's see how the KPIs look like (run all in same cell):
    map_with_kpis = map

    root_map = map_with_kpis.get_root()
    root_map.html.add_child(folium.Element(html_summary))

    map_with_kpis.save('output.html')
    # Open the map in the default web browser
    webbrowser.open('file://' + os.path.realpath('output.html'))



def changeOrderOfDataFrame(order,df):
    # Create a Categorical type with the desired order
    df['city_index'] = pd.Categorical(df['city_index'], categories=order, ordered=True)

    # Sort the DataFrame according to the specified order
    df_reordered = df.sort_values('city_index').reset_index(drop=True)
    return df_reordered


# df_sites = pd.DataFrame(
#     [['hotel',              48.8527, 2.3542],
#      ['Sacre Coeur',        48.8867, 2.3431],
#      ['Louvre',             48.8607, 2.3376],
#      ['Montmartre',         48.8872, 2.3388],
#      ['Port de Suffren',    48.8577, 2.2902],
#      ['Arc de Triomphe',    48.8739, 2.2950],
#      ['Av. Champs Élysées', 48.8710, 2.3036],
#      ['Notre Dame',         48.8531, 2.3498],
#      ['Tour Eiffel',        48.8585, 2.2945]],
#     columns=pd.Index(['place_name', 'latitude', 'longitude'], name='cities')
# )
""""
17.433374 78.446831 Punjagutta Officers
17.471676, 78.426117 Moosapet metro
17.419899,78.524054 ou
17.438353,78.363965 Gachibowli
order_of_visit = [0,3,1,4,2,0]
"""
df_sites = pd.DataFrame(
    [['UPPAL',              17.400959, 78.565839],
     [' Punjagutta Office',        17.433374, 78.446831],
     ['Moosapet metro',             17.471676, 78.426117],
     ['ou',    17.419899,78.524054],
     ['Gachibowli',    17.438353,78.363965]],
    columns=pd.Index(['place_name', 'latitude', 'longitude'], name='cities')
)
main(df_sites,0)
