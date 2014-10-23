$(function () {
    'use strict';

    var geometryField = $('#geometry');

    L.mapbox.accessToken = 'pk.eyJ1Ijoib3JvaWNrIiwiYSI6ImFIZ2M5Q2cifQ.pNyTbEYSPe4ggcx1LeFlBg';
    var map = L.mapbox.map('map', 'examples.map-i86nkdio').setView([51.51173391474148, -0.116729736328125], 10);
    var featureGroup;

    var geom = geometryField.val();
    if (geom) {
        featureGroup = L.geoJson({type: 'Feature', geometry: JSON.parse(geom)}).addTo(map);
        map.fitBounds(featureGroup.getBounds());
    } else {
        featureGroup = L.featureGroup().addTo(map);
    }

    var drawControl = new L.Control.Draw({
        draw: {
            polyline: false,
            rectangle: false,
            circle: false,
            marker: false
        },
        edit: {
            featureGroup: featureGroup
        }
    }).addTo(map);

    map.on('draw:created', function(e) {
        featureGroup.clearLayers();
        featureGroup.addLayer(e.layer);
        geometryField.val(JSON.stringify(e.layer.toGeoJSON().geometry));
    });

    map.on('draw:edited', function(e) {
        var layers = e.layers;
        layers.eachLayer(function (layer) {
            geometryField.val(JSON.stringify(layer.toGeoJSON().geometry));
        });
    });

    map.on('draw:deleted', function() {
        geometryField.val();
    });
}());
