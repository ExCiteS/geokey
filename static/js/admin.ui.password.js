$(function() {
    'use strict';

    function submitForm(event) {
        if (event.target.checkValidity()) {
            var validFields = $(event.target).find(':valid');
            validFields.siblings('.help-block').remove();
            validFields.parents('.form-group').removeClass('has-error');

            if ($('form input#new_password1').val() === $('form input#new_password2').val()) {
                $(event.target).off('submit');
                $(event.target).submit();
            } else {
                $(event.target).find('.help-block').remove();
                $('form input#new_password1').parent().addClass('has-error');
                $('form input#new_password2').parent().addClass('has-error');
                $('form input#new_password2').after('<span class="help-block">The passwords do not match.</span>');
            }
        }
        event.preventDefault();
    }

    $('form').submit(submitForm);
});
