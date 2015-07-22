(function () {
    'use strict';

    var filters = null,
        projectId = $('body').attr('data-project-id'),
        groupId = $('body').attr('data-group-id');

    function handlePermissionChange() {
        $('#filter').toggleClass('hidden');
        if ($(this).val() === 'all') {
            filters = null;
            $('input[name="filters"]').val('');
        } else {
            handleEdit();
        }
    }

    function getValue(field) {
        var value = field.find('#reference-value').val();
        return (value && value.length > 0 ? value : undefined);
    }

    function getRangeValue(field) {
        var key = field.attr('data-key');
        var value = {};
        var minval = field.find('#' + key + '-min').val();
        var maxval = field.find('#' + key + '-max').val();

        if (minval) { value.minval = minval; }
        if (maxval) { value.maxval = maxval; }

        return (value.minval || value.maxval ? value : undefined);
    }

    function handleEdit() {
        filters = {}
        var categories = $('div.category');
        for (var catIterator = 0, len = categories.length; catIterator < len; catIterator++) {
            var category = $(categories[catIterator]);
            var catId = category.find('input.cat').val();

            if (category.find('input.cat').prop( "checked" )) {
                filters[catId] = {};

                var filterFields = category.find('div.field-filter');

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
                    if (field.attr('data-type') != 'DateCreated' && value) { filters[catId][field.attr('data-key')] = value; }
                }
            }
        }

        $('input[name="filters"]').val(JSON.stringify(filters));
    }

    function handleRangeFieldEdit(event) {
        var target = $(event.target),
            container = target.parents('.field-filter');
        console.log(target)
        console.log('#' + target.attr('data-key') + '-min')

        if (target.attr('id') === target.attr('data-key') + '-min') {
            container.find('input#' + target.attr('data-key') + '-max').attr('min', target.val());
        } else if (target.attr('id') === target.attr('data-key') + '-max') {
            container.find('input#' + target.attr('data-key') + '-min').attr('max', target.val());
        }
    }

    function handleCategorySelect() {
        if ($(this).prop( "checked" )) {
            var detailLink = $('<a href="#" class="text-danger activate-detailed">Restrict further</a>');
            $(this).parent().append(detailLink);
            detailLink.click(handleActivateDetailed);
        } else {
            $(this).siblings('a.activate-detailed').remove();
            $(this).parent().siblings('div.field-options').remove();
        }
        handleEdit();
    }

    function addFilter(container, category) {
        container.find('a.activate-detailed').remove();

        var fieldselect = $(Templates.fieldselect(category));
        container.find('.list-group').append(fieldselect);

        fieldselect.find('select').change(function () {
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
            filterForm.find('input.date').datetimepicker({ pickTime: false });
            filterForm.find('input.time').datetimepicker({ pickDate: false });
            filterForm.find('input[type="number"], input.datetime, input.date').change(handleRangeFieldEdit);
            filterForm.find(':input').change(handleEdit);

            filterForm.find('button.remove').click(removeFilter);
        });
    }

    function removeFilter(event) {
        event.preventDefault();

        var container = $(this).parents('div.category'),
            field_options = $(this).parents('div.field-filter');

        if (field_options.siblings().length === 0) {
            container.find('.field-options').remove();
            var detailLink = $('<a href="#" class="text-danger activate-detailed">Restrict further</a>');
            container.children('label').append(detailLink);
            detailLink.click(handleActivateDetailed);
        }

        field_options.remove();
        handleEdit();
    }

    function handleAddMore(event) {
        event.preventDefault();
        var container = $(this).parents('.category');

        function handleTypeSuccess(response) {
            addFilter(container.find('.field-options'), response);
        }

        Control.Ajax.get(
            'projects/' + projectId + '/categories/' + container.find('input.cat').val(),
            handleTypeSuccess
        );
    }

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
            'projects/' + projectId + '/categories/' + container.find('input.cat').val(),
            handleTypeSuccess
        );
    }

    $('form#data-access input[name="permission"]').change(handlePermissionChange);
    $('div.category input.cat').change(handleCategorySelect);
    $('a.activate-detailed').click(handleActivateDetailed);
    $('button#add-more').click(handleAddMore);

    $('input.datetime').datetimepicker();
    $('input.date').datetimepicker({ pickTime: false });
    $('input.time').datetimepicker({ pickDate: false });
    $('input[type="number"], input.datetime, input.date').change(handleRangeFieldEdit);
    $('#filter :input').change(handleEdit);

    $('button.remove').click(removeFilter);
}());
