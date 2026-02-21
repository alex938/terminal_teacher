"""Comprehensive tests for Terminal Teacher application."""
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from commands.models import TeachingSession, CommandEntry
import json
import os


class TeachingSessionModelTest(TestCase):
    """Tests for TeachingSession model."""

    def test_create_session(self):
        """Test creating a teaching session."""
        session = TeachingSession.objects.create(
            title="Test Session",
            is_active=True
        )
        self.assertEqual(session.title, "Test Session")
        self.assertTrue(session.is_active)
        self.assertIsNotNone(session.created_at)

    def test_get_active_session_creates_if_none(self):
        """Test get_active_session creates session if none exists."""
        self.assertEqual(TeachingSession.objects.count(), 0)
        session = TeachingSession.get_active_session()
        self.assertIsNotNone(session)
        self.assertTrue(session.is_active)
        self.assertEqual(TeachingSession.objects.count(), 1)

    def test_get_active_session_returns_existing(self):
        """Test get_active_session returns existing active session."""
        session1 = TeachingSession.objects.create(
            title="Session 1",
            is_active=True
        )
        session2 = TeachingSession.get_active_session()
        self.assertEqual(session1.id, session2.id)


class CommandEntryModelTest(TestCase):
    """Tests for CommandEntry model."""

    def setUp(self):
        self.session = TeachingSession.objects.create(
            title="Test Session",
            is_active=True
        )

    def test_create_command(self):
        """Test creating a command entry."""
        command = CommandEntry.objects.create(
            session=self.session,
            command_text="git status"
        )
        self.assertEqual(command.command_text, "git status")
        self.assertEqual(command.session, self.session)
        self.assertIsNotNone(command.created_at)

    def test_command_ordering(self):
        """Test commands are ordered by creation time."""
        cmd1 = CommandEntry.objects.create(
            session=self.session,
            command_text="first"
        )
        cmd2 = CommandEntry.objects.create(
            session=self.session,
            command_text="second"
        )
        commands = list(self.session.commands.all())
        self.assertEqual(commands[0], cmd1)
        self.assertEqual(commands[1], cmd2)


class AuthenticationTest(TestCase):
    """Tests for authentication system."""

    def setUp(self):
        self.client = Client()
        os.environ['ADMIN_PASSWORD'] = 'test-password'

    def test_login_page_accessible(self):
        """Test login page is accessible."""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_with_correct_password(self):
        """Test login with correct password."""
        response = self.client.post(reverse('login'), {
            'password': 'test-password'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertTrue(self.client.session.get('is_admin'))

    def test_login_with_wrong_password(self):
        """Test login with wrong password."""
        response = self.client.post(reverse('login'), {
            'password': 'wrong-password'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.client.session.get('is_admin'))

    def test_admin_panel_requires_auth(self):
        """Test admin panel requires authentication."""
        response = self.client.get(reverse('admin_panel'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_admin_panel_accessible_when_logged_in(self):
        """Test admin panel accessible after login."""
        session = self.client.session
        session['is_admin'] = True
        session.save()
        
        response = self.client.get(reverse('admin_panel'))
        self.assertEqual(response.status_code, 200)


class PublicViewsTest(TestCase):
    """Tests for public views."""

    def setUp(self):
        self.client = Client()
        self.session = TeachingSession.get_active_session()

    def test_student_view_accessible(self):
        """Test student view is publicly accessible."""
        response = self.client.get(reverse('student_view'))
        self.assertEqual(response.status_code, 200)

    def test_student_view_shows_commands(self):
        """Test student view displays commands."""
        CommandEntry.objects.create(
            session=self.session,
            command_text="ls -la"
        )
        response = self.client.get(reverse('student_view'))
        self.assertContains(response, "ls -la")

    def test_healthz_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get(reverse('healthz'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'ok')


class APIEndpointsTest(TestCase):
    """Tests for API endpoints."""

    def setUp(self):
        self.client = Client()
        os.environ['ADMIN_PASSWORD'] = 'test-password'
        self.session = TeachingSession.get_active_session()

    def test_get_commands_api(self):
        """Test get commands API."""
        cmd = CommandEntry.objects.create(
            session=self.session,
            command_text="echo test"
        )
        response = self.client.get(reverse('api_get_commands'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['commands']), 1)
        self.assertEqual(data['commands'][0]['command_text'], "echo test")

    def test_get_commands_with_since_parameter(self):
        """Test get commands API with since parameter."""
        cmd1 = CommandEntry.objects.create(
            session=self.session,
            command_text="first"
        )
        cmd2 = CommandEntry.objects.create(
            session=self.session,
            command_text="second"
        )
        
        response = self.client.get(
            reverse('api_get_commands') + f'?since={cmd1.id}'
        )
        data = json.loads(response.content)
        self.assertEqual(len(data['commands']), 1)
        self.assertEqual(data['commands'][0]['command_text'], "second")

    def test_submit_command_requires_auth(self):
        """Test submit command requires authentication."""
        response = self.client.post(reverse('api_submit_command'), {
            'command': 'test command'
        })
        self.assertEqual(response.status_code, 401)

    def test_submit_command_with_bearer_token(self):
        """Test submit command with Bearer token."""
        response = self.client.post(
            reverse('api_submit_command'),
            {'command': 'git log'},
            HTTP_AUTHORIZATION='Bearer test-password'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            CommandEntry.objects.filter(command_text='git log').exists()
        )

    def test_submit_command_with_session_auth(self):
        """Test submit command with session authentication."""
        session = self.client.session
        session['is_admin'] = True
        session.save()
        
        response = self.client.post(reverse('api_submit_command'), {
            'command': 'pwd'
        })
        self.assertEqual(response.status_code, 200)

    def test_delete_command_requires_auth(self):
        """Test delete command requires authentication."""
        cmd = CommandEntry.objects.create(
            session=self.session,
            command_text="test"
        )
        # API endpoints return 401 for unauthenticated requests
        response = self.client.post(
            reverse('api_delete_command', args=[cmd.id])
        )
        # This is a protected admin endpoint that redirects to login
        self.assertIn(response.status_code, [302, 401])

    def test_delete_command_works_when_authenticated(self):
        """Test delete command works when authenticated."""
        session = self.client.session
        session['is_admin'] = True
        session.save()
        
        cmd = CommandEntry.objects.create(
            session=self.session,
            command_text="test"
        )
        
        response = self.client.post(
            reverse('api_delete_command', args=[cmd.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            CommandEntry.objects.filter(id=cmd.id).exists()
        )


class XSSPreventionTest(TestCase):
    """Tests for XSS prevention."""

    def setUp(self):
        self.client = Client()
        os.environ['ADMIN_PASSWORD'] = 'test-password'
        self.session = TeachingSession.get_active_session()

    def test_command_text_escaped_in_student_view(self):
        """Test command text is escaped in student view."""
        xss_payload = '<script>alert("XSS")</script>'
        CommandEntry.objects.create(
            session=self.session,
            command_text=xss_payload
        )
        
        response = self.client.get(reverse('student_view'))
        self.assertNotContains(response, '<script>alert("XSS")</script>')
        # The escaped version should be present
        self.assertContains(response, '&lt;script&gt;')

    def test_command_text_escaped_in_json_response(self):
        """Test command text is properly encoded in JSON."""
        xss_payload = '<script>alert("XSS")</script>'
        CommandEntry.objects.create(
            session=self.session,
            command_text=xss_payload
        )
        
        response = self.client.get(reverse('api_get_commands'))
        data = json.loads(response.content)
        # JSON should contain the raw string, but client-side escaping
        # (tested in JavaScript) will handle display
        self.assertEqual(
            data['commands'][0]['command_text'],
            xss_payload
        )


class SessionManagementTest(TestCase):
    """Tests for session management."""

    def setUp(self):
        self.client = Client()
        os.environ['ADMIN_PASSWORD'] = 'test-password'
        session = self.client.session
        session['is_admin'] = True
        session.save()
        self.session = TeachingSession.get_active_session()

    def test_clear_session(self):
        """Test clearing session commands."""
        CommandEntry.objects.create(
            session=self.session,
            command_text="cmd1"
        )
        CommandEntry.objects.create(
            session=self.session,
            command_text="cmd2"
        )
        
        response = self.client.post(reverse('api_clear_session'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.session.commands.count(), 0)

    def test_new_session_creation(self):
        """Test creating a new session."""
        old_session = self.session
        
        response = self.client.post(reverse('api_new_session'), {
            'title': 'New Session'
        })
        self.assertEqual(response.status_code, 200)
        
        # Old session should be inactive
        old_session.refresh_from_db()
        self.assertFalse(old_session.is_active)
        
        # New session should be active
        new_session = TeachingSession.objects.get(title='New Session')
        self.assertTrue(new_session.is_active)
