(function (global) {
	function MessageDisplay (container) {
		this.container = $(container);
	}

	MessageDisplay.prototype.showMessage = function showError(type, message, append) {
		var html = $('<div class="col-sm-12"><div class="alert alert-' + type + '">' + message + '</div></div>').hide();
		append ? this.container.append(html) : this.container.prepend(html);
		
		html.show('slow').delay(5000).hide('slow', function() {
			html.remove();
		});

	}

	MessageDisplay.prototype.showSuccess = function showSuccess(message, append) {
		this.showMessage('success', message, append);
	}

	MessageDisplay.prototype.showError = function showError(message, append) {
		this.showMessage('danger', message, append);
	}

	global.MessageDisplay = MessageDisplay;
}(window.Ui ? window.Ui : window.Ui = {}));