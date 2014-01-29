$(function() {
	var descriptionText = $('div.page-header h1 small');

	var descriptionForm = $('#description-form');
	var descriptionFormField = $('#description-form #description');
	var descriptionFormCancel = $('#description-form button[type="button"]');
	var submitbtn = $('form button[type="submit"]');

	function toggle() {
		descriptionText.toggleClass('hidden');
		descriptionForm.toggleClass('hidden')
	}

	function handleRequestSucess(response) {
		console.log(response);
		descriptionFormField.val(response.project.description);
		descriptionText.children('#descriptionText').text(response.project.description);

		submitbtn.button('reset');
		toggle();

		descriptionFormField.removeClass('loading');
	}

	function handleRequestError() {
		submitbtn.button('reset');
		
		// TODO: Display error message
		
		toggle();
		descriptionFormField.removeClass('loading');
	}

	function handleDescriptionSubmit(event) {
		var projectId = $('body').attr('data-project-id');
		
		submitbtn.button('loading');
		descriptionFormField.addClass('loading');
		Control.Ajax.put('projects/' + projectId, handleRequestSucess, handleRequestError, {'description': descriptionFormField.val()});

		event.preventDefault();
	}

	$('a#edit').click(toggle);
	descriptionFormCancel.click(toggle);
	descriptionForm.submit(handleDescriptionSubmit);
});