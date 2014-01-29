(function (global) {
	function Usergroup(panel, projectId, viewId) {
		var panel = $(panel);
		this.typeAwayResults = panel.find('.panel-footer .type-away');
		this.formField = panel.find('.panel-footer input[type="text"]');
		this.formField.keyup(this.handleFormType.bind(this));
		this.userList = panel.find('.user-list');
		this.messages = new Ui.MessageDisplay('#users');

		var groupId = panel.attr('data-group-id');
		this.url = 'projects/' + projectId + '/usergroups/' + groupId;
		this.numberOfRequests = 0;
		this.userList.find('li a.remove').click(this.handleRemoveUser.bind(this));
	}

	Usergroup.prototype.handleRemoveUser = function handleRemoveUser(event) {
		var userId = $(event.target).attr('data-user-id');
		var itemToRemove = $(event.target).parent('.list-group-item');

		function handleRemoveUserSuccess() {
			itemToRemove.remove();
			this.messages.showSuccess('The user has been removed successfully.');
		}

		function handleRemoveUserError(response) {
			this.messages.showError('An error occured while removing the user. Error text was: ' + response.responseJSON.error);
		}

		Control.Ajax.del(this.url + '/users/' + userId, handleRemoveUserSuccess.bind(this), handleRemoveUserError.bind(this), {'userId': userId});
	}


	Usergroup.prototype.handleAddUserSucess = function handleAddUserSucess(response) {
		var users = response.usergroup.users;

		this.userList.empty();
		for (var i = 0, len = users.length; i < len; i++) {
			var user = users[i];
			this.userList.append('<li class="list-group-item">' + user.first_name + ' ' + user.last_name + ' (<a class="text-danger remove" data-user-id="' + user.id + '" href="#">remove</a>)</li>')
		}
		this.userList.find('li a.remove').click(this.handleRemoveUser.bind(this));
		this.messages.showSuccess('The user has been added successfully.');
	}

	Usergroup.prototype.handleAddUserError = function handleAddUserError(response) {
		this.messages.showError('An error occured while adding the user. Error text was: ' + response.responseJSON.error);
	}

	Usergroup.prototype.handleAddUser = function handleAddUser(event) {
		var userId = $(event.target).attr('data-user-id');

		this.typeAwayResults.hide();
		this.formField.val('');
		Control.Ajax.put(this.url, this.handleAddUserSucess.bind(this), this.handleAddUserError.bind(this), {'userId': userId});
	}




	Usergroup.prototype.handleSuccess = function handleSuccess(response) {
		var users = response.users;
		var header = (users.length > 0 ? 'Click on item to add user' : 'No records matched your query');

		this.typeAwayResults.children().not('.dropdown-header').remove();
		this.numberOfRequests--;
		if (this.numberOfRequests === 0) {
			this.formField.removeClass('loading');
		}
		
		for (var i = 0, len = users.length; i < len; i++) {
			this.typeAwayResults.append('<li role="presentation"><a role="menuitem" tabindex="-1" href="#" data-user-id="' + users[i].id + '">' + users[i].first_name + ' ' + users[i].last_name + '</a></li>');
		}
		
		this.typeAwayResults.children('.dropdown-header').text(header);
		this.typeAwayResults.find('li a').click(this.handleAddUser.bind(this));
		this.typeAwayResults.show();
	}

	Usergroup.prototype.handleError = function handleError(response) {
		this.numberOfRequests--;
		if (this.numberOfRequests === 0) {
			this.formField.removeClass('loading');
		}
		this.typeAwayResults.children().not('.dropdown-header').remove();
		this.typeAwayResults.children('.dropdown-header').html('<span class="text-danger">An error occured while trying to retrieve the user list. Please try again.</span>');
		this.typeAwayResults.show();
	}

	Usergroup.prototype.handleFormType = function handleFormType(event) {
		if (event.target.value.length === 0) {
			this.typeAwayResults.hide();
		} else if (event.target.value.length >= 3) {
			this.formField.addClass('loading');
			this.numberOfRequests++;
			Control.Ajax.get('users?query=' + event.target.value, this.handleSuccess.bind(this), this.handleError.bind(this));
		}
	}

	global.Usergroup = Usergroup;
}(window.Ui ? window.Ui : window.Ui = {}));