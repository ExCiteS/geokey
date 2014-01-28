(function (global) {
	var baseUrl = '/ajax/';

	function Ajax() {
		
	}

	function getCookie(name) {
		var cookieValue = null;
		if (document.cookie && document.cookie != '') {
			var cookies = document.cookie.split(';');
			for (var i = 0; i < cookies.length; i++) {
				var cookie = jQuery.trim(cookies[i]);
				// Does this cookie string begin with the name we want?
				if (cookie.substring(0, name.length + 1) == (name + '=')) {
					cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
					break;
				}
			}
		}
	    return cookieValue;
	}

	function setHeader(xhr) {
		xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
	}

	function request(url, method, successCallback, errorCallback, data) {
		$.ajax({
			url: baseUrl + url,
			method: method,
			xhrFields: {
				withCredentials: true
			},
			success: successCallback,
			error: errorCallback,
			data: JSON.stringify(data),
			beforeSend: setHeader,
			contentType: 'application/json; charset=utf-8'
		});
	}

	Ajax.prototype.get = function get(url, successCallback, errorCallback) {
		request(url, 'GET', successCallback, errorCallback);
	}

	Ajax.prototype.put = function put(url, successCallback, errorCallback, data) {
		request(url, 'PUT', successCallback, errorCallback, data);
	}

	Ajax.prototype.del = function del(url, successCallback, errorCallback) {
		request(url, 'DELETE', successCallback, errorCallback);
	}

	global.Ajax = new Ajax();
}(window.Control ? window.Control : window.Control = {}));