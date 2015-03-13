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

    function dateTimeValid(form) {
        var valid = true;
        var dateTimeFields = $(form).find('input.datetime, input.date');

        for (var i = 0, len = dateTimeFields.length; i < len; i++) {
            var field = $(dateTimeFields[i]);

            var min = field.attr('min');
            var max = field.attr('max');

            if (min) { min = Date.parse(min.replace(' ', 'T')); }
            if (max) { max = Date.parse(max.replace(' ', 'T')); }

            var val = Date.parse(field.val().replace(' ', 'T'));

            if (field.val().length && !val) {
                valid = false;
                field.parents('.form-group').addClass('has-error');
                showHelp(field, 'The date entered could not be validated. Please check the entry.');
            } else {
                if (!(min && val ? (val > min): true)) {
                    valid = false;
                    field.parents('.form-group').addClass('has-error');
                    showHelp(field, 'The entered date must be lower than ' + field.attr('min'));
                }

                if (!(max && val ? (val < max): true)) {
                    valid = false;
                    field.parents('.form-group').addClass('has-error');
                    showHelp(field, 'The entered date must be greater than ' + field.attr('max'));
                }
            }
        }
        return valid;
    }

    function emailsValid(form) {
        var valid = true;

        var emailFields = $(form).find('input[type="email"]');
        for (var i = 0, len = emailFields.length; i < len; i++) {
            var email = emailFields[i].value;
            if (email.split('@')[1].indexOf('.') === -1) {
                valid = false;
                $(emailFields[i]).parents('.form-group').addClass('has-error');
                showHelp($(emailFields[i]), 'You forgot to add a top level domain to the address. Please check your input.');
            }
        }

        return valid;
    }

    function urlsValid(form) {
        var valid = true;
        var urlFields = $(form).find('input[type="url"]');

        for (var i = 0, len = urlFields.length; i < len; i++) {
            if (urlFields[i].value) {
                var url = urlFields[i].value.replace(/\s+/g, '');
                urlFields[i].value = url;
                var host = url.replace('http://','').replace('https://','').split(/[/?#]/)[0];
                if (host.indexOf('.') === -1 && host.indexOf('localhost') === -1) {
                    valid = false;
                    $(urlFields[i]).parents('.form-group').addClass('has-error');
                    $(urlFields[i]).siblings('.help-block').remove();
                    $(urlFields[i]).after('<span class="help-block">The URL you entered is not valid. Did you mean http://localhost/ ?</span>');
                }
            }
        }
        return valid;
    }

	function passwordsValid(form) {
		var valid = true;
		var password1 = $('input#password1');
		var password2 = $('input#password2');

		if (!(password1.val().length >= 6)) {
			valid = false;
			password1.parent().addClass('has-error');
			password1.after('<span class="help-block">The password must be at least 6 characters long.</span>');
		}

		if (password1.val() !== password2.val()) {
			valid = false;
			password1.parent().addClass('has-error');
			password2.parent().addClass('has-error');
			password2.after('<span class="help-block">The passwords do not match.</span>');
		}

		return valid;
	}

	function allValid(form) {
		return emailsValid(form) && dateTimeValid(form) && urlsValid(form) && passwordsValid(form);
	}

	/**
	 * Validates a frorm using standard form.checkValidity(). If valid, the form is submitted.
	 * If not, invalid fields are marked and a help text is provided.
	 * @param  {Event} event The form submission event.
	 */
	function validate(event) {
		var formSubmitted = event.target;
		// remove all error messages
		var errorFields = $(formSubmitted).find('.has-error');
		errorFields.find('.help-block').remove();
		errorFields.removeClass('has-error');

		if (allValid(formSubmitted) && formSubmitted.checkValidity()) {
			// The form is valid, submit the thing
			if (form.attr('method') && form.attr('action')) {
				$(formSubmitted).off('submit');
				$(formSubmitted).submit();
			}
		} else {
			// The form is invalid
			var validFields = $(formSubmitted).find(':valid');
			var invalidFields = $(formSubmitted).find(':invalid');

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
							if (validity.rangeOverflow) { showHelp(field, 'The entered value must be lower than ' + field.attr('max') + '.'); }
							if (validity.rangeUnderflow) { showHelp(field, 'The entered value must be greater than ' + field.attr('min') + '.'); }
							break;
						case 'text':
							if (validity.patternMismatch && ['subdomain', 'key'].indexOf(field.attr('name')) !== -1) {
								showHelp(field, 'Your input contains special characters. The field must only contain characters, numbers, dashes or underscores.');
							}
							break;
					}
				}
			}
		}

		event.preventDefault();
	}

	/**
	 * Resets the form to its initial state. Removes all error messages.
	 */
	function reset() {
		form.find('.form-group').removeClass('has-error');
		form.find('.help-block').remove();
	}

	form.submit(validate);
	$('button[type="reset"]').click(reset);

    function allValid(form) {
        return emailsValid(form) && dateTimeValid(form) && urlsValid(form);
    }

    /**
     * Validates a frorm using standard form.checkValidity(). If valid, the form is submitted.
     * If not, invalid fields are marked and a help text is provided.
     * @param  {Event} event The form submission event.
     */
    function validate(event) {
        var formSubmitted = event.target;
        // remove all error messages
        var errorFields = $(formSubmitted).find('.has-error');
        errorFields.find('.help-block').remove();
        errorFields.removeClass('has-error');

        if (allValid(formSubmitted) && formSubmitted.checkValidity()) {
            // The form is valid, submit the thing
            if (form.attr('method') && form.attr('action')) {
                $(formSubmitted).off('submit');
                $(formSubmitted).submit();
            }
        } else {
            // The form is invalid
            var validFields = $(formSubmitted).find(':valid');
            var invalidFields = $(formSubmitted).find(':invalid');

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
                            if (validity.badInput) {
                                showHelp(field, 'Your input contains non-numeric characters. Maybe you used a comma (,) as decimal point?');
                            }
                            if (validity.stepMismatch) {
                                var digits = field.attr('step').split('.')[1];
                                if (digits) {
                                    showHelp(field, 'You entered more than ' + digits.length + ' digits after the decimal point.');
                                } else {
                                    showHelp(field, 'You entered a none integer value.');
                                }
                            }
                            if (validity.rangeOverflow) {
                                showHelp(field, 'The entered value must be lower than ' + field.attr('max') + '.');
                            }
                            if (validity.rangeUnderflow) {
                                showHelp(field, 'The entered value must be greater than ' + field.attr('min') + '.');
                            }
                            break;
                        case 'text':
                            if (validity.patternMismatch && ['subdomain', 'key'].indexOf(field.attr('name')) !== -1) {
                                showHelp(field, 'Your input contains special characters. The field must only contain characters, numbers, dashes or underscores.');
                            }
                            break;
                    }
                }
            }
        }

        event.preventDefault();
    }

    /**
     * Resets the form to its initial state. Removes all error messages.
     */
    function reset() {
        form.find('.form-group').removeClass('has-error');
        form.find('.help-block').remove();
    }

    form.submit(validate);
    $('button[type="reset"]').click(reset);
}());
