from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Report
from .forms import ReportForm


@login_required
def upload_report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.student = request.user
            report.save()
            messages.success(request, 'Report submitted successfully')
            return redirect('upload_report')
    else:
        form = ReportForm()

    my_reports = Report.objects.filter(student=request.user).order_by('-submitted_at')
    return render(request, 'reports/upload_report.html', {
        'form': form,
        'my_reports': my_reports,
    })