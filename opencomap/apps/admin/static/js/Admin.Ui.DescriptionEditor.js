$(function() {
	var $editLink = $('a#edit');
	var $descriptionText = $('div.page-header h1 small');

	var $descriptionForm = $('#description-form');
	var $descriptionFormField = $('#description-form #description');
	var $descriptionFormCancel = $('#description-form button[type="button"]');
	var $submitbtn = $('form button[type="submit"]');

	function toggle() {
		$descriptionText.toggle();
		$descriptionForm.toggle();
	}

	function handleRequestSucess(response) {
		responseJson = JSON.parse(response);
		$descriptionFormField.val(responseJson.description);
		$descriptionText.children('#descriptionText').text(responseJson.description);

		$submitbtn.button('reset');
		toggle();

		$descriptionFormField.removeClass('loading');
	}

	function handleRequestError() {
		$submitbtn.button('reset');
		
		// TODO: Display error message
		
		toggle();
		$descriptionFormField.removeClass('loading');
	}

	function handleDescriptionSubmit(event) {
		var projectId = $('body').attr('data-project-id');
		var form = $(this);
		
		$submitbtn.button('loading');
		$descriptionFormField.addClass('loading');
		Control.Ajax.post('/api/ajax/project/' + projectId + '/update', handleRequestSucess, handleRequestError, form.serialize());

		event.preventDefault();
	}

	$descriptionForm.hide();
	$editLink.click(toggle);
	$descriptionFormCancel.click(toggle);
	$descriptionForm.submit(handleDescriptionSubmit);
});