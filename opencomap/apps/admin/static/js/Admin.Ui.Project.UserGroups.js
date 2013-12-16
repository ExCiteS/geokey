$(function () {
	var $administratorsPanel = new Ui.Usergroup('#users #administrators', 0),
		$contributorsPanel = new Ui.Usergroup('#users #contributors', 1),
		$everyoneCheck = $('#users #contributors input[type="checkbox"]');


	function toggleEveryoneView(everyone) {
		$('#users #contributors .list-group').toggle(),
		$('#users #contributors .panel-footer').toggle();
	}

	function handleEveryoneChange(event) {
		toggleEveryoneView(event.target.checked)
	}
	
	toggleEveryoneView(false);
	$everyoneCheck.change(handleEveryoneChange);
	
});