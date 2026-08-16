from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.db.models import Q
from django.core.exceptions import PermissionDenied
from students.models import StudentProfile
from messaging.models import Message
from logbook.models import LogbookEntry
from .models import SupervisorProfile
from .forms import SupervisorUserForm, SupervisorProfileForm, LogbookReviewForm
from accounts.decorators import supervisor_required


@supervisor_required
def review_logbook_list(request):
    # only get students assigned to this supervisor
    assigned_students = StudentProfile.objects.filter(
        university_supervisor=request.user
    ).values_list('user', flat=True)

    entries = LogbookEntry.objects.filter(
        student__in=assigned_students
    ).order_by('-submitted_at')

    return render(request, 'supervisors/review_logbook.html', {'entries': entries})


@supervisor_required
def review_logbook_entry(request, entry_id):
    # get the entry but verify the student belongs to this supervisor
    assigned_students = StudentProfile.objects.filter(
        university_supervisor=request.user
    ).values_list('user', flat=True)

    entry = get_object_or_404(LogbookEntry, id=entry_id, student__in=assigned_students)

    if request.method == 'POST':
        form = LogbookReviewForm(request.POST, instance=entry)
        if form.is_valid():
            reviewed_entry = form.save(commit=False)
            reviewed_entry.is_reviewed = True
            reviewed_entry.save()
            django_messages.success(request, 'Review saved successfully')
            return redirect('review_logbook_list')
    else:
        form = LogbookReviewForm(instance=entry)

    return render(request, 'supervisors/grade_entry.html', {'form': form, 'entry': entry})


@supervisor_required
def supervisor_dashboard(request):
    assigned_students = StudentProfile.objects.filter(
        university_supervisor=request.user
    ).select_related('user')

    # get entries only for assigned students
    assigned_user_ids = assigned_students.values_list('user', flat=True)
    entries = LogbookEntry.objects.filter(student__in=assigned_user_ids)

    total_students    = assigned_students.count()
    pending_reviews   = entries.filter(is_reviewed=False).count()
    completed_reviews = entries.filter(is_reviewed=True).count()
    recent_entries    = entries.order_by('-submitted_at')[:5]

    return render(request, 'supervisors/dashboard.html', {
        'assigned_students': assigned_students,
        'total_students':    total_students,
        'pending_reviews':   pending_reviews,
        'completed_reviews': completed_reviews,
        'recent_entries':    recent_entries,
    })


@supervisor_required
def message_list(request):
    assigned_students = StudentProfile.objects.filter(
        university_supervisor=request.user
    ).select_related('user')

    student_data = []
    for sp in assigned_students:
        last_msg = Message.objects.filter(
            Q(sender=request.user, receiver=sp.user) |
            Q(sender=sp.user, receiver=request.user)
        ).order_by('-sent_at').first()
        unread_count = Message.objects.filter(
            sender=sp.user, receiver=request.user, is_read=False
        ).count()
        student_data.append({
            'student':      sp,
            'last_message': last_msg,
            'unread_count': unread_count,
        })

    return render(request, 'supervisors/message_list.html', {
        'student_data': student_data
    })


@supervisor_required
def message_thread(request, student_user_id):
    # ensure this student is actually assigned to this supervisor
    student_profile = get_object_or_404(
        StudentProfile, user_id=student_user_id, university_supervisor=request.user
    )
    student_user = student_profile.user

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Message.objects.create(
                sender=request.user,
                receiver=student_user,
                subject=request.POST.get('subject', ''),
                body=body
            )
        return redirect('message_thread', student_user_id=student_user_id)

    thread = Message.objects.filter(
        Q(sender=request.user, receiver=student_user) |
        Q(sender=student_user, receiver=request.user)
    ).order_by('sent_at')

    thread.filter(sender=student_user, receiver=request.user, is_read=False).update(is_read=True)

    return render(request, 'supervisors/message_thread.html', {
        'student': student_profile,
        'thread':  thread,
    })


@supervisor_required
def supervisor_profile_edit(request):
    profile, _ = SupervisorProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form    = SupervisorUserForm(request.POST, instance=request.user)
        profile_form = SupervisorProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            django_messages.success(request, 'Profile updated successfully')
            return redirect('supervisor_profile_edit')
    else:
        user_form    = SupervisorUserForm(instance=request.user)
        profile_form = SupervisorProfileForm(instance=profile)

    return render(request, 'supervisors/profile_edit.html', {
        'user_form':    user_form,
        'profile_form': profile_form,
    })