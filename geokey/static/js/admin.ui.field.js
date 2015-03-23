/* ***********************************************
 * Module to edit field properties. Is currently only responsible
 * for setting minimim and maximum values of numeric fields.
 * Is automatically loaded when included in a page.
 *
 * @author Oliver Roick (http://github.com/oliverroick)
 * @version 0.1
 * ***********************************************/

$(function() {
    'use strict';

    var projectId = $('body').attr('data-project-id'),
        categoryId = $('body').attr('data-category-id'),
        fieldId = $('body').attr('data-field-id'),
        url = 'projects/' + projectId + '/categories/' + categoryId + '/fields/' + fieldId;

    // Initialize the lookup panel functionality if the field is a lookup
    var lookupPanel = ($('#lookupValuesPanel').length !== 0 ? new Ui.LookupPanel('#lookupValuesPanel', url) : undefined);

    function handleNumericFieldEdit(event) {
        var target = $(event.target);

        if (target.attr('id') === 'minval') {
            $('form input#maxval').attr('min', target.val());
        } else if (target.attr('id') === 'maxval') {
            $('form input#minval').attr('max', target.val());
        }
    }

    $('form input[type="number"]').change(handleNumericFieldEdit);
});
