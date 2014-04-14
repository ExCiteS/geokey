/* ***********************************************
 * Displays a map using Leaflet
 *
 * @author Oliver Roick (http://github.com/oliverroick)
 * @version 0.1
 * ***********************************************/

$(function() {
    'use strict';

    // Reads the IDs from the body's attributes
    var projectId = $('body').attr('data-project-id'),
        viewId = $('body').attr('data-view-id');

    var url = 'projects/' + projectId + '/views/' + viewId + '/data/';

    var map = L.map('map', {
        center: [51.505, -0.09],
        zoom: 13,
        zoomControl: false
    });

    // add an OpenStreetMap tile layer
    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    function showFeatureInfo(event) {
        $('#map').removeClass('col-sm-12').addClass('col-sm-4');

        var feature = event.target.feature;

        function handleObservationtypeSuccess(response) {
            $('#info').remove();
            var context = {
                feature: feature,
                observationtype: response
            };
            $('#map').parent().append(Templates.observationinfo(context));
            map.invalidateSize();
        }

        function handleObservationtypeError(response) {
            alert(response);
        }

        Control.Ajax.get('projects/' + projectId + '/observationtypes/' + feature.properties.observationtype + '/', handleObservationtypeSuccess, handleObservationtypeError);

        map.fitBounds(L.featureGroup([L.geoJson(feature)]).getBounds());
    }

    function handleDataLoadSuccess(response) {
        var dataLayer = L.geoJson(response, {
            onEachFeature: function (feature, layer) {
                layer.bindPopup(Templates.observation(feature));
                // layer.on('click', showFeatureInfo);
            }
        });
        map.fitBounds(dataLayer.getBounds());
        dataLayer.addTo(map);
    }

    function handleDataLoadError(response) {
        alert(response);
    }

    Control.Ajax.get(url, handleDataLoadSuccess, handleDataLoadError);
});