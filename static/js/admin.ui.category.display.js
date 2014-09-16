$(function () {
    var symbolPath = $('body').attr('data-symbol')

    // $("input#colour").pickAColor({
    //     showSpectrum            : true,
    //     // showSavedColors         : false,
    //     // saveColorsPerElement    : false,
    //     // fadeMenuToggle          : false,
    //     // showHexInput            : false,
    //     // showBasicColors         : false,
    //     // allowBlank              : false,
    //     // inlineDropdown          : false     
    // });
    // 
    $("#colour").colorpicker();

    var fileinputConfig = {
        'showUpload': false
    }

    if (symbolPath) {
        fileinputConfig.initialPreview = [
            '<img src="' + symbolPath + '" class="file-preview-image">'
        ]
    }

    $('input#symbol').fileinput(fileinputConfig);
    $('input#symbol').on('fileclear', function(event) {
        $('input#clear-symbol').val('true')
    });
});
