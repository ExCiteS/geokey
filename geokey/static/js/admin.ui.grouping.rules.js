$(function() {
    'use strict';
    var projectId = $('body').attr('data-project-id');

    function handleTypeSelection(event) {
        var target = $(event.currentTarget).parents('form');

        function handleTypeSuccess(response) {
            target.children('.info-loading').hide('slow', function() {
                this.remove();
            });

            $('#field-options').empty();
            $('#field-options').append(Templates.fields(response));

            $('input.datetime').datetimepicker();
            $('input.date').datetimepicker({ pickTime: false });

            $('input.time').datetimepicker({ pickDate: false });

            $('#field-options input[type="number"], #field-options input.datetime, #field-options input.date').change(handleRangeFieldEdit);
            $('#field-options :input').change(handleFieldChange);
        }

        function handleTypeError(response) {
            // messages.showPanelError(target, response.responseJSON.error);
        }

        Control.Ajax.get(
            'projects/' + projectId + '/categories/' + event.currentTarget.value,
            handleTypeSuccess,
            handleTypeError
        );
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

    function handleFieldChange(event) {
        var formSubmitted = event.target;
        var rules = {};

        rules.min_date = $('input[name="created_at-min"]').val() || null;
        rules.max_date = $('input[name="created_at-max"]').val() || null;

        var fields = $('.field-filter');

        for (var i = 0, len = fields.length; i < len; i++) {
            var field = $(fields[i]);
            var value;
            switch (field.attr('data-type')) {
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
            if (value) { rules[field.attr('data-key')] = value; }
        }

        $('input[name="rules"]').val(JSON.stringify(rules));
    }

    function handleRangeFieldEdit(event) {
        var target = $(event.target);

        if (target.attr('id') === target.attr('data-key') + '-min') {
            $('input#' + target.attr('data-key') + '-max').attr('min', target.val());
        } else if (target.attr('id') === target.attr('data-key') + '-max') {
            $('input#' + target.attr('data-key') + '-min').attr('max', target.val());
        }
    }

    $('#field-options :input').change(handleFieldChange);
    $('#field-options input[type="number"], #field-options input.datetime, #field-options input.date').change(handleRangeFieldEdit);
    $('#category').change(handleTypeSelection);
});
