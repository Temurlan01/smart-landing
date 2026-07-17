from django.contrib import admin
from api.models import ContactSubmission

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'sentiment', 'request_type', 'created_at')
    list_filter = ('sentiment', 'request_type', 'created_at')
    search_fields = ('name', 'email', 'comment')
    readonly_fields = ('id', 'created_at', 'updated_at', 'ip_address')

    fieldsets = (
        ('Personal Information', {
            'fields': ('id', 'name', 'email', 'phone')
        }),
        ('Message', {
            'fields': ('comment',)
        }),
        ('AI Analysis', {
            'fields': ('sentiment', 'request_type', 'ai_response')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )