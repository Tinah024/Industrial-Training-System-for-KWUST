import secrets
import string

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser
from .decorators import admin_required, supervisor_required, student_required
from logbook.models import LogbookEntry
from messaging.models import Notification
from students.models import StudentProfile
from messaging.models import Message
from django.db.models import Q

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email    = request.POST.get('email')
        password = request.POST.get('password')

        # SECURITY: role is intentionally never read from POST data.
        # The public registration form only ever creates Student accounts.
        # Supervisor accounts can only be created by an Administrator,
        # via the create_supervisor view below.

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')

        user = CustomUser.objects.create_user(
            username=username, email=email, password=password, role='student'
        )
        login(request, user)
        return redirect('dashboard')

    return render(request, 'accounts/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # redirect each role to their own dashboard
            if user.role == 'admin':
                return redirect('admin_dashboard')
            elif user.role == 'supervisor':
                return redirect('dashboard')
            else:
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
            return redirect('login')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    if request.user.role == 'admin':
        return redirect('admin_dashboard')

    context = {}

    if request.user.role == 'student':
        try:
            profile = StudentProfile.objects.get(user=request.user)
        except StudentProfile.DoesNotExist:
            messages.info(request, 'Please complete your profile to continue.')
            return redirect('my_profile')

        entries  = LogbookEntry.objects.filter(
            student=request.user
        ).order_by('-week_number')
        total    = entries.count()
        reviewed = entries.filter(is_reviewed=True).count()
        pending  = entries.filter(is_reviewed=False).count()
        context  = {
            'entries':      entries[:4],
            'weeks_logged': total,
            'reviewed':     reviewed,
            'pending':      pending,
        }

    elif request.user.role == 'supervisor':
        assigned_students = StudentProfile.objects.filter(
            university_supervisor=request.user
        ).select_related('user')

        assigned_user_ids = assigned_students.values_list('user', flat=True)
        entries = LogbookEntry.objects.filter(student__in=assigned_user_ids).order_by('-submitted_at')

        context = {
            'assigned_students': assigned_students,
            'total_students':    assigned_students.count(),
            'pending_reviews':   entries.filter(is_reviewed=False).count(),
            'completed_reviews': entries.filter(is_reviewed=True).count(),
            'recent_entries':    entries[:5],
        }

    return render(request, 'accounts/dashboard.html', context)


@login_required
def notifications_view(request):
    notes = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')
    notes.filter(is_read=False).update(is_read=True)
    return render(request, 'accounts/notifications.html', {'notifications': notes})


@admin_required
def admin_dashboard(request):
    total_students    = CustomUser.objects.filter(role='student').count()
    total_supervisors = CustomUser.objects.filter(role='supervisor').count()
    total_entries     = LogbookEntry.objects.count()
    pending_reviews   = LogbookEntry.objects.filter(is_reviewed=False).count()

    max_possible    = total_students * 12
    completion_rate = round((total_entries / max_possible) * 100) if max_possible > 0 else 0

    all_users      = CustomUser.objects.exclude(role='admin').order_by('-date_joined')
    all_entries    = LogbookEntry.objects.select_related('student').order_by('-submitted_at')
    recent_entries = all_entries[:20]

    return render(request, 'accounts/admin_dashboard.html', {
        'total_students':    total_students,
        'total_supervisors': total_supervisors,
        'total_entries':     total_entries,
        'pending_reviews':   pending_reviews,
        'reviewed_entries':  total_entries - pending_reviews,
        'completion_rate':   completion_rate,
        'all_users':         all_users,
        'all_entries':       all_entries,
        'recent_entries':    recent_entries,
    })


@admin_required
def create_supervisor(request):
    """
    The only way a Supervisor account can come into existence.
    Only an Administrator can reach this view (enforced by @admin_required),
    and the role is hardcoded to 'supervisor' — never taken from the form.
    """
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        username   = request.POST.get('username', '').strip()
        email      = request.POST.get('email', '').strip()

        if not username or not email:
            messages.error(request, 'Username and email are required.')
            return redirect('create_supervisor')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'That username is already taken.')
            return redirect('create_supervisor')

        # Generate a secure temporary password rather than trusting
        # the admin to type a strong one under time pressure.
        alphabet = string.ascii_letters + string.digits
        temp_password = ''.join(secrets.choice(alphabet) for _ in range(12))

        supervisor = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=temp_password,
            first_name=first_name,
            last_name=last_name,
            role='supervisor',
        )

        messages.success(
            request,
            f'Supervisor account created for {supervisor.get_full_name() or supervisor.username}. '
            f'Temporary password: {temp_password} — share this securely and ask them to change it after first login.'
        )
        return redirect('admin_dashboard')

    return render(request, 'accounts/create_supervisor.html')


def landing_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/landing.html')


@admin_required
def delete_user(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id=user_id)
        if user.role != 'admin':
            user.delete()
    return redirect('admin_dashboard')


@admin_required
def assign_supervisors(request):
    students = StudentProfile.objects.select_related('user', 'university_supervisor').all()
    supervisors = CustomUser.objects.filter(role='supervisor')
    return render(request, 'accounts/assign_supervisors.html', {
        'students': students,
        'supervisors': supervisors,
    })


@admin_required
def assign_supervisor_save(request, student_id):
    if request.method == 'POST':
        from students.models import StudentProfile
        student_profile = get_object_or_404(StudentProfile, id=student_id)
        supervisor_id = request.POST.get('supervisor_id')
        if supervisor_id:
            supervisor = get_object_or_404(CustomUser, id=supervisor_id, role='supervisor')
            student_profile.university_supervisor = supervisor
            student_profile.save()
            messages.success(request, f'{student_profile.user.get_full_name()} assigned to {supervisor.get_full_name()}')
        else:
            student_profile.university_supervisor = None
            student_profile.save()
            messages.success(request, 'Supervisor removed from student.')
    return redirect('assign_supervisors')

@admin_required
def message_oversight(request):
    """
    Read-only list of every active supervisor-student conversation,
    for the admin to monitor tone and professionalism. Admins can view
    threads here but there is no reply box — this is oversight, not
    participation.
    """
    assigned_students = StudentProfile.objects.filter(
        university_supervisor__isnull=False
    ).select_related('user', 'university_supervisor')

    conversations = []
    for sp in assigned_students:
        student_user = sp.user
        supervisor_user = sp.university_supervisor

        thread_qs = Message.objects.filter(
            Q(sender=student_user, receiver=supervisor_user) |
            Q(sender=supervisor_user, receiver=student_user)
        )
        last_msg = thread_qs.order_by('-sent_at').first()
        message_count = thread_qs.count()

        conversations.append({
            'student':       sp,
            'supervisor':    supervisor_user,
            'last_message':  last_msg,
            'message_count': message_count,
        })

    # Conversations with messages, most recent first; silent pairs at the bottom
    with_messages    = [c for c in conversations if c['last_message']]
    without_messages = [c for c in conversations if not c['last_message']]
    with_messages.sort(key=lambda c: c['last_message'].sent_at, reverse=True)
    conversations = with_messages + without_messages

    return render(request, 'accounts/message_oversight.html', {
        'conversations': conversations,
    })


@admin_required
def message_oversight_thread(request, student_id, supervisor_id):
    """
    Read-only full thread between one specific student and their
    assigned supervisor. No POST handling here on purpose — admins
    can view, not send.
    """
    student_profile = get_object_or_404(
        StudentProfile, id=student_id, university_supervisor_id=supervisor_id
    )
    student_user = student_profile.user
    supervisor_user = get_object_or_404(CustomUser, id=supervisor_id, role='supervisor')

    thread = Message.objects.filter(
        Q(sender=student_user, receiver=supervisor_user) |
        Q(sender=supervisor_user, receiver=student_user)
    ).order_by('sent_at')

    return render(request, 'accounts/message_oversight_thread.html', {
        'student':    student_profile,
        'supervisor': supervisor_user,
        'thread':     thread,
    })