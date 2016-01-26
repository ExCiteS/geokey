/* ***********************************************
 * Initialises the color picker.
 * Initialises the file upload and sets the initial state.
 *
 * Docs for colorpicker:
 * http://mjolnic.com/bootstrap-colorpicker/
 *
 * Docs for file upload:
 * http://plugins.krajee.com/file-input
 *
 * Used in:
 * - templates/categories/category_display.html
 * ***********************************************/

$(function() {
    'use strict';

    // Initialise the colorpicker
    $('#colour').colorpicker({
        format: 'hex'
    });

    // Initialise the file upload configuration
    var fileinputConfig = {
        showUpload: false
    };

    // Set initial state of the file upload, if an image has been uploaded
    // before.
    var symbolPath = $('body').attr('data-symbol');
    if (symbolPath) {
        fileinputConfig.initialPreview = [
            '<img src="' + symbolPath + '" class="file-preview-image">'
        ];
    }

    // Initialise the file upload
    $('input#symbol').fileinput(fileinputConfig);

    // When the user removes a file, the value of clear-symbol is set to true,
    // so the image can be removed from data base in the backend.
    $('input#symbol').on('fileclear', function(event) {
        $('input#clear-symbol').val('true');
    });
});
