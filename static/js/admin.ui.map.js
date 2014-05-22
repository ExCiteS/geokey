/* ***********************************************
 * Displays a map using Leaflet
 *
 * @author Oliver Roick (http://github.com/oliverroick)
 * @version 0.1
 * ***********************************************/

$(function() {
    'use strict';

    var messages = new Ui.MessageDisplay();

    // Reads the IDs from the body's attributes
    var projectId = $('body').attr('data-project-id'),
        viewId = $('body').attr('data-view-id'),
        mycontributions = $('body').attr('my-contributions');

    var url = 'projects/' + projectId;
    if (viewId) { url += '/views/' + viewId; }
    if (projectId && mycontributions) {
        url += '/mycontributions/';    
    } else {
        url += '/observations/';
    }

    var map = L.map('map', {
        center: [51.505, -0.09],
        zoom: 13,
        zoomControl: false
    });

    // add an OpenStreetMap tile layer
    L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    function handleDataLoadSuccess(response) {
        $('.info-loading').hide('slow', function() { this.remove(); });
        if (response.features.length) {
            var dataLayer = L.geoJson(response, {
                onEachFeature: function (feature, layer) {
                    layer.bindPopup(Templates.observation(feature));
                }
            });
            dataLayer.addTo(map);
            map.fitBounds(dataLayer.getBounds());
        } else {
            messages.showPanelError($('#map').parent(), 'There are no contributions in this view.');
        }
    }

    function handleDataLoadError(response) {
        $('.info-loading').hide('slow', function() { this.remove(); });
        if (response.status === 403) {
            messages.showPanelError($('#map').parent(), 'You are not allowed to access this view. Please select a different view from the list.');
        } else {
            messages.showPanelError($('#map').parent(), 'An Error occurred while loading the observations. Error text was: ' + response.responseJSON.error);
        }
    }

    messages.showPanelLoading($('#map').parent(), 'Loading observations...');
    Control.Ajax.get(url, handleDataLoadSuccess, handleDataLoadError);
});