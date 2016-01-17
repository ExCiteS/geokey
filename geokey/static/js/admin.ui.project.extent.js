/* ***********************************************
 * Adds map and and drawing functionality to defined geographic extents for
 * projects. All functionality is based on Leaflet and Leaflet.Draw.
 *
 * Used in:
 * - templates/projects/project_extent.html
 * ***********************************************/

$(function () {
    'use strict';

    var geometryField = $('#geometry');

    // initialise the map
    window.map = L.map('map').setView([51.51173391474148, -0.116729736328125], 10);
    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(window.map);
    var featureGroup;

    // Put extent on the map, if it exists
    var geom = geometryField.val();
    if (geom) {
        featureGroup = L.geoJson({type: 'Feature', geometry: JSON.parse(geom)}).addTo(window.map);
        window.map.fitBounds(featureGroup.getBounds());
    } else {
        featureGroup = L.featureGroup().addTo(window.map);
    }

    // initialise draw control
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
    }).addTo(window.map);

    // handle new geometry
    window.map.on('draw:created', function(e) {
        featureGroup.clearLayers();
        featureGroup.addLayer(e.layer);
        geometryField.val(JSON.stringify(e.layer.toGeoJSON().geometry));
    });

    // handle edited geometry
    window.map.on('draw:edited', function(e) {
        var layers = e.layers;
        layers.eachLayer(function (layer) {
            geometryField.val(JSON.stringify(layer.toGeoJSON().geometry));
        });
    });

    // handle deleted geometry
    window.map.on('draw:deleted', function() {
        geometryField.val('');
    });
}());
