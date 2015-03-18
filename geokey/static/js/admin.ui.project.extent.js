$(function () {
    'use strict';

    var geometryField = $('#geometry');

    var map = L.map('map').setView([51.51173391474148, -0.116729736328125], 10);
    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
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
        console.log('deleted');
        geometryField.val('');
    });
}());
