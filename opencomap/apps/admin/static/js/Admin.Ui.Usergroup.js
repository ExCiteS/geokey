(function (global) {
	function Usergroup(panel, groupId) {
		this.panel = $(panel);
		this.formField = this.panel.find('.panel-footer input[type="text"]');
		this.formField.keypress(handleFormType)
	}

	function handleFormType(event) {
		
	}

	global.Usergroup = Usergroup;
}(window.Ui ? window.Ui : window.Ui = {}));