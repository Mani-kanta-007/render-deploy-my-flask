import folium
import openrouteservice

#  OpenRouteService API key
API_KEY = '5b3ce3597851110001cf6248331b242b9d564c6383b35a7d7c7a0772'

# Initialize the OpenRouteService client
client = openrouteservice.Client(key=API_KEY)

def map_creation(df_sites, d_t_constraint,file_name):
    # for calculating avg_location for displaying . Center of the map
    avg_location = df_sites[['latitude','longitude']].mean().tolist()
    map = folium.Map(location=avg_location, zoom_start=14)

    df_routes = df_sites.copy()
    df_routes_segments = df_routes.join(
        df_routes.shift(-1),  # map each stop to its next stop
        rsuffix='_next'
    ).dropna()   # last stop has no "next one", so drop it

    # Cast 'city_index_next' back to integer
    df_routes_segments['city_index_next'] = df_routes_segments['city_index_next'].astype(int)

    df_routes_segments.to_csv('joined_dataframe.csv')

    # printing distance matrix or duration according to file_name mentione
    print(file_name,' : ', d_t_constraint)

    df_routes_segments['d_t'] = df_routes_segments.apply(
        lambda temp : round (
            d_t_constraint[temp.city_index][temp.city_index_next]/(1000 if file_name=='distance_file' else 60),
            2),
        axis = 1
    )

    # saving distance or duration column added file
    df_routes_segments.to_csv('d_t_added_to_df.csv')

    # adding marker and lines
    given_d_t = 'Distance' if file_name=='distance_file' else 'Duration'
    metric =  'km' if file_name=='distance_file' else 'minutes'
    for place in df_routes_segments.itertuples():
        initial_stop = place.Index == 0
        icon = folium.Icon(icon='home' if initial_stop else 'info-sign',
                           color='cadetblue' if initial_stop else 'red')
        marker = folium.Marker(location=(place.latitude,place.longitude),icon=icon,tooltip=f"<b>Name</b>: {place.city_name} <br>" \
                                                                                           + f"<b>Stop number</b>: {place.Index} <br>")
        # line = folium.PolyLine(
        #     locations=[(place.latitude,place.longitude),(place.latitude_next,place.longitude_next)],
        #     tooltip = f"<b>From</b>: {place.city_name} <br>" \
        #               + f"<b>To</b>: {place.city_name_next} <br>" \
        #               + f"<b>{given_d_t}</b>: {place.d_t:.0f} {metric}",
        # )
        marker.add_to(map)
        # line.add_to(map)

    folium.Marker(location=(place.latitude_next,place.longitude_next),
                  tooltip=f"<b>Name</b>: {place.city_name_next} <br>" \
                          + f"<b>Stop number</b>: {place.Index+1} <br>",
                  icon = folium.Icon(icon='info-sign', color='red')
                  ).add_to(map)

    # adding original Route instead of straight lines
    for index, row in df_routes_segments.iterrows():
        start = (row['longitude'], row['latitude'])
        end = (row['longitude_next'], row['latitude_next'])

        # Get directions from OpenRouteService
        route = client.directions(
            coordinates=[start, end],
            profile='driving-car',
            format='geojson'
        )

        # Extract the route geometry
        route_coords = [list(reversed(coord)) for coord in route['features'][0]['geometry']['coordinates']]
        # Define the tooltip
        tooltip = (
            f"<b>From</b>: {row['city_name']} <br>"
            f"<b>To</b>: {row['city_name_next']} <br>"
            f"<b>Distance</b>: {row['d_t']:.2f} {metric}"
        )

        # Draw the route as a polyline on the map with the tooltip
        folium.PolyLine(locations=route_coords, color='blue', tooltip=tooltip).add_to(map)
    # ------
    return print_html_content_on_map(df_routes_segments,map,file_name)


def print_html_content_on_map(df_routes_segments,map,file_name):
    TAG_NUMBER_STOPS = "Num stops"
    TAG_TOTAL_DISTANCE = "Distance" if file_name == 'distance_file' else 'Duration'
    _SPACE_HTML = "&nbsp"  # needed to add empty spaces between KPIs

    n_stops = df_routes_segments['city_name'].size
    route_distance = df_routes_segments['d_t'].sum()

    _html_text_summary = f"""
    <b>{TAG_NUMBER_STOPS}</b> <b>{TAG_TOTAL_DISTANCE}</b>
    <br>
    {n_stops} {16 * _SPACE_HTML} {route_distance:.0f} km
    """ if file_name=='distance_file' else f"""
    <b>{TAG_NUMBER_STOPS}</b> <b>{TAG_TOTAL_DISTANCE}</b>
    <br>
    {n_stops} {16 * _SPACE_HTML} {route_distance:.0f} minutes
    """


    STYLE_SUMMARY = (
        "position:absolute;z-index:100000;font-size:20px;"
        "right:0;bottom:0;color:black;"
        "text-shadow:-1px 0 white, 0 1px white, 0 1px white"
    )
    html_summary = f'<h2 style="{STYLE_SUMMARY}">{_html_text_summary}</h2>'

    # let's see how the KPIs look like
    map_with_kpis = map

    root_map = map_with_kpis.get_root()
    root_map.html.add_child(folium.Element(html_summary))
    output_file = file_name+'_'+'output.html'
    root_map.save(output_file)
    return output_file
