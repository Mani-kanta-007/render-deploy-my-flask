import requests

def api_call(origin):
    url = "https://trueway-matrix.p.rapidapi.com/CalculateDrivingMatrix"
    querystring = {"origins": origin}

    headers = {
        "x-rapidapi-key": "795bee2608mshb146b4d5cbfde7ep11e93bjsn4a436c87e0ef",
        "x-rapidapi-host": "trueway-matrix.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        if response.status_code !=200:
            print("BOO!",response.status_code)
            return None, None, False, 'API-FAILED.html'

        response.raise_for_status()  # Raise an exception for HTTP errors

        obj = response.json()
        distances = obj["distances"]
        durations = obj["durations"]

        print('API-RESPONSE : ',distances,durations)

        # if response data have no road connections then retunr
        for i in distances:
            for t in i:
                if t is None:
                    return None, None, False,'NO_ROAD.html'

        print("API_SUCCESSFULLY_CALLED!!")
        return distances, durations, True, None

    except requests.exceptions.RequestException as e:
        print(f"Error: API call failed with exception: {e}")
        return None, None, False, 'API-FAILED.html'
