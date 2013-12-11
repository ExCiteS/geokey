$(function() {
	var map = L.map('map', {
		center: [51.505, -0.09],
    	zoom: 13,
		zoomControl: false
	});

	// add an OpenStreetMap tile layer
	L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
    	attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
	}).addTo(map);
});