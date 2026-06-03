from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import StudentProfile, JobPosting, Application, RecruiterProfile
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme

def home(request):
    from .models import StudentProfile, RecruiterProfile, JobPosting, Application
    
    total_students = StudentProfile.objects.count()
    total_recruiters = RecruiterProfile.objects.count()
    active_drives = JobPosting.objects.count()
    
    # Number of unique students who are Selected
    placed_students = Application.objects.filter(status='Selected').values('student').distinct().count()
    
    # Fetch active companies from jobs
    active_companies = list(JobPosting.objects.values_list('company_name', flat=True).distinct())
    
    # Default set of top companies to guarantee a beautiful full marquee list
    default_companies = ["Google", "Stripe", "Microsoft", "Meta", "Amazon", "TechCorp"]
    companies_list = list(dict.fromkeys(active_companies + default_companies))
    
    # Retrieve top 3 featured drives
    featured_drives = JobPosting.objects.all().order_by('-created_at')[:3]
    
    context = {
        'total_students': total_students,
        'total_recruiters': total_recruiters,
        'active_drives': active_drives,
        'placed_students': placed_students,
        'companies': companies_list,
        'featured_drives': featured_drives,
    }
    return render(request, 'core/home.html', context)

def register(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        n = request.POST.get('name')
        e = request.POST.get('email')
        sid = request.POST.get('student_id')
        branch = request.POST.get('branch')
        cgpa = request.POST.get('cgpa')
        skills = request.POST.get('skills')
        resume = request.FILES.get('resume')
        
        if User.objects.filter(username=u).exists():
            messages.error(request, 'Username already exists')
            return redirect('register')
            
        user = User.objects.create_user(username=u, password=p, email=e, first_name=n)
        StudentProfile.objects.create(
            user=user, student_id=sid, branch=branch, cgpa=cgpa, skills=skills, resume=resume
        )
        login(request, user)
        return redirect('student_dashboard')
        
    return render(request, 'core/register.html')

def register_recruiter(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        n = request.POST.get('name')
        e = request.POST.get('email')
        c_name = request.POST.get('company_name')
        
        if User.objects.filter(username=u).exists():
            messages.error(request, 'Username already exists')
            return redirect('register_recruiter')
            
        user = User.objects.create_user(username=u, password=p, email=e, first_name=n)
        RecruiterProfile.objects.create(
            user=user, company_name=c_name
        )
        login(request, user)
        return redirect('company_dashboard')
        
    return render(request, 'core/register_recruiter.html')

def user_login(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        role = request.POST.get('role', 'student')
        
        user = authenticate(request, username=u, password=p)
        if user is not None:
            # Check user role mapping
            is_student = hasattr(user, 'studentprofile')
            is_admin = user.is_staff
            is_company = hasattr(user, 'recruiterprofile')
            
            role_valid = False
            error_msg = ""
            
            if role == 'student':
                if is_student:
                    role_valid = True
                else:
                    error_msg = "This account is not registered as a Student."
            elif role == 'company':
                if is_company:
                    role_valid = True
                else:
                    error_msg = "This account is not registered as a Recruiter/Company."
            elif role == 'admin':
                if is_admin:
                    role_valid = True
                else:
                    error_msg = "This account does not have administrative privileges."
            
            if role_valid:
                login(request, user)
                next_url = request.GET.get('next') or request.POST.get('next')
                if next_url and url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}):
                    return redirect(next_url)
                if is_student:
                    return redirect('student_dashboard')
                elif is_admin:
                    return redirect('admin_dashboard')
                else:
                    return redirect('company_dashboard')
            else:
                messages.error(request, error_msg)
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'core/login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def student_dashboard(request):
    try:
        profile = request.user.studentprofile
    except (AttributeError, StudentProfile.DoesNotExist):
        messages.error(request, 'Access denied. Student profile required.')
        return redirect('home')
    applications = Application.objects.filter(student=profile)
    
    from .models import Notification
    notifications = Notification.objects.filter(student=profile).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'profile': profile,
        'applications': applications,
        'notifications': notifications[:5],
        'unread_count': unread_count
    }
    return render(request, 'core/student_dashboard.html', context)

@login_required
def mark_notifications_read(request):
    try:
        profile = request.user.studentprofile
    except (AttributeError, StudentProfile.DoesNotExist):
        messages.error(request, 'Access denied. Student profile required.')
        return redirect('home')
        
    from .models import Notification
    Notification.objects.filter(student=profile, is_read=False).update(is_read=True)
    messages.success(request, 'All notifications marked as read.')
    return redirect('student_dashboard')

@login_required
def edit_profile(request):
    try:
        profile = request.user.studentprofile
    except (AttributeError, StudentProfile.DoesNotExist):
        messages.error(request, 'Access denied. Student profile required.')
        return redirect('home')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        student_id = request.POST.get('student_id')
        branch = request.POST.get('branch')
        cgpa = request.POST.get('cgpa')
        skills = request.POST.get('skills')
        resume = request.FILES.get('resume')
        
        # Check duplicate Student ID
        if StudentProfile.objects.exclude(user=request.user).filter(student_id=student_id).exists():
            messages.error(request, f'Student ID "{student_id}" already exists.')
            return render(request, 'core/edit_profile.html', {'profile': profile})
            
        # Update User model details
        request.user.first_name = name
        request.user.email = email
        request.user.save()
        
        # Update StudentProfile model details
        profile.student_id = student_id
        profile.branch = branch
        profile.cgpa = cgpa
        profile.skills = skills
        if resume:
            profile.resume = resume
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('student_dashboard')
        
    return render(request, 'core/edit_profile.html', {'profile': profile})

def job_list(request):
    profile = None
    if request.user.is_authenticated:
        try:
            profile = request.user.studentprofile
        except (AttributeError, StudentProfile.DoesNotExist):
            profile = None
    jobs = JobPosting.objects.all().order_by('-created_at')
    
    # 🔍 Simple search & branch filters
    search_query = request.GET.get('search', '').strip()
    branch_query = request.GET.get('branch', '').strip()
    
    if search_query:
        from django.db.models import Q
        jobs = jobs.filter(
            Q(company_name__icontains=search_query) | 
            Q(job_role__icontains=search_query) | 
            Q(eligibility__icontains=search_query)
        )
        
    if branch_query:
        from django.db.models import Q
        jobs = jobs.filter(
            Q(eligible_branches__icontains=branch_query) | 
            Q(eligible_branches__icontains='All')
        )
    
    # Pre-calculate eligibility status for the logged-in student
    for job in jobs:
        if profile:
            is_eligible, reason = job.is_student_eligible(profile)
            job.is_eligible = is_eligible
            job.eligibility_reason = reason
            job.has_applied = Application.objects.filter(student=profile, job=job).exists()
        else:
            job.is_eligible = True
            job.eligibility_reason = "Eligible"
            job.has_applied = False
            
    return render(request, 'core/job_list.html', {'jobs': jobs, 'profile': profile})

@login_required
def apply_job(request, job_id):
    if request.method == 'POST':
        job = get_object_or_404(JobPosting, id=job_id)
        try:
            profile = request.user.studentprofile
        except (AttributeError, StudentProfile.DoesNotExist):
            messages.error(request, 'Only registered students can apply for placement drives.')
            return redirect('job_list')
            
        # Verify eligibility
        is_eligible, reason = job.is_student_eligible(profile)
        if not is_eligible:
            messages.error(request, f'Application failed: {reason}')
            return redirect('job_list')
            
        if not Application.objects.filter(student=profile, job=job).exists():
            Application.objects.create(student=profile, job=job)
            messages.success(request, f'Successfully applied for {job.company_name}')
        else:
            messages.warning(request, 'You have already applied for this job')
    return redirect('job_list')

@login_required
def company_dashboard(request):
    try:
        profile = request.user.recruiterprofile
    except (AttributeError, RecruiterProfile.DoesNotExist):
        messages.error(request, 'Access denied. Recruiter account required.')
        return redirect('home')
        
    # Only show drives posted by this specific recruiter user
    jobs = JobPosting.objects.filter(recruiter=request.user).order_by('-created_at')
    return render(request, 'core/company_dashboard.html', {'jobs': jobs, 'profile': profile})

@login_required
def post_job(request):
    try:
        profile = request.user.recruiterprofile
    except (AttributeError, RecruiterProfile.DoesNotExist):
        messages.error(request, 'Access denied. Recruiter account required.')
        return redirect('home')
        
    if request.method == 'POST':
        role = request.POST.get('job_role')
        pkg = request.POST.get('package')
        elig = request.POST.get('eligibility')
        min_cgpa_val = request.POST.get('min_cgpa', '0.00')
        eligible_branches_val = request.POST.get('eligible_branches', 'All')
        deadline_val = request.POST.get('application_deadline') or None
        drive_date_val = request.POST.get('drive_date') or None
        
        try:
            min_cgpa_dec = float(min_cgpa_val)
        except ValueError:
            min_cgpa_dec = 0.00
            
        JobPosting.objects.create(
            recruiter=request.user,
            company_name=profile.company_name,  # Prefilled from profile!
            job_role=role, 
            package=pkg, 
            eligibility=elig,
            min_cgpa=min_cgpa_dec,
            eligible_branches=eligible_branches_val,
            application_deadline=deadline_val,
            drive_date=drive_date_val
        )
        messages.success(request, 'Job posted successfully!')
        return redirect('company_dashboard')
    return render(request, 'core/post_job.html', {'profile': profile})

@login_required
def view_candidates(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id)
    applications = Application.objects.filter(job=job)
    return render(request, 'core/view_candidates.html', {'job': job, 'applications': applications})

@login_required
def update_status(request, application_id):
    if request.method == 'POST':
        app = get_object_or_404(Application, id=application_id)
        new_status = request.POST.get('status')
        
        if app.status != new_status:
            old_status = app.status
            app.status = new_status
            app.save()
            
            # Create a Notification record
            message = f"Your application for '{app.job.job_role}' at {app.job.company_name} has been updated from '{old_status}' to '{new_status}'."
            from .models import Notification
            Notification.objects.create(student=app.student, message=message)
            
            # Simulated status update email logs
            from django.core.mail import send_mail
            from django.conf import settings
            subject = f"Status Update: {app.job.company_name} - {app.job.job_role}"
            body = f"Hello {app.student.user.first_name},\n\n{message}\n\nPlease check your student dashboard.\n\nBest,\nPlacement Portal Team"
            
            try:
                send_mail(
                    subject,
                    body,
                    settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@placementportal.com',
                    [app.student.user.email],
                    fail_silently=True,
                )
            except Exception as e:
                # Fallback email console logger
                print(f"[Email Log] To: {app.student.user.email} | Subject: {subject} | Body: {body}")
                
            messages.success(request, 'Status updated and notification sent successfully')
        else:
            messages.info(request, 'No changes made to the status')
            
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('view_candidates', job_id=app.job.id)
    return redirect('company_dashboard')

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Administrator privileges required.')
        return redirect('home')
        
    from django.db.models import Avg
    
    # Calculate statistics
    total_students = StudentProfile.objects.count()
    total_drives = JobPosting.objects.count()
    total_applications = Application.objects.count()
    
    selected_count = Application.objects.filter(status='Selected').count()
    placed_percentage = round((selected_count / total_applications * 100), 1) if total_applications > 0 else 0.0
    
    avg_cgpa_dict = StudentProfile.objects.aggregate(Avg('cgpa'))
    avg_cgpa = round(avg_cgpa_dict['cgpa__avg'], 2) if avg_cgpa_dict['cgpa__avg'] is not None else 0.00
    
    # Fetch lists
    students = StudentProfile.objects.all().order_by('-cgpa')
    jobs = JobPosting.objects.all().order_by('-created_at')
    applications = Application.objects.all().order_by('-applied_on')
    
    # Fetch recruiters and calculate their posted job counts
    recruiters = RecruiterProfile.objects.all().order_by('company_name')
    for r in recruiters:
        r.num_drives = JobPosting.objects.filter(recruiter=r.user).count()
        
    context = {
        'total_students': total_students,
        'total_drives': total_drives,
        'total_applications': total_applications,
        'placed_percentage': placed_percentage,
        'avg_cgpa': avg_cgpa,
        'students': students,
        'jobs': jobs,
        'applications': applications,
        'recruiters': recruiters,
    }
    
    return render(request, 'core/admin_dashboard.html', context)

@login_required
def export_job_ics(request, job_id):
    from django.http import HttpResponse
    job = get_object_or_404(JobPosting, id=job_id)
    import datetime
    
    # Generate standard ICS lines
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Placement Portal//Calendar Export//EN",
        "CALSCALE:GREGORIAN",
    ]
    
    # Add application deadline event
    if job.application_deadline:
        # Midnight UTC on that day
        dt = datetime.datetime.combine(job.application_deadline, datetime.time(23, 59, 0))
        dt_str = dt.strftime("%Y%m%dT%H%M%SZ")
        ics_lines.extend([
            "BEGIN:VEVENT",
            f"UID:deadline_{job.id}@placementportal.edu",
            f"DTSTAMP:{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART:{dt_str}",
            f"DTEND:{dt_str}",
            f"SUMMARY:Apply By: {job.company_name} - {job.job_role}",
            f"DESCRIPTION:Deadline to submit application for {job.job_role} at {job.company_name}. Compensation: {job.package}.",
            "END:VEVENT"
        ])
        
    # Add drive date event
    if job.drive_date:
        # Start at 9 AM and end at 5 PM on that day
        start_dt = datetime.datetime.combine(job.drive_date, datetime.time(9, 0, 0))
        end_dt = datetime.datetime.combine(job.drive_date, datetime.time(17, 0, 0))
        
        ics_lines.extend([
            "BEGIN:VEVENT",
            f"UID:drive_{job.id}@placementportal.edu",
            f"DTSTAMP:{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}",
            f"DTSTART:{start_dt.strftime('%Y%m%dT%H%M%SZ')}",
            f"DTEND:{end_dt.strftime('%Y%m%dT%H%M%SZ')}",
            f"SUMMARY:Placement Drive: {job.company_name} - {job.job_role}",
            f"DESCRIPTION:Placement recruitment drive / interviews for {job.job_role} at {job.company_name}. Package: {job.package}.",
            "END:VEVENT"
        ])
        
    ics_lines.append("END:VCALENDAR")
    
    response = HttpResponse("\r\n".join(ics_lines), content_type="text/calendar")
    response['Content-Disposition'] = f'attachment; filename="{job.company_name}_drive.ics"'
    return response

def placement_calendar(request):
    import json
    from django.core.serializers.json import DjangoJSONEncoder
    
    jobs = JobPosting.objects.all()
    events = []
    
    for job in jobs:
        if job.application_deadline:
            events.append({
                'id': job.id,
                'title': f"{job.company_name} - Apply Deadline",
                'date': job.application_deadline.strftime("%Y-%m-%d"),
                'type': 'deadline',
                'company': job.company_name,
                'role': job.job_role,
                'package': job.package,
                'cgpa': str(job.min_cgpa)
            })
        if job.drive_date:
            events.append({
                'id': job.id,
                'title': f"{job.company_name} - Drive Date",
                'date': job.drive_date.strftime("%Y-%m-%d"),
                'type': 'drive',
                'company': job.company_name,
                'role': job.job_role,
                'package': job.package,
                'cgpa': str(job.min_cgpa)
            })
            
    # Also fetch upcoming events sorted by date
    import datetime
    today = datetime.date.today()
    upcoming_events = []
    for e in events:
        event_date = datetime.datetime.strptime(e['date'], "%Y-%m-%d").date()
        if event_date >= today:
            upcoming_events.append({
                **e,
                'date_obj': event_date
            })
            
    upcoming_events.sort(key=lambda x: x['date_obj'])
    
    context = {
        'events_json': json.dumps(events, cls=DjangoJSONEncoder),
        'upcoming_events': upcoming_events[:8], # Show top 8 upcoming events in sidebar
    }
    
    return render(request, 'core/placement_calendar.html', context)
