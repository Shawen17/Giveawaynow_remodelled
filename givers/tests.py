from django.test import TestCase
from .models import ContactUs
from.forms import ContactUsForm


class ContactUsTestCase(TestCase):
    def setUp(self):
        ContactUs.objects.create(ticket='uhgrt56',email='tolu@yahoo.com',subject='enquiry',body='i am still waiting for my package')

    def test_contactus_is_updated(self):
        shawen=ContactUs.objects.get(email='tolu@yahoo.com')
        self.assertEqual(shawen.ticket,'uhgrt56')

    def test_form_field(self):
        form=ContactUsForm()
        self.assertFalse(form.fields['email'].label is None)

