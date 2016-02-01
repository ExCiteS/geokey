/* ***********************************************
 * Initialises the file input functionality for
 * input field.
 *
 * Used in:
 * - templates/categories/category_display.html
 * - templates/categories/field_settings.html
 * ***********************************************/

$(function(global) {
    'use strict';

    function FileInput() {}

    FileInput.prototype.init = function(field, additionalSettings) {
        var settings = {
            showUpload: false,
            showCancel: false,
            browseLabel: 'Browse...',
            msgLoading: 'Loading file {index} of {files}...'
        };

        for (var key in additionalSettings) {
            settings[key] = additionalSettings[key];
        }

        if (field.attr('data-preview')) {
            settings.initialPreview = '<img src="' + field.attr('data-preview') + '" class="file-preview-image">';
        }

        field.fileinput(settings);
        field.parents().find('div.fileinput-remove').hide();

        field.on('fileclear', function() {
            $('input#' + $(this).data('target') + '-clear').val('true');
        });
    };

    global.FileInput = new FileInput();
}(window.Ui ? window.Ui : window.Ui = {}));
