$(function() {
	var $_form = $('form');

	/**
	 * Validates a frorm using standard form.checkValidity(). If valid, the form is submitted. 
	 * If not, invalid fields are marked and a help text is provided. 
	 * @param  {Object} event The form submit event.
	 */
	function validate(event) {
		if (this.checkValidity()) {
			// The form is valid, submit the thing
			$(this).off('submit');
			$(this).submit();
		} else {
			// The form is invalid
			var validFields = $(this).find(':valid');
			var invalidFields = $(this).find(':invalid');

			for (var i = 0, len = invalidFields.length; i < len; i++) {
				var field = $(invalidFields[i])
				var validity = invalidFields[i].validity
				field.parents('.form-group').addClass('has-error');

				if (!validity.valueMissing && validity.typeMismatch) {
					if (field.attr('type') === 'email') {
						field.siblings('.help-block').remove();
						field.after('<span class="help-block">Please insert a valid email address; e.g., kermit@muppets.co.uk.</span>');
					}
				}
			}

			// Remove help blocks and error state from valid fields
			validFields.siblings('.help-block').remove();
			validFields.parents('.form-group').removeClass('has-error');
		}

		event.preventDefault();
	}

	$_form.submit(validate);
}());