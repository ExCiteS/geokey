(function () {
    'use strict';

    function handleTypeSelect(event) {
        $('.field-special').addClass('hidden');
        switch (event.target.value) {
            case 'NumericField':
                $('#minmax').removeClass('hidden');
                break;
            case 'LookupField':
            case 'MultipleLookupField':
                $('#lookup').removeClass('hidden');
                break;
        }
    }

    $('form select#type').change(handleTypeSelect);
}());
