from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser
from students.models import StudentProfile
from .models import Message, Notification


@login_required
def inbox(request):
    received = Message.objects.filter(receiver=request.user).order_by('-sent_at')
    sent = Message.objects.filter(sender=request.user).order_by('-sent_at')

    return render(request, 'messaging/inbox.html', {
        'received': received,
        'sent': sent,
    })


@login_required
def chat(request, user_id):
    other_user = get_object_or_404(CustomUser, id=user_id)

    if request.user.role == 'student':
        # student can only chat with their assigned supervisor
        if other_user.role != 'supervisor':
            raise PermissionDenied
        try:
            student_profile = StudentProfile.objects.get(user=request.user)
            if student_profile.university_supervisor != other_user:
                raise PermissionDenied
        except StudentProfile.DoesNotExist:
            raise PermissionDenied

    elif request.user.role == 'supervisor':
        # supervisor can only chat with a student assigned to them
        if other_user.role != 'student':
            raise PermissionDenied
        is_assigned = StudentProfile.objects.filter(
            user=other_user, university_supervisor=request.user
        ).exists()
        if not is_assigned:
            raise PermissionDenied

    else:
        # admins use message_oversight for read-only viewing, not this view
        raise PermissionDenied

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                subject=request.POST.get('subject', ''),
                body=body
            )
        return redirect('messaging:chat', user_id=user_id)

    thread = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by('sent_at')

    thread.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)

    return render(request, 'messaging/chat.html', {
        'other_user': other_user,
        'messages': thread,
    })


@login_required
def notifications(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, 'messaging/notifications.html', {
        'notifications': notifications,
    })