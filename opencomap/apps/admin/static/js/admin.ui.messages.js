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
	 * @param {String} container Optional. The HTML element id if the element in which the messages shall be displayed.
	 */
	function MessageDisplay (container) {
		if (container) {
			this.container = $(container);	
		}
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

	/**
	 * Displays a message within a panel above an element. 
	 * @param  {String}  type      Class name of the error message alert. Currently accepts 'success' and 'danger. for errors.
	 * @param  {Element} container The element above which the message is displayed.
	 * @param  {String}  message   The message text
	 */
	MessageDisplay.prototype.showPanelMessage = function showPanelMessage(type, container, message) {	
		var html = $('<div class="alert alert-' + type + '">' + message + '</div>').hide();
		container.prepend(html);
		
		html.show('slow').delay(5000).hide('slow', function() {
			html.remove();
		});
	};

	/**
	 * Displays a success message within a panel above an element. 
	 * @param  {Element} container The element above which the message is displayed.
	 * @param  {String}  message   The message text
	 */
	MessageDisplay.prototype.showPanelSuccess = function showPanelSuccess(container, message) {	
		this.showPanelMessage('success', container, message);
	};

	/**
	 * Displays a error message within a panel above an element. 
	 * @param  {Element} container The element above which the message is displayed.
	 * @param  {String}  message   The message text
	 */
	MessageDisplay.prototype.showPanelError = function showPanelError(container, message) {	
		this.showPanelMessage('danger', container, message);
	};

	/**
	 * Displays a little green tick within an element as indicator for an successful actions. 
	 * @param  {Element} container The element in which the tick is displayed.
	 */
	MessageDisplay.prototype.showInlineSuccess = function showInlineSuccess(container) {
		container.addClass('success');
		setTimeout(function () {
			container.removeClass('success');
		}.bind(this), 3000);
	};

	/**
	 * Displays a error message within a panel. 
	 * @param  {Element} container The element above which the message is displayed.
	 * @param  {String}  message   The message text
	 */
	MessageDisplay.prototype.showInlineError = function showInlineError(container, message) {
		var html = $('<p class="error text-danger">' + message + '</p>').hide();
		container.append(html);
		html.show('slow').delay(5000).hide('slow', function() {
			html.remove();
		});
	};

	global.MessageDisplay = MessageDisplay;
}(window.Ui ? window.Ui : window.Ui = {}));