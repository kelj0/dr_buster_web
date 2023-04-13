from django.db import models
import uuid


class Wordlist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.BinaryField()


class Scan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    result = models.JSONField(default=dict({'count': 0, 'urls': []}))

