$(function() {
	var $typeSelectionField = $('#type');
	var $lookupValuesPanel = $('#lookupValuesPanel');
	var lookupPanel = new Ui.LookupPanel('#lookupValuesPanel');

	function handleTypeSelection(event) {
		if (event.target.value === '4') { $lookupValuesPanel.show(); } 
		else { $lookupValuesPanel.hide(); }
	}
	
	$typeSelectionField.change(handleTypeSelection);
	$lookupValuesPanel.hide();
});