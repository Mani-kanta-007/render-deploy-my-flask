document.getElementById('city_name').addEventListener('input', function() {
    const cityName = this.value;
    if (cityName.length > 2) { // start suggesting after 3 characters
        fetch(`https://api.opencagedata.com/geocode/v1/json?q=${cityName}&key=cf407d776d8444339efe6310a2aefde9`)
            .then(response => response.json())
            .then(data => {
                const results = data.results;
                const suggestions = document.getElementById('suggestions');
                suggestions.innerHTML = '';

                results.forEach(result => {
                    const suggestion = document.createElement('div');
                    suggestion.className = 'suggestion-item';
                    suggestion.textContent = result.formatted;
                    suggestion.addEventListener('click', () => {
                        document.getElementById('city_name').value = result.formatted;
                        document.getElementById('latitude').value = result.geometry.lat;
                        document.getElementById('longitude').value = result.geometry.lng;
                        suggestions.innerHTML = '';
                    });
                    suggestions.appendChild(suggestion);
                });
            })
            .catch(error => console.error('Error:', error));
    } else {
        document.getElementById('suggestions').innerHTML = '';
    }
});

document.getElementById('addCity').addEventListener('click', function() {
    const cityName = document.getElementById('city_name').value;
    const latitude = document.getElementById('latitude').value;
    const longitude = document.getElementById('longitude').value;

//    criteria for api
    const cityItems = document.getElementsByClassName('city-item');
    if (cityItems.length >= 50) {
        alert('You can only add up to 50 cities.');
        return;
    }

    if (cityName && latitude && longitude) {
        const cityList = document.getElementById('cityList');
        const cityItem = document.createElement('div');
        cityItem.className = 'city-item';
        cityItem.textContent = `City: ${cityName}, Latitude: ${latitude}, Longitude: ${longitude}`;
        cityList.appendChild(cityItem);

        document.getElementById('city_name').value = '';
        document.getElementById('latitude').value = '';
        document.getElementById('longitude').value = '';
        document.getElementById('suggestions').innerHTML = '';
    }
});

document.getElementById('submitCities').addEventListener('click', function() {
    const cityItems = document.getElementsByClassName('city-item');
    const cities = [];

    for (let i = 0; i < cityItems.length; i++) {
        const cityText = cityItems[i].textContent;
        const cityData = cityText.match(/City: (.*), Latitude: (.*), Longitude: (.*)/);
        cities.push({
            city_name: cityData[1],
            latitude: parseFloat(cityData[2]),
            longitude: parseFloat(cityData[3])
        });
    }

    fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(cities)
    })
    .then(response => response.text())
    .then(html => {
        document.open();
        document.write(html);
        document.close();
    })
    .catch(error => console.log('Error:', error));
});