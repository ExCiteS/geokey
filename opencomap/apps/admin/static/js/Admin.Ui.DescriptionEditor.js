$(function() {
	var $editLink = $('a#edit');
	var $descriptionText = $('div.page-header h1 small');

	var $descriptionForm = $('#description-form');
	var $descriptionFormCancel = $('#description-form button[type="button"]');

	function handleEditClick(event) {
		$descriptionText.hide();
		$descriptionForm.show();
	}

	function handleCancelClick(event) {
		$descriptionText.show();
		$descriptionForm.hide();
	}

	function handleDescriptionSubmit(event) {
		var description = $('#description-form input#description').val();
		console.log('Description value: ' + description);
		// TODO: Implement saving to server
		event.preventDefault();
	}

	$descriptionForm.hide();
	$editLink.click(handleEditClick);
	$descriptionFormCancel.click(handleCancelClick);
	$descriptionForm.submit(handleDescriptionSubmit);
});