$(function() {
	var messages = new Ui.MessageDisplay('.page-header');

	var descriptionText = $('div.page-header h1 small'),
		descriptionForm = $('#description-form'),
		descriptionFormField = $('#description-form #description'),
		descriptionFormCancel = $('#description-form button[type="button"]'),
		submitbtn = $('form#description-form button[type="submit"]');

	var projectId = $('body').attr('data-project-id'),
		featuretypeId = $('body').attr('data-featuretype-id'),
		fieldId = $('body').attr('data-field-id');

	var url = 'projects/' + projectId;
	if (featuretypeId) { url += '/featuretypes/' + featuretypeId; }
	if (fieldId) { url += '/fields/' + fieldId; }

	function toggle() {
		descriptionText.toggleClass('hidden');
		descriptionForm.toggleClass('hidden')
	}

	function handleRequestSucess(response) {
		var resultAccessor = 'project';
		if (featuretypeId) { resultAccessor = 'featuretype'; }
		if (fieldId) { resultAccessor = 'field'; }

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