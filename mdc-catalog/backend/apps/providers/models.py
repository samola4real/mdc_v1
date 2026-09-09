import uuid

from django.db import models


class Provider(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"
        ARCHIVED = "archived", "Archived"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider_id = models.CharField(max_length=255, unique=True)
    provider_name = models.CharField(max_length=255)
    country = models.CharField(max_length=100)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    custom_provider_fields = models.JSONField(default=dict, blank=True)
    publication_metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.provider_id}: {self.provider_name}"


class Offering(models.Model):
    class SupportStatus(models.TextChoices):
        CONFIRMED = "confirmed", "Confirmed"
        CANDIDATE_REQUIRING_CONFIRMATION = (
            "candidate_requiring_confirmation", "Candidate requiring confirmation"
        )
        UNKNOWN = "unknown", "Unknown"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    offering_id = models.CharField(max_length=512, unique=True)
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="offerings")
    offering_name = models.CharField(max_length=255)
    service_category = models.CharField(max_length=255)
    part_family = models.CharField(max_length=255)
    support_status = models.CharField(
        max_length=32, choices=SupportStatus.choices, default=SupportStatus.UNKNOWN
    )
    supported_part_types = models.JSONField(default=list, blank=True)
    family_capabilities = models.JSONField(default=dict, blank=True)
    part_type_capabilities = models.JSONField(default=dict, blank=True)
    generic_capabilities = models.JSONField(default=dict, blank=True)
    custom_offering_fields = models.JSONField(default=dict, blank=True)
    custom_capability_fields = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    sequence_index = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.offering_id}: {self.offering_name}"


class ProviderCertification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(
        Provider, on_delete=models.CASCADE, related_name="certifications"
    )
    code = models.CharField(max_length=255)
    source_type = models.CharField(max_length=64)
    confidence = models.CharField(max_length=64)
    source_note = models.TextField(null=True, blank=True)
    # An omitted note differs from an explicitly supplied null in canonical records.
    source_note_present = models.BooleanField(default=False)
    sequence_index = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["provider", "code"], name="unique_provider_certification")
        ]

    def __str__(self):
        return f"{self.provider_id}: {self.code}"


class ProviderPublication(models.Model):
    class Operation(models.TextChoices):
        CREATE = "create", "Create"
        UPDATE = "update", "Update"

    class Status(models.TextChoices):
        RECEIVED = "received", "Received"
        VALIDATION_FAILED = "validation_failed", "Validation failed"
        VALIDATED = "validated", "Validated"
        PERSISTED = "persisted", "Persisted"
        SYNC_PENDING = "sync_pending", "Sync pending"
        SYNCED = "synced", "Synced"
        SYNC_FAILED = "sync_failed", "Sync failed"
        REJECTED = "rejected", "Rejected"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.ForeignKey(
        Provider, null=True, blank=True, on_delete=models.SET_NULL, related_name="publications"
    )
    provider_id_snapshot = models.CharField(max_length=255)
    operation = models.CharField(max_length=16, choices=Operation.choices)
    status = models.CharField(max_length=24, choices=Status.choices, default=Status.RECEIVED)
    contract_version = models.CharField(max_length=32, default="1.0")
    submitted_payload = models.JSONField(default=dict)
    normalized_payload = models.JSONField(default=dict)
    submitted_by_external_id = models.CharField(max_length=255, null=True, blank=True)
    validation_errors = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    validated_at = models.DateTimeField(null=True, blank=True)
    persisted_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.id}: {self.provider_id_snapshot} ({self.status})"


class CatalogueSyncEvent(models.Model):
    class EntityType(models.TextChoices):
        PROVIDER = "provider", "Provider"
        OFFERING = "offering", "Offering"

    class Operation(models.TextChoices):
        UPSERT = "upsert", "Upsert"
        DELETE = "delete", "Delete"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    publication = models.ForeignKey(
        ProviderPublication, on_delete=models.CASCADE, related_name="sync_events"
    )
    entity_type = models.CharField(max_length=16, choices=EntityType.choices)
    entity_id = models.CharField(max_length=512)
    operation = models.CharField(max_length=16, choices=Operation.choices)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    attempt_count = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["status", "created_at"], name="sync_status_created_idx")]

    def __str__(self):
        return f"{self.operation} {self.entity_type} {self.entity_id} ({self.status})"
