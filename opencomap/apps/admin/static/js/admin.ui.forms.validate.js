$(function() {
	var form = $('form').not('#description-form');

	/**
	 * Displays a help text beneath invalid fields. 
	 * @param  {Object} field   The invalid field
	 * @param  {String} message The message to display.
	 */
	function showHelp(field, message) {
		field.siblings('.help-block').remove();
		field.after('<span class="help-block">' + message  + '</span>');
	}

	/**
	 * Validates a frorm using standard form.checkValidity(). If valid, the form is submitted. 
	 * If not, invalid fields are marked and a help text is provided. 
	 */
	function validate() {
		if (this.checkValidity()) {
			// The form is valid, submit the thing
			if (form.attr('method') && form.attr('action')) {
				$(this).off('submit');
				$(this).submit();
			}
		} else {
			// The form is invalid
			var validFields = $(this).find(':valid');
			var invalidFields = $(this).find(':invalid');

			for (var i = 0, len = invalidFields.length; i < len; i++) {
				var field = $(invalidFields[i])
				var validity = invalidFields[i].validity
				field.parents('.form-group').addClass('has-error');

				if (validity.valueMissing) {
					if (field.prop('tagName') === 'SELECT') { showHelp(field, 'Please select a value.'); }
					else { showHelp(field, 'This field is required.'); }
				}

				if (!validity.valueMissing) {
					switch (field.attr('type')) {
						case 'email':
							if (validity.typeMismatch) { showHelp(field, 'Please insert a valid email address; e.g., kermit@muppets.co.uk.'); }
							break;
						case 'number':
							if (validity.badInput) { showHelp(field, 'Your input contains non-numeric characters. Maybe you used a comma (,) as decimal point?'); }
							if (validity.stepMismatch) { showHelp(field, 'You entered more than three digits after the decimal point.'); }
							break;
					}
				}
			}

			// Remove help blocks and error state from valid fields
			validFields.siblings('.help-block').remove();
			validFields.parents('.form-group').removeClass('has-error');
		}

		event.preventDefault();
	}

	function reset() {
		form.find('.form-group').removeClass('has-error');
		form.find('.help-block').remove();
		form.find(':required').after('<span class="help-block">This field is required.</span>')

	}

	form.submit(validate);
	$('button[type="reset"]').click(reset);
}());