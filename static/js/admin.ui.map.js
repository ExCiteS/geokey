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

	function handleDataLoadSuccess(response) {
		console.log(response);
	}

	function handleDataLoadError(response) {
		console.log(response);
	}

	Control.Ajax.get(url, handleDataLoadSuccess, handleDataLoadError);
});