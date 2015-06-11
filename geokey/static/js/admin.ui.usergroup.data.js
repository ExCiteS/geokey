(function () {
    'use strict';

    var filters = null,
        projectId = $('body').attr('data-project-id'),
        groupId = $('body').attr('data-group-id');

    function handlePermissionChange() {
        $('#filter').toggleClass('hidden');
        filters = ($(this).val() === 'all' ? null : {});
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
                                filters[catId]['max_date'] = field.find('input#created_at-max').val() || null;
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
                    if (value) { filters[catId][field.attr('data-key')] = value; }
                }
            }
        }
        $('input[name="filters"]').val(JSON.stringify(filters));
    }

    function handleRangeFieldEdit(event) {
        var target = $(event.target);

        if (target.attr('id') === target.attr('data-key') + '-min') {
            $('input#' + target.attr('data-key') + '-max').attr('min', target.val());
        } else if (target.attr('id') === target.attr('data-key') + '-max') {
            $('input#' + target.attr('data-key') + '-min').attr('max', target.val());
        }
    }

    function handleCategorySelect() {
        if ($(this).prop( "checked" )) {
            var detailLink = $('<a href="#" class="text-danger activate-detailed">Restrict further</a>');
            $(this).parent().append(detailLink);
            detailLink.click(handleActivateDetailed);
        } else {
            $(this).siblings('a.activate-detailed').remove();
            $(this).siblings('div.field-options').remove();
        }
        handleEdit();
    }

    function addFilter(container, category) {
        container.find('a.activate-detailed').remove();
        var field_options = $('<div class="field-options"></div>');
        container.find('#add-more').before(field_options);

        var fieldselect = $(Templates.fieldselect(category));
        field_options.append(fieldselect);

        fieldselect.change(function () {
            fieldselect.remove();

            var fieldkey = $(this).val();
            var filterForm;

            if (fieldkey === 'created_at') {
                filterForm = $(Templates.createdfield(field))
                field_options.append(filterForm);
            } else {
                var field;

                for (var i = 0, len = category.fields.length; i < len; i++) {
                    if (fieldkey === category.fields[i].key) {
                        field = category.fields[i];
                        break;
                    }
                }
                filterForm = $(Templates.field(field))
                field_options.append(filterForm);
            }

            filterForm.find('input.datetime').datetimepicker();
            filterForm.find('input.date').datetimepicker({ pickTime: false });
            filterForm.find('input.time').datetimepicker({ pickDate: false });
            filterForm.find('input[type="number"], input.datetime, input.date').change(handleRangeFieldEdit);
            filterForm.find(':input').change(handleEdit);

            filterForm.find('a.remove').click(function(event) {
                event.preventDefault();

                if (field_options.siblings().length === 2) {
                    container.find('#add-more').remove();
                    var detailLink = $('<a href="#" class="text-danger activate-detailed">Restrict further</a>');
                    container.children('label').append(detailLink);
                    detailLink.click(handleActivateDetailed);
                }

                field_options.remove();
            });
        });
    }

    function handleActivateDetailed(event) {
        event.preventDefault();
        var container = $(this).parent().parent();

        function handleTypeSuccess(response) {
            var button = $('<button id="add-more" class="btn btn-primary" type="button">Add another filter</button>');
            container.append(button);
            button.click(function(event) {
                event.preventDefault();
                addFilter(container, response);
            });

            addFilter(container, response);
        }

        Control.Ajax.get(
            'projects/' + projectId + '/categories/' + container.find('input.cat').val(),
            handleTypeSuccess
        );
    }

    $('form#data-access input[name="permission"]').change(handlePermissionChange);
    $('form#data-access input[name="permission"]').change(handleEdit);
    $('div.category input.cat').change(handleCategorySelect);
}());
