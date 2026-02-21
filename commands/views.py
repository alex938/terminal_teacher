"""Views for the terminal teacher application."""
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt, csrf_protect, ensure_csrf_cookie
from django.utils import timezone
from django.db import transaction
from datetime import timedelta

from .models import TeachingSession, CommandEntry
from .auth import require_admin, require_admin_api, get_admin_password


# Public views (no authentication required)

@require_GET
@ensure_csrf_cookie
def student_view(request):
    """Main student view - displays commands in real-time."""
    session = TeachingSession.get_active_session()
    commands = list(session.commands.all()[:100])
    
    return render(request, 'commands/student_view.html', {
        'session': session,
        'commands': commands,
    })


@require_GET
def api_get_commands(request):
    """API endpoint for polling new commands."""
    since_id = request.GET.get('since', 0)
    try:
        since_id = int(since_id)
    except (ValueError, TypeError):
        since_id = 0
    
    session = TeachingSession.get_active_session()
    
    # Get all command IDs in the current session
    all_command_ids = list(session.commands.values_list('id', flat=True))
    
    # Get new commands
    commands = session.commands.filter(id__gt=since_id).values(
        'id', 'command_text', 'created_at'
    )
    
    return JsonResponse({
        'commands': list(commands),
        'all_command_ids': all_command_ids,
        'session_id': session.id,
        'session_title': session.title,
    })


@require_GET
def healthz(request):
    """Health check endpoint."""
    return JsonResponse({'status': 'ok'})


# Authentication views

@require_http_methods(['GET', 'POST'])
def login_view(request):
    """Login page for admin access."""
    if request.method == 'POST':
        password = request.POST.get('password', '')
        try:
            if password == get_admin_password():
                request.session['is_admin'] = True
                next_url = request.GET.get('next', '/admin-panel/')
                return redirect(next_url)
            else:
                return render(request, 'commands/login.html', {
                    'error': 'Invalid password'
                })
        except ValueError as e:
            return render(request, 'commands/login.html', {
                'error': str(e)
            })
    
    return render(request, 'commands/login.html')


@require_POST
def logout_view(request):
    """Logout endpoint."""
    request.session.flush()
    return redirect('student_view')


# Protected views (authentication required)

@require_admin
@require_GET
def admin_panel(request):
    """Admin panel for managing commands and sessions."""
    session = TeachingSession.get_active_session()
    commands = session.commands.all()
    
    return render(request, 'commands/admin_panel.html', {
        'session': session,
        'commands': commands,
    })


# Protected API endpoints

@csrf_exempt
@require_admin_api
@require_POST
def api_submit_command(request):
    """API endpoint to submit a new command."""
    command_text = request.POST.get('command', '')
    
    if not command_text or not command_text.strip():
        return JsonResponse({'error': 'Command text is required'}, status=400)
    
    command_text = command_text.strip()
    session = TeachingSession.get_active_session()
    
    # Check for duplicate in last 5 seconds
    five_seconds_ago = timezone.now() - timedelta(seconds=5)
    recent_duplicate = session.commands.filter(
        command_text=command_text,
        created_at__gte=five_seconds_ago
    ).exists()
    
    if recent_duplicate:
        # Duplicate detected, don't add but return success
        return JsonResponse({
            'success': True,
            'duplicate': True,
            'message': 'Duplicate command ignored'
        })
    
    # Not a duplicate, add it
    command = CommandEntry.objects.create(
        session=session,
        command_text=command_text
    )
    
    return JsonResponse({
        'success': True,
        'command_id': command.id,
        'message': 'Command submitted successfully'
    })


@csrf_protect
@require_admin
@require_POST
def api_delete_command(request, command_id):
    """API endpoint to delete a specific command."""
    try:
        command = CommandEntry.objects.get(id=command_id)
        command.delete()
        return JsonResponse({'success': True, 'message': 'Command deleted'})
    except CommandEntry.DoesNotExist:
        return JsonResponse({'error': 'Command not found'}, status=404)


@csrf_protect
@require_admin
@require_POST
def api_clear_session(request):
    """API endpoint to clear all commands in the current session."""
    session = TeachingSession.get_active_session()
    count = session.commands.count()
    session.commands.all().delete()
    
    return JsonResponse({
        'success': True,
        'message': f'Cleared {count} commands from session'
    })


@csrf_protect
@require_admin
@require_POST
def api_new_session(request):
    """API endpoint to start a new teaching session."""
    title = request.POST.get('title', '')
    
    with transaction.atomic():
        # Deactivate all current sessions
        TeachingSession.objects.filter(is_active=True).update(is_active=False)
        
        # Create new active session
        if not title:
            title = f"Session {timezone.now().strftime('%Y-%m-%d %H:%M')}"
        
        new_session = TeachingSession.objects.create(
            title=title,
            is_active=True
        )
    
    return JsonResponse({
        'success': True,
        'session_id': new_session.id,
        'session_title': new_session.title,
        'message': 'New session created'
    })


@csrf_protect
@require_admin
@require_POST
def api_add_manual_command(request):
    """API endpoint to manually add a command (fallback)."""
    command_text = request.POST.get('command', '')
    
    if not command_text or not command_text.strip():
        return JsonResponse({'error': 'Command text is required'}, status=400)
    
    session = TeachingSession.get_active_session()
    command = CommandEntry.objects.create(
        session=session,
        command_text=command_text.strip()
    )
    
    return JsonResponse({
        'success': True,
        'command_id': command.id,
        'message': 'Command added successfully'
    })


@csrf_protect
@require_admin
@require_POST
def api_nuke_database(request):
    """Nuclear option: delete everything and reset IDs."""
    from django.db import connection
    
    # Delete all data
    CommandEntry.objects.all().delete()
    TeachingSession.objects.all().delete()
    
    # Reset auto-increment counters (SQLite specific)
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='commands_commandentry'")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='commands_teachingsession'")
    
    # Create fresh session
    TeachingSession.get_active_session()
    
    return JsonResponse({
        'success': True,
        'message': 'Database nuked! All IDs reset to 1.'
    })
