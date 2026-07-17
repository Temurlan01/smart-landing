from typing import Optional
from api.models import ContactSubmission
from django.db.models import QuerySet

class ContactRepository:
    @staticmethod
    def create(**kwargs) -> ContactSubmission:
        return ContactSubmission.objects.create(**kwargs)

    @staticmethod
    def all() -> QuerySet:
        return ContactSubmission.objects.all()

    @staticmethod
    def get_by_id(pk) -> Optional[ContactSubmission]:
        try:
            return ContactSubmission.objects.get(pk=pk)
        except ContactSubmission.DoesNotExist:
            return None