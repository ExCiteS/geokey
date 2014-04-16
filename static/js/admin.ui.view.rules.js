$(function() {
    'use strict';
    var projectId = $('body').attr('data-project-id'),
        viewId = $('body').attr('data-view-id');

    var messages = new Ui.MessageDisplay();

    function handleTypeSelection(event) {
        var target = $(event.currentTarget).parents('form');
        messages.showPanelLoading(target, 'Loading field information for this observation type...');

        function handleTypeSuccess(response) {
            target.children('.info-loading').hide('slow', function() {
                this.remove();
            });

            $('#field-options').empty();
            $('#field-options').append(Templates.fields(response));
            if (!Modernizr.inputtypes.datetime) {
                $('input[type="datetime"]').datetimepicker();
            }
        }

        function handleTypeError(response) {
            messages.showPanelError(target, response.responseJSON.error);
        }

        Control.Ajax.get(
            'projects/' + projectId + '/observationtypes/' + event.currentTarget.value,
            handleTypeSuccess,
            handleTypeError
        );
    }

    function getValue(field) {
        var value = field.find('#reference-value').val();
        return (value && value.length > 0 ? value : undefined);
    }

    function getRangeValue(field) {
        var value = {};
        var minval = field.find('#minval').val();
        var maxval = field.find('#maxval').val();

        if (minval) { value.minval = minval; }
        if (maxval) { value.maxval = maxval; }

        return (value.minval || value.maxval ? value : undefined);
    }

    function handleSubmit() {
        var rules = {};
        var fields = $('.field-filter');

        for (var i = 0, len = fields.length; i < len; i++) {
            var field = $(fields[i]);
            var value;
            switch (field.attr('data-type')) {
                case 'DateTimeField':
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
        $('form#rule-form').submit();
    }

    $('#observationtype').change(handleTypeSelection);
    $('button[type="button"]').click(handleSubmit);
});