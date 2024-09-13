from flask import Flask, request, send_file, render_template
import pandas as pd
from api import api_call
from tsp import tsp
from map import *
app = Flask(__name__)

distance, duration = None, None
toggle = None

def main(df_cities, start_city):
    # api-parameter-setting
    origin = ''
    for cord in df_cities.itertuples():
        origin += f'{cord.latitude},{cord.longitude};'
    origin = origin[0:len(origin)-1]

    global distance, duration
    # api-calling
    distance, duration, success, file_name = api_call(origin)

    if not success:
        return  file_name

    # tsp-calculation-for-distance-matrix
    order_of_visit_distance, distance_of_journey = tsp(distance, start_city)
    # tsp-calculation-for-duration-matrix
    order_of_visit_duration, duration_of_journey = tsp(duration, start_city)

    # remove last for adjusting size
    # example : order_of_visit = [0,3,1,4,2,0]
    order_of_visit_distance = order_of_visit_distance[0:len(order_of_visit_distance)-1]
    order_of_visit_duation = order_of_visit_duration[0:len(order_of_visit_duration)-1]

    # Create a list of indices as integers
    df_cities['city_index'] = list(range(len(df_cities)))
    df_cities.to_csv('original_DataFrame.csv')
    # making a copies for different virtualizations

    df_cities_distance = df_cities.copy()
    df_cities_duration = df_cities.copy()

    # ordering according to visited order
    df_cities_distance = changeOrderOfDataFrame(order_of_visit_distance, df_cities_distance)
    df_cities_duration = changeOrderOfDataFrame(order_of_visit_duation, df_cities_duration)

    df_cities_distance.to_csv('tsp_order_data_frame_distance.csv')
    df_cities_duration.to_csv('tsp_order_data_frame_duration.csv')
    distance_map = map_creation(df_cities_distance,distance,'distance_file')
    duration_map = map_creation(df_cities_distance,duration,'duration_file')
    return  distance_map


def changeOrderOfDataFrame(order,df):
    # Create a Categorical type with the desired order
    df['city_index'] = pd.Categorical(df['city_index'], categories=order, ordered=True)

    # Sort the DataFrame according to the specified order
    df_reordered = df.sort_values('city_index').reset_index(drop=True)
    return df_reordered


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()

    # Create the DataFrame in the specified format
    df_sites = pd.DataFrame(
        [[city['city_name'], city['latitude'], city['longitude']] for city in data],
        columns=pd.Index(['city_name', 'latitude', 'longitude'], name='city')
    )

    # selected toggle should catch here

    html_content =  main(df_sites,start_city=0)
    return send_file(html_content)


if __name__ == '__main__':
    app.run()
