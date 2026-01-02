window.addEventListener('map:init', function (event) {
    var map = event.detail.map;
    
    // Helper: ensure Control.Geocoder is available, otherwise load from CDN
    function ensureGeocoder(cb) {
        if (window.L && L.Control && L.Control.Geocoder && typeof L.Control.Geocoder.nominatim === 'function') {
            return cb();
        }
        // Avoid inserting multiple script tags
        if (window._leaflet_geocoder_loading) {
            // poll until available
            var wait = setInterval(function() {
                if (window.L && L.Control && L.Control.Geocoder && typeof L.Control.Geocoder.nominatim === 'function') {
                    clearInterval(wait);
                    cb();
                }
            }, 100);
            return;
        }
        window._leaflet_geocoder_loading = true;
        var script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/leaflet-control-geocoder@1.13.0/dist/Control.Geocoder.js';
        script.async = true;
        script.onload = function() {
            window._leaflet_geocoder_loading = false;
            cb();
        };
        script.onerror = function() {
            window._leaflet_geocoder_loading = false;
            console.error('Failed to load leaflet-control-geocoder.js');
        };
        document.head.appendChild(script);
    }

    // initialize geocoder when map ready and script available
    map.whenReady(function() {
        ensureGeocoder(function() {
            var geocoder = L.Control.geocoder({
                defaultMarkGeocode: false,  // Don't auto-add marker
                collapsed: true,           // Keep search box expanded
                position: 'topleft',
                placeholder: 'Search for location...',
                errorMessage: 'Location not found. Try a different search.',
                geocoder: L.Control.Geocoder.nominatim({
                    // Use local proxy to avoid CORS and to provide a proper User-Agent
                    // The proxy endpoint is implemented in Django at /geocode/nominatim/
                    serviceUrl: 'https://nominatim.openstreetmap.org/',
                    htmlTemplate: function(r) {
                        return r.display_name;
                    }
                })
            });

            // Handle geocoding results
            geocoder.on('markgeocode', function(e) {
                var latlng = e.geocode.center;

                // Clear existing markers
                map.eachLayer(function(layer) {
                    if (layer instanceof L.Marker) {
                        map.removeLayer(layer);
                    }
                });

                // Add new marker at found location
                var marker = L.marker(latlng).addTo(map);

                // Pan to the location
                map.setView(latlng, 15);

                // Update the form field with coordinates
                var event = new CustomEvent('geocode:result', {
                    detail: {
                        latlng: latlng,
                        marker: marker
                    }
                });
                window.dispatchEvent(event);
            });

            geocoder.addTo(map);
        });
    });
});

// Keep track of geometry fields attached to maps so we can update them
window._django_leaflet_fields = window._django_leaflet_fields || {};

// Listen for the django-leaflet field load event to capture the field instance
window.addEventListener('map:loadfield', function(ev) {
    try {
        var field = ev.detail.field; // L.GeometryField instance
        var map = field._map;
        if (map && map._container && map._container.id) {
            window._django_leaflet_fields[map._container.id] = field;
        }
    } catch (err) {
        // ignore
    }
});

// When a geocode result is dispatched, store the geometry to the corresponding field
window.addEventListener('geocode:result', function(ev) {
    var latlng = ev.detail.latlng;
    var marker = ev.detail.marker;
    // Find the map that contains this marker (marker._map)
    var map = marker._map || null;
    if (!map || !map._container || !map._container.id) return;
    var field = window._django_leaflet_fields[map._container.id];
    if (!field) return;

    // Clear existing layers if field is not a collection
    if (!field.options.is_collection) {
        field.drawnItems.eachLayer(function(l) {
            field.drawnItems.removeLayer(l);
            try { map.removeLayer(l); } catch (e) {}
        });
    }

    // Create a proper point layer and add to the field drawnItems
    var pointLayer = L.marker(latlng);
    field.drawnItems.addLayer(pointLayer);
    if (!field.drawnItems._map) {
        field.drawnItems.addTo(map);
    }

    // Persist to the hidden form field
    try {
        field.store.save(field.drawnItems);
    } catch (err) {
        console.error('Error saving geocoded point to geometry field', err);
    }
});
