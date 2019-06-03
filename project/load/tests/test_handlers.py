from django.test import TestCase

from load.handlers.espn import ESPNHandler


def prepare_data(obj):
    pass
    # obj.handler = CommonHandler.objects.get(slug=CommonHandler.SRC_ESPN)


#######################################################################################
######  ESPNHandler
#######################################################################################
class ESPNHandlerTest(TestCase):

    def setUp(self):
        prepare_data(self)

    #######################################################################
    def test_espn_handler_get(self):
        handler = ESPNHandler.get()
        self.assertEquals(handler.slug, ESPNHandler.SRC_ESPN)
