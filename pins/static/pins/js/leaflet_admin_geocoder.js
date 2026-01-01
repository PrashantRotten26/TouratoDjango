window.addEventListener('map:init', function (event) {
    var map = event.detail.map;
    
    var geocoder = L.Control.geocoder({
        defaultMarkGeocode: true,
        collapsed: true,
        position: 'topleft',
        placeholder: 'Search for city or address...',
        errorMessage: 'No results found.',
        geocoder: L.Control.Geocoder.nominatim()  // Free OSM Nominatim
    }).addTo(map);
});
