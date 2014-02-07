/* ***********************************************
 * Mangages the members of user groups. 
 *
 * @author Oliver Roick (http://github.com/oliverroick)
 * @version 0.1
 * ***********************************************/

(function (global) {
	'use strict';

	/**
	 * Constructor
	 * @param {[type]} panelId   The HTML element id of the usergroup ui
	 * @param {[type]} projectId The project id of the usergroup
	 * @param {[type]} viewId    Optional. The view id of the usergroup
	 */
	function Usergroup(panelId, projectId, viewId) {
		var panel = $(panelId);
		var groupId = panel.attr('data-group-id');

		// Get the elements
		this.typeAwayResults = panel.find('.panel-footer .type-away');
		this.formField = panel.find('.panel-footer input[type="text"]');
		this.userList = panel.find('.user-list');
		this.messages = new Ui.MessageDisplay('#users');

		// Build the request url
		this.url = 'projects/' + projectId + '/usergroups/' + groupId + '/users';
		if (viewId) { this.url = 'projects/' + projectId + '/views/' + viewId + '/usergroups/' + groupId + '/users'; }

		this.numberOfRequests = 0;
		
		// Register the click event handler of remove links
		this.userList.find('li a.remove').click(this.handleRemoveUser.bind(this));

		// Register the keyup event on the text field. 
		this.formField.keyup(this.handleFormType.bind(this));
	}

	/**
	 * Returns the user name display to be used in type away drop down and in the user list
	 * @param  {Object} user The user to be displayed
	 */
	function getUserDisplay(user) {
		var username = user.username;
		if (user.first_name || user.last_name) {
			username += ' (';
			if (user.first_name) {username += user.first_name; }
			if (user.first_name && user.last_name) {username += ' '; }
			if (user.last_name) {username += user.last_name; }
			username += ')';
		}
		return username;
	}

	/**
	 * Handles the click event when the user clicks on the remove link in the user list.
	 * @param  {Event} event The click event fired by the link.
	 */
	Usergroup.prototype.handleRemoveUser = function handleRemoveUser(event) {
		var userId = $(event.target).parent('a').attr('data-user-id');
		var itemToRemove = $(event.target).parents('.list-group-item');

		/**
		 * Handles the response after the removal of the user from the group was successful. 
		 */
		function handleRemoveUserSuccess() {
			itemToRemove.remove();
			if (this.userList.children().length === 0) {
				this.userList.append('<li class="list-group-item">No users have been assigned to this group.</li>')
			}
			this.messages.showSuccess('The user has been removed successfully.');
		}

		/**
		 * Handles the response after the removal of the user from the group failed. 
		 * @param  {Object} response JSON object of the response
		 */
		function handleRemoveUserError(response) {
			this.messages.showError('An error occured while removing the user. Error text was: ' + response.responseJSON.error);
		}

		Control.Ajax.del(this.url + '/' + userId, handleRemoveUserSuccess.bind(this), handleRemoveUserError.bind(this), {'userId': userId});
		event.preventDefault();
	};


	/**
	 * Handles the response if the addition of the user to the group was successful. 
	 * @param  {Object} response JSON object of the response
	 */
	Usergroup.prototype.handleAddUserSucess = function handleAddUserSucess(response) {
		var users = response.usergroup.users;

		this.userList.empty();
		for (var i = 0, len = users.length; i < len; i++) {
			var user = users[i];
			this.userList.append('<li class="list-group-item">' + getUserDisplay(user) + ' <a class="text-danger remove" data-user-id="' + user.id + '" href="#"><small>remove</small></a></li>');
		}
		this.userList.find('li a.remove').click(this.handleRemoveUser.bind(this));
		this.messages.showSuccess('The user has been added successfully.');
	};

	/**
	 * Handles the response if the addition of the user to the group failed.
	 * @param  {Object} response JSON object of the response
	 */
	Usergroup.prototype.handleAddUserError = function handleAddUserError(response) {
		this.messages.showError('An error occured while adding the user. Error text was: ' + response.responseJSON.error);
	};

	/**
	 * Handles click events pn items in the user dropdown list. Adds the user to the group.
	 * @param  {Event} event The click event on the user link.
	 */
	Usergroup.prototype.handleAddUser = function handleAddUser(event) {
		var userId = $(event.target).attr('data-user-id');

		this.typeAwayResults.hide();
		this.formField.val('');
		Control.Ajax.put(this.url, this.handleAddUserSucess.bind(this), this.handleAddUserError.bind(this), {'userId': userId});
	};


	
	/**
	 * Handles the reponse the the request for the user list was successful. Updates the dropdown list.
	 * @param  {Object} response JSON object of the response
	 */
	Usergroup.prototype.handleSuccess = function handleSuccess(response) {
		var users = response.users;
		var header = (users.length > 0 ? 'Click on item to add user' : 'No records matched your query');

		this.typeAwayResults.children().not('.dropdown-header').remove();
		this.numberOfRequests--;
		if (this.numberOfRequests === 0) {
			this.formField.removeClass('loading');
		}
		
		for (var i = 0, len = users.length; i < len; i++) {
			this.typeAwayResults.append('<li role="presentation"><a role="menuitem" tabindex="-1" href="#" data-user-id="' + users[i].id + '">' + getUserDisplay(users[i]) + '</a></li>');
		}
		
		this.typeAwayResults.children('.dropdown-header').text(header);
		this.typeAwayResults.find('li a').click(this.handleAddUser.bind(this));
		this.typeAwayResults.show();
	};

	/**
	 * Handles the reponse the the request for the user list failed.
	 */
	Usergroup.prototype.handleError = function handleError() {
		this.numberOfRequests--;
		if (this.numberOfRequests === 0) {
			this.formField.removeClass('loading');
		}
		this.typeAwayResults.children().not('.dropdown-header').remove();
		this.typeAwayResults.children('.dropdown-header').html('<span class="text-danger">An error occured while trying to retrieve the user list. Please try again.</span>');
		this.typeAwayResults.show();
	};

	/**
	 * Handles user type in the search field. Requests for a users list after 3 characters have been typed.
	 * @param  {Event} event The keyup event fired by the field.
	 */
	Usergroup.prototype.handleFormType = function handleFormType(event) {
		if (event.target.value.length === 0) {
			this.typeAwayResults.hide();
		} else if (event.target.value.length >= 3) {
			this.formField.addClass('loading');
			this.numberOfRequests++;
			Control.Ajax.get('users?query=' + event.target.value, this.handleSuccess.bind(this), this.handleError.bind(this));
		}
	};

	global.Usergroup = Usergroup;
}(window.Ui ? window.Ui : window.Ui = {}));