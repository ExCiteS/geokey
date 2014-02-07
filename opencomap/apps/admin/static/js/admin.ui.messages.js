/* ***********************************************
 * Module to display messages on the Ui. Can be instanciated using new Ui.MessageDisplay('#container')
 *
 * @author Oliver Roick (http://github.com/oliverroick)
 * @version 0.1
 * ***********************************************/

(function (global) {
	'use strict';

	/**
	 * Constructor
	 * @param {String} container The HTML element id if the element in which the messages shall be displayed.
	 */
	function MessageDisplay (container) {
		this.container = $(container);
	}

	/**
	 * Displays the message
	 * @param  {String} type     Class name of the error message alert. Currently accepts 'success' and 'danger. for errors.
	 * @param  {String} message  The message text
	 * @param  {Boolean} append  Optional. If true the message will be appended to the container, otherwise it will be inserted as the first element in the container. 
	 */
	MessageDisplay.prototype.showMessage = function showError(type, message, append) {
		var html = $('<div class="col-sm-12"><div class="alert alert-' + type + '">' + message + '</div></div>').hide();
		if (append) { this.container.append(html); }
		else { this.container.prepend(html); }
		
		html.show('slow').delay(5000).hide('slow', function() {
			html.remove();
		});
	};

	/**
	 * Displays a success message
	 * @param  {String} message  The message text
	 * @param  {Boolean} append  Optional. If true the message will be appended to the container, otherwise it will be inserted as the first element in the container. 
	 */
	MessageDisplay.prototype.showSuccess = function showSuccess(message, append) {
		this.showMessage('success', message, append);
	};

	/**
	 * Displays a error message
	 * @param  {String} message  The message text
	 * @param  {Boolean} append  Optional. If true the message will be appended to the container, otherwise it will be inserted as the first element in the container. 
	 */
	MessageDisplay.prototype.showError = function showError(message, append) {
		this.showMessage('danger', message, append);
	};

	global.MessageDisplay = MessageDisplay;
}(window.Ui ? window.Ui : window.Ui = {}));