$(function() {
	var projectId = $('body').attr('data-project-id'),
		viewId = $('body').attr('data-view-id');
		groupId = $('body').attr('data-group-id');

	var url = 'projects/' + projectId + '/views/' + viewId + '/usergroups/' + groupId;
	
	var usergroupPanel =  new Ui.Usergroup('#users #members', projectId, viewId),
		messages = new Ui.MessageDisplay('#users');

	function handlePermissionChange(event) {
		var data = {};
		var target = $(event.target).parents('.checkbox');

		function handleGroupUpdateError(response) {
			messages.showError('An error occurred while updating permissions of this user group. Error text was: ' + response.responseJSON.error);
			target.prepend('<span class="glyphicon glyphicon-remove text-danger"></span>').delay(5000).queue(function() {
				$(this).children('span.glyphicon').remove();
				$(this).dequeue();
			});
		}

		function handleGroupUpdateSuccess(response) {
			target.prepend('<span class="glyphicon glyphicon-ok text-success"></span>').delay(2000).queue(function() {
				$(this).children('span.glyphicon').remove();
				$(this).dequeue();
			});
		}

		data[event.target.name] = $(event.target).prop('checked');
		Control.Ajax.put(url, handleGroupUpdateSuccess, handleGroupUpdateError, data);
	}

	$('#permissions input[type="checkbox"]').change(handlePermissionChange);
});