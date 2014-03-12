/* ***********************************************
 * Validates form accroding to the definition in the HTML.
 * Is automatically loaded when included in a page.
 *
 * @author Oliver Roick (http://github.com/oliverroick)
 * @version 0.1
 * ***********************************************/

$(function() {
	'use strict';

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
	 * @param  {Event} event The form submission event.
	 */
	function validate(event) {
		var formSumitted = event.target;
		if (formSumitted.checkValidity()) {
			// The form is valid, submit the thing
			if (form.attr('method') && form.attr('action')) {
				$(formSumitted).off('submit');
				$(formSumitted).submit();
			}
		} else {
			// The form is invalid
			var validFields = $(formSumitted).find(':valid');
			var invalidFields = $(formSumitted).find(':invalid');

			// Iterate through all invlaid fields and display an error message
			for (var i = 0, len = invalidFields.length; i < len; i++) {
				var field = $(invalidFields[i]);
				var validity = invalidFields[i].validity;
				field.parents('.form-group').addClass('has-error');

				if (validity.valueMissing) {
					if (field.prop('tagName') === 'SELECT') { showHelp(field, 'Please select a value.'); }
					else { showHelp(field, 'This field is required.'); }
				}

				if (!validity.valueMissing) {
					switch (field.attr('type')) {
						case 'url':
							if (validity.typeMismatch) { showHelp(field, 'Please enter a valid URL; e.g., http://example.com.'); }
							break;
						case 'email':
							if (validity.typeMismatch) { showHelp(field, 'Please enter a valid email address; e.g., name@example.com.'); }
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

	/**
	 * Resets the form to its initial state. Removes all error messages.
	 */
	function reset() {
		form.find('.form-group').removeClass('has-error');
		form.find('.help-block').remove();
		form.find(':required').after('<span class="help-block">This field is required.</span>');
	}

	form.submit(validate);
	$('button[type="reset"]').click(reset);
}());