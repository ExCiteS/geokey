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

    // Initialise the color picker
    $('#colour').colorpicker({
        format: 'hex'
    });

    // Initialise file upload for each field
    $('input:file').each(function() {
        Ui.FileInput.init($(this));
    });
});
