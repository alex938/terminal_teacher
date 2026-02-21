from django.db import models
from django.utils import timezone


class TeachingSession(models.Model):
    """Represents a teaching session (e.g., one class period or day)."""
    title = models.CharField(
        max_length=200,
        help_text="Session title or date"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Only one session should be active at a time"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', '-created_at']),
        ]

    def __str__(self):
        return f"{self.title} ({'Active' if self.is_active else 'Inactive'})"

    @classmethod
    def get_active_session(cls):
        """Get or create the active session."""
        session = cls.objects.filter(is_active=True).first()
        if not session:
            session = cls.objects.create(
                title=f"Session {timezone.now().strftime('%Y-%m-%d %H:%M')}",
                is_active=True
            )
        return session


class CommandEntry(models.Model):
    """Represents a single command entered by the teacher."""
    session = models.ForeignKey(
        TeachingSession,
        on_delete=models.CASCADE,
        related_name='commands'
    )
    command_text = models.TextField(help_text="The command text (no output)")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
        ]
        verbose_name_plural = "Command entries"

    def __str__(self):
        return f"{self.command_text[:50]} ({self.created_at})"
