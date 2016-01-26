/* ***********************************************
 * Functionality to define filters for user groups and subsets.
 *
 * Used in:
 * - templates/subsets/subsets_data.html
 * - templates/users/usergroups_data.html
 * ***********************************************/

(function() {
    'use strict';

    var filters = null,
        projectId = $('body').attr('data-project-id'),
        usergroupId = $('body').attr('data-usergroup-id');

    /**
     * Handles changes to general permissions (all data vs. selected data).
     * Hides the filter settings and empties input[name="filters"]' if users can access all data
     */
    function handlePermissionChange() {
        $('#filter').toggleClass('hidden');
        if ($(this).val() === 'all') {
            filters = null;
            $('input[name="filters"]').val('');
        } else {
            handleEdit();
        }
    }

    /**
     * Returns the value for a standard field, i.e. text, selects
     * @return {Object} undefined, if field is empty
     */
    function getValue(field) {
        var value = field.find('#reference-value').val();
        return (value && value.length > 0 ? value : undefined);
    }

    /**
     * Returns the value for a range field, i.e. numbers, dates.
     * Returned object:
     * {
     *    minval: 1,
     *    maxval: 10
     * }
     *
     * @return {Object} undefined, if field is empty
     */
    function getRangeValue(field) {
        var key = field.attr('data-key');
        var value = {};
        var minval = field.find('#' + key + '-min').val();
        var maxval = field.find('#' + key + '-max').val();

        if (minval) {
            value.minval = minval;
        }
        if (maxval) {
            value.maxval = maxval;
        }

        return (value.minval || value.maxval ? value : undefined);
    }

    /**
     * Is called after any field has been edited. Collects values of all fields
     * and updates input[name="filters"]
     */
    function handleEdit() {
        filters = {}
        var categories = $('div.category');

        // Iterate over all categories
        for (var catIterator = 0, len = categories.length; catIterator < len; catIterator++) {
            var category = $(categories[catIterator]);
            var catId = category.find('input.category').val();

            if (category.find('input.category').prop("checked")) { // include only categories that are activated
                filters[catId] = {};

                var filterFields = category.find('div.field-filter');

                // iterate over all field filters per category and get the value for the field
                for (var i = 0; i < filterFields.length; i++) {
                    var field = $(filterFields[i]);

                    var value;
                    switch (field.attr('data-type')) {
                        case 'DateCreated':
                            if (field.find('input#created_at-min').val()) {
                                filters[catId]['min_date'] = field.find('input#created_at-min').val();
                            }
                            if (field.find('input#created_at-max').val()) {
                                filters[catId]['max_date'] = field.find('input#created_at-max').val();
                            }
                            break;
                        case 'DateTimeField':
                        case 'DateField':
                        case 'TimeField':
                        case 'NumericField':
                            value = getRangeValue(field);
                            break;
                        default:
                            value = getValue(field);
                            break;
                    }
                    if (field.attr('data-type') != 'DateCreated' && value) {
                        filters[catId][field.attr('data-key')] = value;
                    }
                }
            }
        }

        // set the value of input[name="filters"] to the stringified version of filters
        // the value of input[name="filters"] is evaluated on server side and stored accordingly
        $('input[name="filters"]').val(JSON.stringify(filters));
    }

    /**
     * Is called after range fields (e.g. numbers, dates) and updated. It updates
     * the minimum or maximum value of the corresponding field, for better form
     * field validation. That means of you update the minimum value of a numeric
     * field the min attribute of the maximum value field is updated.
     */
    function handleRangeFieldEdit(event) {
        var target = $(event.target),
            container = target.parents('.field-filter');

        if (target.attr('id') === target.attr('data-key') + '-min') {
            container.find('input#' + target.attr('data-key') + '-max').attr('min', target.val());
        } else if (target.attr('id') === target.attr('data-key') + '-max') {
            container.find('input#' + target.attr('data-key') + '-min').attr('max', target.val());
        }
    }

    /**
     * Is called when the selects or unselects a category.
     */
    function handleCategorySelect() {
        if ($(this).prop("checked")) {
            var detailLink = $('<a href="#" class="text-danger activate-detailed">Restrict further</a>');
            $(this).parent().append(detailLink);
            detailLink.click(handleActivateDetailed);
        } else {
            $(this).siblings('a.activate-detailed').remove();
            $(this).parent().siblings('div.field-options').remove();
        }
        handleEdit();
    }

    /**
     * Adds form fields to add a new filter for a category.
     */
    function addFilter(container, category) {
        container.find('a.activate-detailed').remove();

        // Adds select field for a fields in the category
        var fieldselect = $(Templates.fieldselect(category));
        container.find('.list-group').append(fieldselect);

        // user selects a field, form fields to define the filter for the field is added
        fieldselect.find('select').change(function() {
            fieldselect.remove();

            var fieldkey = $(this).val();
            var filterForm;

            if (fieldkey === 'created_at') {
                filterForm = $(Templates.createdfield(field));
                container.find('.list-group').append(filterForm);
            } else {
                var field;

                for (var i = 0, len = category.fields.length; i < len; i++) {
                    if (fieldkey === category.fields[i].key) {
                        field = category.fields[i];
                        break;
                    }
                }
                filterForm = $(Templates.field(field))
                container.find('.list-group').append(filterForm);
            }

            filterForm.find('input.datetime').datetimepicker();
            filterForm.find('input.date').datetimepicker({
                pickTime: false
            });
            filterForm.find('input.time').datetimepicker({
                pickDate: false
            });
            filterForm.find('input[type="number"], input.datetime, input.date').change(handleRangeFieldEdit);
            filterForm.find(':input').change(handleEdit);

            filterForm.find('button.remove').click(removeFilter);
        });
    }

    /**
     * Removes a filter from a category
     */
    function removeFilter(event) {
        event.preventDefault();

        var container = $(this).parents('div.category'),
            field_options = $(this).parents('div.field-filter');

        if (field_options.siblings().length === 0) {
            // Remove all field filter forms
            container.find('.field-options').remove();

            // Add the "Restrict further link"
            var detailLink = $('<a href="#" class="text-danger activate-detailed">Restrict further</a>');
            container.children('label').append(detailLink);
            detailLink.click(handleActivateDetailed);
        }

        field_options.remove();
        handleEdit();
    }

    /**
     * Is called when the user clicks "Add another filter". Adds a new field filter.
     */
    function handleAddMore(event) {
        event.preventDefault();
        var container = $(this).parents('.category');

        function handleTypeSuccess(response) {
            addFilter(container.find('.field-options'), response);
        }

        Control.Ajax.get(
            'projects/' + projectId + '/categories/' + container.find('input.category').val(),
            handleTypeSuccess
        );
    }

    /**
     * Is called when the user clicks "Restrict further".
     */
    function handleActivateDetailed(event) {
        event.preventDefault();
        var container = $(this).parent().parent();
        $(this).remove();

        function handleTypeSuccess(response) {
            var field_container = $('<div class="field-options panel panel-default"><div class="list-group"></div><div class="panel-footer"><button id="add-more" class="btn btn-default btn-sm" type="button"><span class="text-success">Add another filter</span></button><div>');
            container.append(field_container);

            field_container.find('button#add-more').click(function(event) {
                event.preventDefault();
                addFilter(field_container, response);
            });

            addFilter(field_container, response);
        }

        Control.Ajax.get(
            'projects/' + projectId + '/categories/' + container.find('input.category').val(),
            handleTypeSuccess
        );
    }

    // handle when the general permissions (all data vs. selected data) are changed
    $('form#data-access input[name="permission"]').change(handlePermissionChange);

    // user selects a category to be included in the filter
    $('div.category input.category').change(handleCategorySelect);

    // users clicks "Restrict further" to select filters for attribute values
    $('a.activate-detailed').click(handleActivateDetailed);

    // user wants to add another filter
    $('button#add-more').click(handleAddMore);

    // activate datetime picker for date/time fields
    $('input.datetime').datetimepicker();
    $('input.date').datetimepicker({
        pickTime: false
    });
    $('input.time').datetimepicker({
        pickDate: false
    });

    // registers eventhandle on value change for numbers and dates
    // handleRangeFieldEdit sets min/max values of corresponding fields for validation
    $('input[type="number"], input.datetime, input.date').change(handleRangeFieldEdit);

    // handle value change in any form field to update the filter string that is sent to the server
    $('#filter :input').change(handleEdit);

    // user removes a filter
    $('button.remove').click(removeFilter);
}());
