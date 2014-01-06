(function (global) {
	function Project(id) {
		this.projectId = id;
	}

	Project.prototype.del = function del() {
		function handleSuccess(response) {
			window.location.replace("/admin/dashboard");
		}

		function handleError(response) {
			console.log('error');
		}

		Control.Ajax.get('/api/ajax/project/' + this.projectId + '/delete', handleSuccess, handleError);
	}

	global.Project = Project;
}(window.Control ? window.Control : window.Control = {}));
