from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import timedelta
from cities_light.models import City, Country
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core import mail

from meetup.forms import (AddMeetupForm, EditMeetupForm, AddMeetupLocationMemberForm,
                          AddMeetupLocationForm, EditMeetupLocationForm, AddMeetupCommentForm,
                          EditMeetupCommentForm, RsvpForm, AddSupportRequestForm,
                          EditSupportRequestForm, AddSupportRequestCommentForm,
                          EditSupportRequestCommentForm, RequestMeetupLocationForm,
                          RequestMeetupForm)
from meetup.models import (Meetup, MeetupLocation, Rsvp, SupportRequest, RequestMeetupLocation,
                           RequestMeetup)
from users.models import SystersUser
from common.models import Comment


class MeetupFormTestCaseBase:
    def setUp(self):
        self.user = User.objects.create_user(username='foo', password='foobar',
                                             email='user@test.com')
        self.systers_user = SystersUser.objects.get(user=self.user)
        country = Country.objects.create(name='Bar', continent='AS')
        self.location = City.objects.create(name='Baz', display_name='Baz', country=country)
        self.meetup_location = MeetupLocation.objects.create(
            name="Foo Systers", slug="foo", location=self.location,
            description="It's a test meetup location", sponsors="BarBaz", leader=self.systers_user)
        self.meetup_location.members.add(self.systers_user)
        self.meetup_location.moderators.add(self.systers_user)

        self.meetup = Meetup.objects.create(title='Foo Bar Baz', slug='foobarbaz',
                                            date=timezone.now().date(),
                                            time=timezone.now().time(),
                                            description='This is test Meetup',
                                            meetup_location=self.meetup_location,
                                            created_by=self.systers_user,
                                            last_updated=timezone.now())


class RequestMeetupLocationFormTestCase(MeetupFormTestCaseBase, TestCase):
    def test_add_request_meetup_location_form(self):
        # Testing form with invalid data
        invalid_data = {'name': 'def', 'location': 'Baz, Bar, AS'}
        form = AddMeetupLocationForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())
        # Testing form with valid data
        location_id = self.location.id
        data = {'name': 'Bar Systers', 'slug': 'bar', 'location': location_id,
                'description': 'test test test.', 'email': 'abc@def.com'}
        form = RequestMeetupLocationForm(data=data, user=self.user)
        self.assertTrue(form.is_valid())
        form.save()

        new_meetup_location_request = RequestMeetupLocation.objects.get(slug='bar')
        self.assertTrue(new_meetup_location_request.name, 'Bar Systers')


class RequestMeetupFormTestCase(MeetupFormTestCaseBase, TestCase):
    def test_add_request_meetup_form(self):
        # Testing form with invalid data
        invalid_data = {'title': 'abc', 'date': timezone.now().date()}
        form = RequestMeetupForm(data=invalid_data, created_by=self.user,
                                 meetup_location=self.meetup_location)
        self.assertFalse(form.is_valid())

        date = (timezone.now() + timedelta(2)).date()
        time = timezone.now().time()
        data = {'title': 'Foo', 'slug': 'foo', 'date': date, 'time': time,
                'description': "It's a test meetup."}
        form = RequestMeetupForm(data=data, created_by=self.user,
                                 meetup_location=self.meetup_location)
        self.assertTrue(form.is_valid())
        form.save()
        new_meetup_request = RequestMeetup.objects.get(slug='foo')
        self.assertTrue(new_meetup_request.title, 'Foo')
        self.assertTrue(new_meetup_request.created_by, self.systers_user)
        self.assertTrue(new_meetup_request.meetup_location, self.meetup_location)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user.email, mail.outbox[0].to)
        self.assertIn('New Meetup Request', mail.outbox[0].subject)

    def test_request_meetup_form_with_past_date(self):
        """Test add Meetup form with a date that has passed."""
        date = (timezone.now() - timedelta(2)).date()
        time = timezone.now().time()
        data = {'title': 'Foo', 'slug': 'foo', 'date': date, 'time': time,
                'description': "It's a test meetup."}
        form = AddMeetupForm(data=data, created_by=self.systers_user,
                             meetup_location=self.meetup_location)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors['date'], ["Date should not be before today's date."])

    def test_request_meetup_form_with_passed_time(self):
        """Test add Meetup form with a time that has passed."""
        date = timezone.now().date()
        time = (timezone.now() - timedelta(2)).time()
        data = {'title': 'Foo', 'slug': 'foo', 'date': date, 'time': time,
                'description': "It's a test meetup."}
        form = AddMeetupForm(data=data, created_by=self.systers_user,
                             meetup_location=self.meetup_location)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors['time'],
                        ["Time should not be a time that has already passed."])
        self.assertRaises(ValidationError, form.clean_time())


class AddMeetupFormTestCase(MeetupFormTestCaseBase, TestCase):
    def setUp(self):
        super(AddMeetupFormTestCase, self).setUp()
        self.password = 'bazbar'
        self.user2 = User.objects.create_user(username='baz', password=self.password,
                                              email='user2@test.com')
        self.systers_user2 = SystersUser.objects.get(user=self.user2)
        self.meetup_location.members.add(self.systers_user2)

    def test_add_meetup_form(self):
        """Test add Meetup form"""
        invalid_data = {'title': 'abc', 'date': timezone.now().date()}
        form = AddMeetupForm(data=invalid_data, created_by=self.systers_user,
                             meetup_location=self.meetup_location)
        self.assertFalse(form.is_valid())

        date = (timezone.now() + timedelta(2)).date()
        time = timezone.now().time()
        start_time = timezone.now().time()
        end_time = timezone.now().time()
        data = {'title': 'Foo', 'slug': 'foo', 'date': date, 'time': time,
                'start_time': start_time, 'end_time': end_time,
                'description': "It's a test meetup."}
        form = AddMeetupForm(data=data, created_by=self.user,
                             meetup_location=self.meetup_location)
        self.assertTrue(form.is_valid())
        form.save()
        new_meetup = Meetup.objects.get(slug='foo')
        self.assertTrue(new_meetup.title, 'Foo')
        self.assertTrue(new_meetup.created_by, self.systers_user)
        self.assertTrue(new_meetup.meetup_location, self.meetup_location)
        self.assertEqual(len(mail.outbox), 2)
        self.assertIn(self.user.email, mail.outbox[0].to)
        self.assertIn('New Meetup', mail.outbox[0].subject)
        self.assertIn(self.user2.email, mail.outbox[1].to)
        self.assertIn('New Meetup', mail.outbox[1].subject)

    def test_add_meetup_form_with_past_date(self):
        """Test add Meetup form with a date that has passed."""
        date = (timezone.now() - timedelta(2)).date()
        time = timezone.now().time()
        data = {'title': 'Foo', 'slug': 'foo', 'date': date, 'time': time,
                'description': "It's a test meetup."}
        form = AddMeetupForm(data=data, created_by=self.systers_user,
                             meetup_location=self.meetup_location)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors['date'], ["Date should not be before today's date."])

    def test_add_meetup_form_with_passed_time(self):
        """Test add Meetup form with a time that has passed."""
        date = timezone.now().date()
        time = (timezone.now() - timedelta(2)).time()
        data = {'title': 'Foo', 'slug': 'foo', 'date': date, 'time': time,
                'description': "It's a test meetup."}
        form = AddMeetupForm(data=data, created_by=self.systers_user,
                             meetup_location=self.meetup_location)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors['time'],
                        ["Time should not be a time that has already passed."])


class EditMeetupFormTestCase(MeetupFormTestCaseBase, TestCase):
    def test_edit_meetup_form(self):
        """Test edit meetup"""
        incomplete_data = {'slug': 'slug', 'date': timezone.now().date()}
        form = EditMeetupForm(data=incomplete_data)
        self.assertFalse(form.is_valid())

        date = (timezone.now() + timedelta(2)).date()
        time = timezone.now().time()
        start_time = timezone.now().time()
        end_time = timezone.now().time()

        data = {'slug': 'foobar', 'title': 'Foo Bar', 'date': date, 'time': time,
                'start_time': start_time, 'end_time': end_time,
                'description': "It's a test meetup.", 'venue': 'test address'}
        form = EditMeetupForm(instance=self.meetup, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        meetup = Meetup.objects.get()
        self.assertEqual(meetup.title, 'Foo Bar')
        self.assertEqual(meetup.slug, 'foobar')
        self.assertEqual(meetup.created_by, self.systers_user)
        self.assertEqual(meetup.meetup_location, self.meetup_location)


class AddMeetupLocationMemberFormTestCase(MeetupFormTestCaseBase, TestCase):
    def setUp(self):
        super(AddMeetupLocationMemberFormTestCase, self).setUp()
        self.user2 = User.objects.create_user(username='baz', password='bazbar',
                                              email='user2@test.com')
        self.systers_user2 = SystersUser.objects.get(user=self.user2)

    def test_add_meetup_location_member_form(self):
        """Test add meetup location Member form"""
        invalid_data = {'username': 'non_existent'}
        form = AddMeetupLocationMemberForm(data=invalid_data)
        self.assertFalse(form.is_valid())

        username = self.user2.get_username()
        data = {'username': username}
        self.meetup_location = MeetupLocation.objects.get()
        form = AddMeetupLocationMemberForm(data=data, instance=self.meetup_location)
        self.assertTrue(form.is_valid())
        form.save()

        members = self.meetup_location.members.all()
        self.assertTrue(self.systers_user2 in members)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user2.email, mail.outbox[0].to)
        self.assertIn('Joined Meetup Location', mail.outbox[0].subject)


class AddMeetupLocationFormTestCase(MeetupFormTestCaseBase, TestCase):
    def test_add_meetup_location_form(self):
        """Test add Meetup Location form"""
        invalid_data = {'name': 'def', 'location': 'Baz, Bar, AS'}
        form = AddMeetupLocationForm(data=invalid_data, user=self.user)
        self.assertFalse(form.is_valid())

        location_id = self.location.id
        data = {'name': 'Bar Systers', 'slug': 'bar', 'location': location_id,
                'description': 'test test test.', 'email': 'abc@def.com', 'sponsors': 'BaaBaa'}
        form = AddMeetupLocationForm(data=data, user=self.user)
        self.assertTrue(form.is_valid())
        form.save()

        new_meetup_location = MeetupLocation.objects.get(slug='bar')
        self.assertTrue(new_meetup_location.name, 'Bar Systers')


class EditMeetupLocationFormTestCase(MeetupFormTestCaseBase, TestCase):
    def test_edit_meetup_location_form(self):
        """Test edit meetup location form"""
        invalid_data = {'location': 4, 'sponsors': 'wrogn'}
        form = EditMeetupLocationForm(data=invalid_data)
        self.assertFalse(form.is_valid())

        location_id = self.location.id
        data = {'name': 'Foo Systers', 'slug': 'foo', 'location': location_id,
                'description': 'test edit', 'email': 'foo@bar.com', 'sponsors': 'test'}
        form = EditMeetupLocationForm(instance=self.meetup_location, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        meetup_location = MeetupLocation.objects.get()
        self.assertEqual(meetup_location.description, 'test edit')
        self.assertEqual(meetup_location.sponsors, 'test')


class AddMeetupCommentFormTestCase(MeetupFormTestCaseBase, TestCase):
    def test_add_meetup_comment_form(self):
        """Test add meetup Comment form"""
        data = {'body': 'This is a test comment'}
        form = AddMeetupCommentForm(data=data, author=self.user,
                                    content_object=self.meetup)
        self.assertTrue(form.is_valid())
        form.save()
        comments = Comment.objects.all()
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].body, 'This is a test comment')
        self.assertEqual(comments[0].author, self.systers_user)
        self.assertEqual(comments[0].content_object, self.meetup)


class EditMeetupCommentFormTestCase(MeetupFormTestCaseBase, TestCase):
    def setUp(self):
        super(EditMeetupCommentFormTestCase, self).setUp()
        meetup_content_type = ContentType.objects.get(app_label='meetup', model='meetup')
        self.comment = Comment.objects.create(author=self.systers_user, is_approved=True,
                                              body='This is a test comment',
                                              content_type=meetup_content_type,
                                              object_id=self.meetup.id)

    def test_edit_meetup_comment_form(self):
        """Test edit meetup Comment form"""
        data = {'body': 'This is an edited test comment'}
        form = EditMeetupCommentForm(instance=self.comment, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        comments = Comment.objects.all()
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].body, 'This is an edited test comment')
        self.assertEqual(comments[0].author, self.systers_user)
        self.assertEqual(comments[0].content_object, self.meetup)


class RsvpFormTestCase(MeetupFormTestCaseBase, TestCase):
    def test_rsvp_form(self):
        """Test Rsvp form"""
        data = {'coming': True, 'plus_one': True}
        form = RsvpForm(data=data, user=self.user,
                        meetup=self.meetup)
        self.assertTrue(form.is_valid())
        form.save()
        rsvp_list = Rsvp.objects.filter(meetup=self.meetup)
        self.assertEqual(len(rsvp_list), 1)
        self.assertEqual(rsvp_list[0].coming, True)
        self.assertEqual(rsvp_list[0].plus_one, True)
        self.assertEqual(rsvp_list[0].user, self.systers_user)
        self.assertEqual(rsvp_list[0].meetup, self.meetup)


class AddSupportRequestFormTestCase(MeetupFormTestCaseBase, TestCase):
    def test_add_support_request_form(self):
        """Test add Support Request form"""
        data = {'description': 'This is a test description'}
        form = AddSupportRequestForm(data=data, volunteer=self.user,
                                     meetup=self.meetup)
        self.assertTrue(form.is_valid())
        form.save()
        support_requests = SupportRequest.objects.all()
        self.assertEqual(len(support_requests), 1)
        self.assertEqual(support_requests[0].description, 'This is a test description')
        self.assertEqual(support_requests[0].volunteer, self.systers_user)
        self.assertEqual(support_requests[0].meetup, self.meetup)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user.email, mail.outbox[0].to)
        self.assertIn('New Support Request', mail.outbox[0].subject)


class EditSupportRequestFormTestCase(MeetupFormTestCaseBase, TestCase):
    def setUp(self):
        super(EditSupportRequestFormTestCase, self).setUp()
        self.support_request = SupportRequest.objects.create(
            volunteer=self.systers_user, meetup=self.meetup,
            description='This is a test description', is_approved=False)

    def test_edit_support_request_form(self):
        """Test edit Support Request form"""
        data = {'description': 'This is an edited test description'}
        form = EditSupportRequestForm(instance=self.support_request, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        support_requests = SupportRequest.objects.all()
        self.assertEqual(len(support_requests), 1)
        self.assertEqual(support_requests[0].description, 'This is an edited test description')
        self.assertEqual(support_requests[0].volunteer, self.systers_user)
        self.assertEqual(support_requests[0].meetup, self.meetup)


class AddSupportRequestCommentFormTestCase(MeetupFormTestCaseBase, TestCase):
    def setUp(self):
        super(AddSupportRequestCommentFormTestCase, self).setUp()
        self.support_request = SupportRequest.objects.create(
            volunteer=self.systers_user, meetup=self.meetup,
            description='This is a test description', is_approved=False)

    def test_add_support_request_comment_form(self):
        """Test add support request Comment form"""
        data = {'body': 'This is a test comment'}
        form = AddSupportRequestCommentForm(data=data, author=self.user,
                                            content_object=self.support_request)
        self.assertTrue(form.is_valid())
        form.save()
        comments = Comment.objects.all()
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].body, 'This is a test comment')
        self.assertEqual(comments[0].author, self.systers_user)
        self.assertEqual(comments[0].content_object, self.support_request)


class EditSupportRequestCommentFormTestCase(MeetupFormTestCaseBase, TestCase):
    def setUp(self):
        super(EditSupportRequestCommentFormTestCase, self).setUp()
        self.support_request = SupportRequest.objects.create(
            volunteer=self.systers_user, meetup=self.meetup,
            description='This is a test description', is_approved=False)
        support_request_content_type = ContentType.objects.get(app_label='meetup',
                                                               model='supportrequest')
        self.comment = Comment.objects.create(author=self.systers_user, is_approved=True,
                                              body='This is a test comment',
                                              content_type=support_request_content_type,
                                              object_id=self.support_request.id)

    def test_edit_support_request_comment_form(self):
        """Test edit support request Comment form"""
        data = {'body': 'This is an edited test comment'}
        form = EditSupportRequestCommentForm(instance=self.comment, data=data)
        self.assertTrue(form.is_valid())
        form.save()
        comments = Comment.objects.all()
        self.assertEqual(len(comments), 1)
        self.assertEqual(comments[0].body, 'This is an edited test comment')
        self.assertEqual(comments[0].author, self.systers_user)
        self.assertEqual(comments[0].content_object, self.support_request)
