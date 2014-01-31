(function (global) {
	function LookupPanel(panelId, url) {
		this.panel = $(panelId);
		this.url = url + '/lookupvalues';
		this.lookuplist = this.panel.find('ul.list-group');
		this.formField = this.panel.find('input[name="new-value"]');
		this.addButton = this.panel.find('.panel-footer button');

		this.addButton.click(this.handleAddValue.bind(this));
		this.lookuplist.find('li a').click(this.handleRemoveValue.bind(this));
	}

	LookupPanel.prototype.handleRemoveValue = function handleRemoveValue(event) {
		var lookupId = $(event.target).attr('data-lookup-id');
		var itemToRemove = $(event.target).parent('.list-group-item');

		function handleRemoveValueSucces(response) {
			console.log(response)
			itemToRemove.remove();
		}

		function handleRemoveValueError(response) {
			console.log(response);
		}

		Control.Ajax.del(this.url + '/' + lookupId, handleRemoveValueSucces, handleRemoveValueError, {name: this.formField.val()});

		event.preventDefault();
	}

	LookupPanel.prototype.handleAddValueSuccess = function handleAddValueSuccess(response) {
		var lookupValues = response.field.lookupvalues;

		this.formField.val(null);
		this.lookuplist.empty();
		for (var i = 0, len = lookupValues.length; i < len; i++) {
			this.lookuplist.append('<li class="list-group-item">' + lookupValues[i].name + ' (<a data-lookup-id="' + lookupValues[i].id + '" class="text-danger" href="#">remove</a>)</li>');
		}
		this.lookuplist.find('li a').click(this.handleRemoveValue.bind(this));
		this.addButton.button('reset');
	}

	LookupPanel.prototype.handleAddValueError = function handleAddValueError(response) {
		console.log(response);
	}

	LookupPanel.prototype.handleAddValue = function handleAddValue(event) {
		this.addButton.button('loading');
		Control.Ajax.put(this.url, this.handleAddValueSuccess.bind(this), this.handleAddValueError.bind(this), {name: this.formField.val()});
	}

	global.LookupPanel = LookupPanel;
}(window.Ui ? window.Ui : window.Ui = {}));