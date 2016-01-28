/* ***********************************************
 * Module to edit field properties. Is currently only responsible
 * for setting minimum and maximum values of numeric fields and initialising
 * lookup field edits.
 * Is automatically loaded when included in a page.
 
 * Used in:
 * - templates/categories/field_settings.html
 * ***********************************************/

$(function() {
    'use strict';

    var projectId = $('body').attr('data-project-id'),
        categoryId = $('body').attr('data-category-id'),
        fieldId = $('body').attr('data-field-id'),
        url = 'projects/' + projectId + '/categories/' + categoryId + '/fields/' + fieldId;

    // Initialize the lookup panel functionality if the field is a lookup
    if ($('#lookupValuesPanel').length !== 0) {
        new Ui.LookupPanel('#lookupValuesPanel', url);

        // Initialise file upload for each field
        $('input:file').each(function() {
            Ui.FileInput.init($(this));
        });
    }

    // Set the min and maximum values for numeric fields, so they can be
    // validated
    function handleNumericFieldEdit(event) {
        var target = $(event.target);

        if (target.attr('id') === 'minval') {
            // set the current minval as minimum value for maxval field
            $('form input#maxval').attr('min', target.val());
        } else if (target.attr('id') === 'maxval') {
            // set the current maxval as minimum value for minval field
            $('form input#minval').attr('max', target.val());
        }
    }

    $('form input[type="number"]').change(handleNumericFieldEdit);
});
