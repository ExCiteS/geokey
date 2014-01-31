$(function() {
	var projectId = $('body').attr('data-project-id'),
		featuretypeId = $('body').attr('data-featuretype-id'),
		fieldId = $('body').attr('data-field-id'),
		url = 'projects/' + projectId + '/featuretypes/' + featuretypeId + '/fields/' + fieldId;

	var lookupPanel = ($('#lookupValuesPanel').length !== 0 ? new Ui.LookupPanel('#lookupValuesPanel', url) : undefined);
	var valuesSubmitBtn = $('form#valuesForm button[type="submit"]');
	var messages = new Ui.MessageDisplay('#constraints');
	
	function handleNumericUpdateError(response) {
		valuesSubmitBtn.button('reset');
		messages.showError('An error occured while updating the field. Error text was: ' + response.responseJSON.error + '.')
	}

	function handleNumericUpdateSuccess(response) {
		$('form#valuesForm input[name="minval"]').attr('value', response.field.minval);
		$('form#valuesForm input[name="maxval"]').attr('value', response.field.maxval);
		valuesSubmitBtn.button('reset');
		messages.showSuccess('The field has been updated with new minumum and maximum values.')
	}

	function submitForm() {
		if (this.checkValidity()) {
			valuesSubmitBtn.button('loading');
			var form = $(this).serializeArray();
			var values = {};
			for (var i = 0, len = form.length; i < len; i++) {
				values[form[i].name] = (parseFloat(form[i].value) || null);
			}
			Control.Ajax.put(url, handleNumericUpdateSuccess, handleNumericUpdateError, values);
		}
		event.preventDefault();
	}

	$('form#valuesForm').submit(submitForm);
});