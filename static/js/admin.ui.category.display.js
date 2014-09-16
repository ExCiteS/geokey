$(function () {
    $("input#colour").pickAColor({
        showSpectrum            : true,
        showSavedColors         : false,
        saveColorsPerElement    : false,
        fadeMenuToggle          : false,
        showHexInput            : false,
        showBasicColors         : false,
        allowBlank              : false,
        inlineDropdown          : false     
    });
});
