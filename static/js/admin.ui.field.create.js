(function () {
    'use strict';

    function setFieldKey(event) {
        var keyField = $('input#key');
        var fieldName = $(event.target).val();
        if (!keyField.val().length) {
            var keyValue = fieldName.replace(/\s/g, '_').replace(/[^\w]/gi, '').toLowerCase();
            keyField.val(keyValue);
        }
    }

    $('input#name').blur(setFieldKey);
}());