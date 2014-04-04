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
        $('#map').removeClass('col-sm-12').addClass('col-sm-6');

        var feature = event.target.feature;

        function handleObservationtypeSuccess(response) {
            $('#info').remove();
            var target = $('<div class="col-sm-6" id="info"></div>');
            target.append('<h4>'+ response.name +'</h4>');
            target.append('<p>'+ response.description +'</p>');

            var table = $('<table class="table table-striped"><tr><th>Field name</th><th>Value</th></tr></table>');
            for (var i = 0, len = response.fields.length; i < len; i++) {
                var field = response.fields[i];
                var value = (feature.properties[field.key] ? feature.properties[field.key] : '—');

                switch (field.fieldtype) {
                    case 'lookup':
                        for (var j = 0, lenj = field.lookupvalues.length; j < lenj; j++) {
                            if (field.lookupvalues[j].id === value) {
                                value = field.lookupvalues[j].name;
                                break;
                            }
                        }
                        break;
                    case 'date':
                        value = moment(value).fromNow() + ' ('+ moment(value).format('llll') +')';
                        break;
                }

                table.append('<tr><td>' + field.name + '</td><td>' + value + '</td></tr>');
            }
            target.append(table);
            $('#map').parent().append(target);
            map.invalidateSize();
        }

        function handleObservationtypeError(response) {
            alert(response);
        }

        Control.Ajax.get('projects/' + projectId + '/observationtypes/' + feature.properties.observationtype + '/', handleObservationtypeSuccess, handleObservationtypeError);

        map.fitBounds([[feature.geometry.coordinates[1], feature.geometry.coordinates[0]]]);
    }

    function handleDataLoadSuccess(response) {
        var dataLayer = L.geoJson(response, {
            onEachFeature: function (feature, layer) {
                layer.on('click', showFeatureInfo);
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