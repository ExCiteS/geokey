(function () {
    'use strict';

    var projectId = $('body').attr('data-project-id'),
        categoryId = $('body').attr('data-category-id'),
        url = 'projects/' + projectId + '/categories/' + categoryId;

    var keyField = $('input#key');

    function replaceKey(event) {
        var new_key = $(this).attr('href').substring(1);
        keyField.parents('.form-group').removeClass('has-error');
        keyField.siblings('.help-block').remove();
        keyField.val(new_key);
    }

    function setFieldKey(event) {
        var fieldName = $(event.target).val();
        
        var keyValue = fieldName.replace(/\s/g, '_').replace(/[^\w]/gi, '').toLowerCase();
        keyField.val(keyValue);

        function handleSuccess(response) {
            if (!response.accepted) {
                var message = 'The key <code>' + keyValue + '</code> already exists. <a href="#' + response.suggested_key + '" id="replace-key">Click here to use <code>' + response.suggested_key + '</code> instead.</a>';
                
                keyField.parents('.form-group').addClass('has-error');
                keyField.siblings('.help-block').remove();
                keyField.after('<span class="help-block">' + message  + '</span>');
                $('#replace-key').click(replaceKey);
            }
        }

        function handleError(response) {
            
        }

        Control.Ajax.get(url + '/check-key/?key=' + keyValue, handleSuccess, handleError);
    }

    function handleTypeSelect(event) {
        $('.field-special').addClass('hidden');
        switch (event.target.value) {
            case 'NumericField':
                $('#minmax').removeClass('hidden');
                break;
            case 'LookupField':
                $('#lookup').removeClass('hidden');
                break;    
        }
    }

    $('input#name').change(setFieldKey);
    $('form select#type').change(handleTypeSelect);
}());