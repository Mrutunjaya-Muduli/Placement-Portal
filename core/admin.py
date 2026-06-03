from django.contrib import admin
from .models import StudentProfile, JobPosting, Application, RecruiterProfile

# --- Custom Admin Site Branding Configuration ---
admin.site.site_header = "🎓 Placement Portal Admin Hub"
admin.site.site_title = "Placement Portal Admin Portal"
admin.site.index_title = "System Management & Placement Control Center"

@admin.register(RecruiterProfile)
class RecruiterProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name')
    search_fields = ('user__username', 'user__first_name', 'company_name')

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('get_full_name', 'student_id', 'branch', 'cgpa', 'skills_summary', 'has_resume')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'student_id', 'branch', 'skills')
    list_filter = ('branch', 'cgpa')
    ordering = ('-cgpa',)

    @admin.display(description='Student Name')
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    @admin.display(description='Skills')
    def skills_summary(self, obj):
        if obj.skills and len(obj.skills) > 40:
            return obj.skills[:37] + "..."
        return obj.skills or "N/A"

    @admin.display(boolean=True, description='Has Resume')
    def has_resume(self, obj):
        return bool(obj.resume)


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'job_role', 'package', 'min_cgpa', 'eligible_branches', 'created_at')
    search_fields = ('company_name', 'job_role', 'eligibility', 'eligible_branches')
    list_filter = ('eligible_branches', 'min_cgpa', 'created_at')
    ordering = ('-created_at',)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'get_student_branch', 'get_student_cgpa', 'job', 'status', 'applied_on')
    list_filter = ('status', 'applied_on', 'job__company_name')
    search_fields = (
        'student__user__username', 
        'student__user__first_name', 
        'student__student_id', 
        'job__company_name', 
        'job__job_role'
    )
    ordering = ('-applied_on',)
    
    # Custom bulk status actions
    actions = ['mark_as_shortlisted', 'mark_as_selected', 'mark_as_rejected']

    @admin.display(description='Branch')
    def get_student_branch(self, obj):
        return obj.student.branch

    @admin.display(description='CGPA')
    def get_student_cgpa(self, obj):
        return obj.student.cgpa

    # Bulk action methods
    @admin.action(description='Mark selected applications as Shortlisted')
    def mark_as_shortlisted(self, request, queryset):
        rows_updated = queryset.update(status='Shortlisted')
        self.message_user(request, f"{rows_updated} applications successfully marked as Shortlisted.")

    @admin.action(description='Mark selected applications as Selected')
    def mark_as_selected(self, request, queryset):
        rows_updated = queryset.update(status='Selected')
        self.message_user(request, f"{rows_updated} applications successfully marked as Selected.")

    @admin.action(description='Mark selected applications as Rejected')
    def mark_as_rejected(self, request, queryset):
        rows_updated = queryset.update(status='Rejected')
        self.message_user(request, f"{rows_updated} applications successfully marked as Rejected.")
