$(function() {
    'use strict';
    var projectId = $('body').attr('data-project-id'),
        viewId = $('body').attr('data-view-id');

    var messages = new Ui.MessageDisplay();

    function handleTypeSelection(event) {
        var target = $(event.currentTarget).parents('form');
        messages.showPanelLoading(target, 'Loading field information for this contribution type...');

        function handleTypeSuccess(response) {
            target.children('.info-loading').hide('slow', function() {
                this.remove();
            });

            $('#field-options').empty();
            $('#field-options').append(Templates.fields(response));
            if (!Modernizr.inputtypes.datetime) {
                $('input[type="datetime"]').datetimepicker();
            }
            $('input[type="number"]').change(handleNumericFieldEdit);
            $('#field-options :input').change(handleFieldChange);
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
                case 'NumericField':
                    value = getRangeValue(field);
                    break;
                default:
                    value = getValue(field);
                    break;
            }
            if (value) { rules[field.attr('data-key')] = value; }
        }
        console.log(rules);
        $('input[name="rules"]').val(JSON.stringify(rules));
    }

    function handleNumericFieldEdit(event) {
        var target = $(event.target);
        
        if (target.attr('id') === target.attr('data-key') + '-min') {
            $('input#' + target.attr('data-key') + '-max').attr('min', target.val());
        } else if (target.attr('id') === target.attr('data-key') + '-max') {
            $('input#' + target.attr('data-key') + '-min').attr('max', target.val());
        }
    }
    $('#field-options :input').change(handleFieldChange);
    $('#observationtype').change(handleTypeSelection);
});