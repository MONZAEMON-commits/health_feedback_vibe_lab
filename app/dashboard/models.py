from django.db import models


class SystemSetting(models.Model):
    admin_timeout_minutes = models.PositiveIntegerField()
