from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import student_required
from .models import LogbookEntry
from .forms import LogbookEntryForm


@student_required
def submit_logbook(request):
    if request.method == 'POST':
        form = LogbookEntryForm(request.POST, request.FILES)
        if form.is_valid():
            week_number = form.cleaned_data['week_number']

            if week_number < 1 or week_number > 12:
                messages.error(request, 'Week number must be between 1 and 12.')
                return render(request, 'logbook/submit_logbook.html', {'form': form})

            if LogbookEntry.objects.filter(student=request.user, week_number=week_number).exists():
                messages.error(request, f'You have already submitted a logbook entry for Week {week_number}.')
                return render(request, 'logbook/submit_logbook.html', {'form': form})

            entry = form.save(commit=False)
            entry.student = request.user
            entry.save()
            messages.success(request, f'Week {week_number} logbook entry submitted successfully!')
            return redirect('my_logbook')
    else:
        form = LogbookEntryForm()

    return render(request, 'logbook/submit_logbook.html', {'form': form})


@student_required
def my_logbook(request):
    # strictly filter by request.user — no other student's entries can appear
    entries = LogbookEntry.objects.filter(student=request.user).order_by('week_number')
    submitted_weeks = list(entries.values_list('week_number', flat=True))
    remaining_weeks = [w for w in range(1, 13) if w not in submitted_weeks]

    return render(request, 'logbook/my_logbook.html', {
        'entries': entries,
        'submitted_weeks': submitted_weeks,
        'remaining_weeks': remaining_weeks,
        'total_submitted': len(submitted_weeks),
    })


@student_required
def view_entry(request, entry_id):
    # student can only view their OWN entry — 404 if they try another student's
    entry = get_object_or_404(LogbookEntry, id=entry_id, student=request.user)
    return render(request, 'logbook/view_entry.html', {'entry': entry})