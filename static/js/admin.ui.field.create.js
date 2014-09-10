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
        $('.field-special').addClass('hidden');
        switch (event.target.value) {
            case 'NumericField':
                $('#minmax').removeClass('hidden');
                break;
            case 'LookupField':
                $('#lookup').removeClass('hidden');
                break;    
        }
    }

    $('input#name').blur(setFieldKey);
    $('form select#type').change(handleTypeSelect);
}());