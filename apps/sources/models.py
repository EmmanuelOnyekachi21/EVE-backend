from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q
import uuid

# Create your models here.
class Source(models.Model):
    """
    Model representing a source of data.
    """
    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    platform = models.CharField(max_length=50)
    external_identifier = models.CharField(max_length=255)
    trust_score = models.SmallIntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    verified = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    last_fetched_at = models.DateTimeField(null=True, blank=True)
    consecutive_errors = models.IntegerField(default=0)
    metadata = models.JSONField(null=True, blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("platform", "external_identifier")
        indexes = [
            models.Index(fields=['platform', 'active']),
        ]
    
    @property
    def trust_tier(self):
        """
        Returns the trust tier of the source.
        """
        if self.trust_score < 40:
            return "low"
        elif self.trust_score < 70:
            return "medium"
        else:
            return "high"
        
    
    def __str__(self):
        """
        Returns a string representation of the source.
        """
        return f"{self.platform}:{self.external_identifier} ({self.trust_score})"


class SourceTrustHistory(models.Model):
    """
    Model representing the trust history of a source.
    """
    source = models.ForeignKey(
        Source,
        on_delete=models.CASCADE,
        related_name='trust_history'
    )
    trust_score = models.SmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    reason = models.TextField()
    changed_by = models.CharField(max_length=100)
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_to = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['source', 'valid_from']),
        ]
        constraints = [
            models.CheckConstraint(
                check=Q(valid_to__isnull=True) | Q(valid_to__gt=models.F('valid_from')),
                name='chk_valid_trust_period'
            )
        ]

    def __str__(self):
        """
        Returns a string representation of the source trust history.
        """
        return f"{self.source} → {self.trust_score} ({self.valid_from.date()})"
