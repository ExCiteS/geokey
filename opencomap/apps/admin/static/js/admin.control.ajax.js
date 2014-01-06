(function (global) {
	function Ajax() {
		
	}

	function request(url, method, successCallback, errorCallback, data) {
		$.ajax({
			url: url,
			method: method,
			xhrFields: {
				withCredentials: true
			},
			success: successCallback,
			error: errorCallback,
			data: data
		});
	}

	Ajax.prototype.get = function get(url, successCallback, errorCallback) {
		request(url, 'GET', successCallback, errorCallback);
	}

	Ajax.prototype.post = function get(url, successCallback, errorCallback, data) {
		request(url, 'POST', successCallback, errorCallback, data);
	}

	global.Ajax = new Ajax();
}(window.Control ? window.Control : window.Control = {}));