/* ***********************************************
 * Based on what is selected as field type, the script shows and hides form
 * fields specific to certain field types.
 *
 * For instance, if you select the type TextField, the inputs for max lenght and
 * display as textbox are show. These fields are wrapped in a div with
 * id="text", which is shown.
 *
 * Used in:
 * - templates/categories/field_create.html
 * ***********************************************/

(function () {
    'use strict';

    function handleTypeSelect(event) {
        // hide all specific inputs
        $('.field-special').addClass('hidden');

        // switch on the field type, it shows specific fields accordingly
        switch (event.target.value) {
            case 'TextField':
                $('#text').removeClass('hidden');
                break;
            case 'NumericField':
                $('#minmax').removeClass('hidden');
                break;
            case 'LookupField':
            case 'MultipleLookupField':
                $('#lookup').removeClass('hidden');
                break;
        }
    }

    // register the event handler on the select field
    $('form select#type').change(handleTypeSelect);
}());
