$(function() {
    'use strict';

    var appId = $('body').attr('data-app-id'),
        url = 'apps/' + appId;

    var messages = new Ui.MessageDisplay('form#appForm');
    var valuesSubmitBtn = $('form#appForm button[type="submit"]');

    function handleAppUpdateError(response) {
        valuesSubmitBtn.button('reset');
        messages.showError('An error occured while updating the app details. Error text was: ' + response.responseJSON.error);
    }

    function handleAppUpdateSuccess(response) {
        $('form#appForm input[name="download_url"]').attr('value', response.download_url);
        $('form#appForm input[name="redirect_url"]').attr('value', response.redirect_url);
        valuesSubmitBtn.button('reset');
    }

    function urlsValid(form) {
        var valid = true;
        var urlFields = $(form).find('input[type="url"]');

        for (var i = 0, len = urlFields.length; i < len; i++) {
            var url = urlFields[i].value;
            var host = url.replace('http://','').replace('https://','').split(/[/?#]/)[0];
            if (host.indexOf('.') === -1 && host.indexOf('localhost') === -1) {
                valid = false;
                $(urlFields[i]).parents('.form-group').addClass('has-error');
                $(urlFields[i]).siblings('.help-block').remove();
                $(urlFields[i]).after('<span class="help-block">The URL you entered is not valid. Did you mean http://localhost/ ?</span>');
            }
        }
        return valid;
    }

    function submitForm(event) {
        if (event.target.checkValidity() && urlsValid(event.target)) {
            valuesSubmitBtn.button('loading');
            var form = $(event.target).serializeArray();
            var values = {};
            for (var i = 0, len = form.length; i < len; i++) {
                values[form[i].name] = form[i].value;
            }

            Control.Ajax.put(url, handleAppUpdateSuccess, handleAppUpdateError, values);
        }
        event.preventDefault();
    }

    $('form#appForm').submit(submitForm);
});