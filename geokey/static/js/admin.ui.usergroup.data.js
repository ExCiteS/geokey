(function () {
    'use strict';

    var filters = null,
        projectId = $('body').attr('data-project-id'),
        groupId = $('body').attr('data-group-id');

    function handlePermissionChange() {
        $('#filter').toggleClass('hidden');
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

            filterForm.find('a.remove').click(function(event) {
                event.preventDefault();

                if (field_options.siblings().length === 2) {
                    container.find('#add-more').remove();
                    var detailLink = $('<a href="#" class="text-danger activate-detailed">Restrict further</a>');
                    container.append(detailLink);
                    detailLink.click(handleActivateDetailed);
                }

                field_options.remove();
            });
        });
    }

    function handleActivateDetailed(event) {
        event.preventDefault();
        var container = $(this).parent();

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
            'projects/' + projectId + '/categories/' + container.children('input.cat').val(),
            handleTypeSuccess
        );
    }

    $('form#data-access input[name="permission"]').change(handlePermissionChange);
    $('div.category input.cat').change(handleCategorySelect);
}());
