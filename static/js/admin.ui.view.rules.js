Handlebars.registerHelper('ifCond', function(v1, v2, options) {
  if(v1 === v2) {
    return options.fn(this);
  }
  return options.inverse(this);
});

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

            $('#field-options').append(Templates.fields(response));
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

    function getRule(field) {
        console.log(field);
        var rule;
        var val = field.find('#reference-value').val();

        if (val && val.length > 0) {
            rule = {
                id: field.attr('data-id'),
                value: val
            };
        }
        return rule;
    }

    function getRangeRule(field) {
        console.log(field);
        var rule;
        var minval = field.find('#minval').val();
        var maxval = field.find('#maxval').val();

        if (minval || maxval) {
            rule = {
                id: field.attr('data-id'),
                minval: minval,
                maxval: maxval
            };
        }
        return rule;
    }

    function handleSubmit() {
        var rules = [];
        var fields = $('.field-filter');

        for (var i = 0, len = fields.length; i < len; i++) {
            var field = $(fields[i]);
            var rule;
            switch (field.attr('data-type')) {
                case 'DateTimeField':
                case 'NumericField':
                    rule = getRangeRule(field);
                    break;
                default:
                    rule = getRule(field);
                    break;
            }

            if (rule) { rules.push(rule); }
        }
        console.log(rules);


    }

    $('#observationtype').change(handleTypeSelection);
    $('button[type="button"]').click(handleSubmit);
});