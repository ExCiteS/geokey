(function (global) {
	function MessageDisplay (container) {
		this.container = $(container);
	}

	MessageDisplay.prototype.showMessage = function showError(type, message) {
		var html = $('<div class="col-md-12"><div class="alert alert-' + type + '">' + message + '</div></div>').hide();
		this.container.prepend(html);
		html.show('slow').delay(5000).hide('slow', function() {
			html.remove();
		});

	}

	MessageDisplay.prototype.showSuccess = function showSuccess(message) {
		this.showMessage('success', message);
	}

	MessageDisplay.prototype.showError = function showError(message) {
		this.showMessage('danger', message);
	}

	global.MessageDisplay = MessageDisplay;
}(window.Ui ? window.Ui : window.Ui = {}));