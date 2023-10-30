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

    def formatted_created_at(self):
        return (
            self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        )

    def formatted_updated_at(self):
        return (
            self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None
        )
