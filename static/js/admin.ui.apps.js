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
        messages.showSuccess('The application details have been updated.');
    }

    function submitForm(event) {
        if (event.target.checkValidity()) {
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