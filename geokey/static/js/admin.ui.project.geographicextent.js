/* ***********************************************
 * Adds map and and drawing functionality to
 * defined geographic extents of projects.
 *
 * Used in:
 * - projects/project_geographicextent.html
 * ***********************************************/

$(function() {
    'use strict';

    var geometryField = $('#geometry');

    // Initialise the map
    window.map = L.map('map').setView([0, 0], 1);

    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(window.map);

    var featureGroup;

    // Put extent on the map (if it exists)
    var geometry = geometryField.val();

    if (geometry) {
        featureGroup = L.geoJson({
            type: 'Feature',
            geometry: JSON.parse(geometry)
        }).addTo(window.map);

        window.map.fitBounds(featureGroup.getBounds());
    } else {
        featureGroup = L.featureGroup().addTo(window.map);
    }

    // Initialise draw control (only if project is not locked)
    if ($('body').data('project-locked') != 'True') {
        new L.Control.Draw({
            draw: {
                marker: false,
                polyline: false,
                polygon: true,
                rectangle: false,
                circle: false
            },
            edit: {
                featureGroup: featureGroup
            }
        }).addTo(window.map);
    }

    // Handle new geometry
    window.map.on('draw:created', function(e) {
        featureGroup.clearLayers().addLayer(e.layer);
        geometryField.val(JSON.stringify(e.layer.toGeoJSON().geometry));
    });

    // Handle edited geometry
    window.map.on('draw:edited', function(e) {
        var layers = e.layers;

        layers.eachLayer(function(layer) {
            geometryField.val(JSON.stringify(layer.toGeoJSON().geometry));
        });
    });

    // Handle deleted geometry
    window.map.on('draw:deleted', function() {
        geometryField.val('');
    });
}());
