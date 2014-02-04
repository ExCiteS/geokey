$(function() {
	var messages = new Ui.MessageDisplay('.page-header');

	var descriptionText = $('div.page-header p.lead'),
		descriptionForm = $('#description-form'),
		descriptionFormField = $('#description-form #description'),
		descriptionFormCancel = $('#description-form button[type="button"]'),
		submitbtn = $('form#description-form button[type="submit"]');

	var projectId = $('body').attr('data-project-id'),
		featuretypeId = $('body').attr('data-featuretype-id'),
		fieldId = $('body').attr('data-field-id');
		viewId = $('body').attr('data-view-id');
		groupId = $('body').attr('data-group-id');

	var url = 'projects/' + projectId;
	if (projectId && viewId) { url += '/views/' + viewId; }
	if (projectId && viewId && groupId) { url += '/usergroups/' + groupId; }
	if (projectId && featuretypeId) { url += '/featuretypes/' + featuretypeId; }
	if (projectId && featuretypeId && fieldId) { url += '/fields/' + fieldId; }

	function toggle() {
		descriptionText.toggleClass('hidden');
		descriptionForm.toggleClass('hidden')
	}

	function handleRequestSucess(response) {
		console.log(response);
		var resultAccessor = 'project';
		if (featuretypeId) { resultAccessor = 'featuretype'; }
		if (fieldId) { resultAccessor = 'field'; }
		if (viewId) { resultAccessor = 'view'; }
		if (groupId) { resultAccessor = 'usergroup'; }

		descriptionFormField.val(response[resultAccessor].description);
		descriptionText.children('#descriptionText').text(response[resultAccessor].description);

		toggle();
		submitbtn.button('reset');
		descriptionFormField.removeClass('loading');
	}

	function handleRequestError(response) {
		submitbtn.button('reset');
		messages.showError('An error occurred while updating the description. Error text was: ' + response.responseJSON.error, true);
		descriptionFormField.removeClass('loading');
	}

	function handleDescriptionSubmit(event) {
		submitbtn.button('loading');
		descriptionFormField.addClass('loading');
		Control.Ajax.put(url, handleRequestSucess, handleRequestError, {'description': descriptionFormField.val()});

		event.preventDefault();
	}

	$('button#edit').click(toggle);
	descriptionFormCancel.click(toggle);
	descriptionForm.submit(handleDescriptionSubmit);
});