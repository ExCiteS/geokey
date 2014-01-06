$(function() {
	var $editLink = $('a#edit');
	var $descriptionText = $('div.page-header h1 small');

	var $descriptionForm = $('#description-form');
	var $descriptionFormField = $('#description-form #description');
	var $descriptionFormCancel = $('#description-form button[type="button"]');

	function toggle() {
		$descriptionText.toggle();
		$descriptionForm.toggle();
	}

	function handleDescriptionSubmit(event) {
		var projectId = $('body').attr('data-project-id');
		var form = $(this);
		var submitbtn = $('form button[type="submit"]');
		
		submitbtn.button('loading');
		$.ajax({
			url: '/api/ajax/project/' + projectId + '/update',
			method: 'POST',
			data: form.serializeArray(),
			xhrFields: {
				withCredentials: true
			},
			beforeSend: function() {
				$descriptionFormField.addClass('loading');
			},
			complete: function() {
				$descriptionFormField.removeClass('loading');
			},
			success: function (response) {
				responseJson = JSON.parse(response);
				$descriptionFormField.val(responseJson.description);
				$descriptionText.children('#descriptionText').text(responseJson.description);

				submitbtn.button('reset');
				toggle();
			},
			error: function (response) {
				submitbtn.button('reset');
				console.log('error');
				// TODO: Create porper error on server side
				
				toggle();
			}
		});

		event.preventDefault();
	}

	$descriptionForm.hide();
	$editLink.click(toggle);
	$descriptionFormCancel.click(toggle);
	$descriptionForm.submit(handleDescriptionSubmit);
});