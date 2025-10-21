# core/models.py
from django.db import models
from django.utils import timezone


# The Custom Manager for Safe Deletion
class SafeDeleteManager(models.Manager):
    """
    A custom model manager that automatically excludes soft-deleted objects
    from its default queryset.
    """
    def get_queryset(self):
        """
        Overrides the default queryset to filter out objects where is_deleted is True.
        """
        return super().get_queryset().filter(is_deleted=False)

    def all_with_deleted(self):
        """
        Returns a queryset that includes all objects, even soft-deleted ones.
        Useful for admin panels, auditing, or un-deleting.
        """
        return super().get_queryset()

    def deleted_only(self):
        """
        Returns a queryset that includes ONLY soft-deleted objects.
        """
        return super().get_queryset().filter(is_deleted=True)


# The Abstract BaseModel
class BaseModel(models.Model):
    """
    An abstract base model that provides common fields and functionality:
    - created_at: Timestamp for when the record was created.
    - updated_at: Timestamp for the last update.
    - is_deleted: Boolean flag for soft deletion.
    - Custom delete() method to perform a soft delete.
    - A custom manager to handle filtering of soft-deleted records.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        help_text="Timestamp when the record was created."
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        editable=False,
        help_text="Timestamp when the record was last updated."
    )
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,  # Indexing this field is good for query performance
        help_text="Indicates if the record has been soft-deleted."
    )

    # --- Managers ---
    # The 'objects' manager is the default one. By replacing it with our
    # custom manager, all default queries will be "safe".
    objects = SafeDeleteManager()
    
    # We also keep the original, unfiltered manager available for special cases.
    all_objects = models.Manager()

    class Meta:
        # It tells Django that this model is abstract
        # and should not have its own database table.
        abstract = True
        
        # Optional: Default ordering for all inheriting models
        ordering = ['-created_at']

    def delete(self, using=None, keep_parents=False):
        """
        Overrides the default delete method to perform a soft delete.
        It sets the is_deleted flag to True and saves the object.
        """
        self.is_deleted = True
        self.save()

    def undelete(self):
        """
        A helper method to restore a soft-deleted object.
        """
        self.is_deleted = False
        self.save()

    def __str__(self):
        # Provide a sensible default string representation
        return f"Record created on {self.created_at.strftime('%Y-%m-%d %H:%M')}"