from backendtest import BackendTest

class TestView(BackendTest):
	def test_getView(self):
		views = self.project.getViews()
		self.assertEquals(len(views), 1)
		self.assertEquals(views[0].name, self.featureType.name)

	def test_Features(self):
		views = self.project.getViews()
		features_in_view = views[0].getFeatures()
		self.assertEquals(len(features_in_view), len(self.geometries))