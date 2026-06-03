from django.db import models
from django.contrib.auth.models import User

class RecruiterProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.company_name})"

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=50, unique=True)
    branch = models.CharField(max_length=100)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2)
    skills = models.TextField(help_text="Comma separated skills")
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"

class JobPosting(models.Model):
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    company_name = models.CharField(max_length=200)
    job_role = models.CharField(max_length=200)
    package = models.CharField(max_length=100, help_text="e.g., 12 LPA")
    eligibility = models.TextField(help_text="e.g., Minimum 7.5 CGPA, CSE/IT only")
    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    eligible_branches = models.TextField(help_text="e.g., Computer Science, IT or All", default="All")
    application_deadline = models.DateField(null=True, blank=True, help_text="Deadline to apply for this drive")
    drive_date = models.DateField(null=True, blank=True, help_text="Date of recruitment drive / tests / interviews")
    created_at = models.DateTimeField(auto_now_add=True)

    def is_student_eligible(self, student_profile):
        # 1. Check CGPA
        if student_profile.cgpa < self.min_cgpa:
            return False, f"CGPA of {student_profile.cgpa} is below the required {self.min_cgpa}."
        
        # 2. Check Branch
        eligible_str = self.eligible_branches.strip() if self.eligible_branches else ""
        if eligible_str and eligible_str.lower() != "all":
            allowed_branches = [b.strip().lower() for b in eligible_str.split(',')]
            student_branch = student_profile.branch.strip().lower()
            
            match = False
            for allowed in allowed_branches:
                # Clean strings for robustness
                a_clean = allowed.replace("&", "and")
                s_clean = student_branch.replace("&", "and")
                
                # Check for standard abbreviations or simple substring presence
                if a_clean in s_clean or s_clean in a_clean:
                    match = True
                    break
                
                # Common branch abbreviations
                abbrev_map = {
                    'cse': 'computer science',
                    'it': 'information technology',
                    'ece': 'electronics',
                    'eee': 'electrical',
                    'me': 'mechanical',
                    'ce': 'civil'
                }
                for abbrev, full in abbrev_map.items():
                    if allowed == abbrev:
                        if full in s_clean:
                            match = True
                            break
            
            if not match:
                return False, f"Branch '{student_profile.branch}' is not eligible. Allowed: {self.eligible_branches}."
                
        return True, "Eligible"

    def __str__(self):
        return f"{self.company_name} - {self.job_role}"

class Application(models.Model):
    STATUS_CHOICES = (
        ('Applied', 'Applied'),
        ('Shortlisted', 'Shortlisted'),
        ('Selected', 'Selected'),
        ('Rejected', 'Rejected'),
    )
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Applied')
    applied_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'job')

    def __str__(self):
        return f"{self.student.user.username} -> {self.job.company_name} ({self.status})"

class Notification(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.student.user.username}: {self.message[:30]}"
