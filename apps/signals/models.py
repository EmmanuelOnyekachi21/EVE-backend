from django.db import models
import uuid
from django.contrib.gis.db import models as gis_models
from apps.sources.models import Source
from django.utils import timezone
import hashlib
import json

# Create your models here.
class Signal(models.Model):
    """
    Model representing a signal.
    """
    SIGNAL_TYPES = (
        ('robbery', 'Robbery'),
        ('assault', 'Assault'),
        ('burglary', 'Burglary'),
        ('vehicle_theft', 'Vehicle Theft'),
        ('harassment', 'Harassment'),
        ('other', 'Other'),
    )
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    content = models.TextField()
    signal_type = models.CharField(max_length=20, choices=SIGNAL_TYPES)
    location = gis_models.PointField(srid=4326)
    occurred_at = models.DateTimeField()
    source = models.ForeignKey(
        Source,
        on_delete=models.RESTRICT,
        related_name='signals',
    )
    source_metadata = models.JSONField(default=dict, blank=True, null=True)
    dedup_hash = models.CharField(
        max_length=64,
        unique=True,
        blank=True,
        help_text='SHA256 hash of the signal content and location',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['signal_type', 'location']),
            models.Index(fields=['occurred_at']),
        ]
        ordering = ['-occurred_at']

    def clean(self):
        """
        Clean the signal data.
        """
        if self.occurred_at and self.occurred_at > timezone.now():
            raise ValueError('Signal cannot be in the future')
    
    def save(self, *args, **kwargs):
        """
        Save the signal data.
        """
        # Generate dedup_hash before validation
        if not self.dedup_hash:
            self.dedup_hash = self.compute_dedup_hash(
                self.source_id, 
                self.signal_type, 
                self.location,
                self.occurred_at
            )
        
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.signal_type} at {self.location}'
    
    @staticmethod
    def compute_dedup_hash(source_id, signal_type, location, occurred_at):
        """
        Compute the deduplication hash for the signal.
        """
        # Round coordinates to 5 decimal places
        rounded_coords = (round(location.x, 5), round(location.y, 5))
        
        # Truncate timestamp to minute
        truncated_time = occurred_at.replace(second=0, microsecond=0)
        
        # Convert the signal data to a JSON string
        signal_data = json.dumps({
            'source_id': str(source_id),
            'signal_type': signal_type,
            'location': rounded_coords,
            'occurred_at': truncated_time.isoformat(),
        }, sort_keys=True)

        # Compute the SHA256 hash of the signal data
        return hashlib.sha256(signal_data.encode('utf-8')).hexdigest()