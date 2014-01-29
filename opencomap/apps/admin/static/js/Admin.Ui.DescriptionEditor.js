$(function() {
	var messages = new Ui.MessageDisplay('.page-header');

	var descriptionText = $('div.page-header h1 small');

	var descriptionForm = $('#description-form');
	var descriptionFormField = $('#description-form #description');
	var descriptionFormCancel = $('#description-form button[type="button"]');
	var submitbtn = $('form button[type="submit"]');

	var projectId = $('body').attr('data-project-id');
	var featuretypeId = $('body').attr('data-featuretype-id');

	var url = 'projects/' + projectId;
	if (featuretypeId) { url += '/featuretypes/' + featuretypeId; }

	function toggle() {
		descriptionText.toggleClass('hidden');
		descriptionForm.toggleClass('hidden')
	}

	function handleRequestSucess(response) {
		var resultAccessor = 'project';
		if (featuretypeId) { resultAccessor = 'featuretype'; }

		descriptionFormField.val(response[resultAccessor].description);
		descriptionText.children('#descriptionText').text(response[resultAccessor].description);

		submitbtn.button('reset');
		toggle();

		descriptionFormField.removeClass('loading');
	}

	function handleRequestError(response) {
		submitbtn.button('reset');
		messages.showError('An error occurred while updating the description. Error text was: ' + response.responseJSON.error, true);
		descriptionFormField.removeClass('loading');
	}

	function handleDescriptionSubmit(event) {
		var projectId = $('body').attr('data-project-id');
		
		submitbtn.button('loading');
		descriptionFormField.addClass('loading');
		Control.Ajax.put(url, handleRequestSucess, handleRequestError, {'description': descriptionFormField.val()});

		event.preventDefault();
	}

	$('a#edit').click(toggle);
	descriptionFormCancel.click(toggle);
	descriptionForm.submit(handleDescriptionSubmit);
});