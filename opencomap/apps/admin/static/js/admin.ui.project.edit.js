$(function () {
	var control = new Control.Project($('body').attr('data-project-id'));

	function handleProjectDelete() {
		control.del();
	}

	$('#delete_confirm button[value="delete"]').click(handleProjectDelete);
});