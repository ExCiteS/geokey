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

    function handleTypeSelect(event) {
        $('#minmax').addClass('hidden');
        if (event.target.value === 'NumericField') {
            $('#minmax').removeClass('hidden');
        }
    }

    $('input#name').blur(setFieldKey);
    $('form select#type').change(handleTypeSelect);
}());