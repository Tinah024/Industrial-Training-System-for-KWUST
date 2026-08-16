from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.decorators import student_required
from .models import StudentProfile
from .forms import StudentProfileForm


@student_required
def my_profile(request):
    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        form = StudentProfileForm(request.POST, instance=profile)
        if form.is_valid():
            new_profile = form.save(commit=False)
            new_profile.user = request.user
            new_profile.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('my_profile')
    else:
        form = StudentProfileForm(instance=profile)

    return render(request, 'students/profile.html', {'form': form, 'profile': profile})