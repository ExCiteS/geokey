$(function () {
    'use strict';

    var symbolPath = $('body').attr('data-symbol');
    $("#colour").colorpicker();

    var fileinputConfig = {
        'showUpload': false
    };

    if (symbolPath) {
        fileinputConfig.initialPreview = [
            '<img src="' + symbolPath + '" class="file-preview-image">'
        ];
    }

    $('input#symbol').fileinput(fileinputConfig);
    $('input#symbol').on('fileclear', function(event) {
        $('input#clear-symbol').val('true');
    });
});
