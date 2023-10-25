from django.db import models


class CommonModel(models.Model):

    """Common Model Definition"""

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True,
    )

    class Meta:
        abstract = True
