from django.db import models
from common.models import CommonModel


class Board(CommonModel):
    class FeedChoices(models.TextChoices):
        """Feed Choices Definition"""

        FACEBOOK = "facebook", "Facebook"
        TWITTER = "twitter", "Twitter"
        INSTAGRAM = "instagram", "Instagram"
        THREADS = "threads", "Threads"

    title = models.CharField(
        max_length=80,
        blank=False,
        null=False,
    )
    feed_type = models.CharField(
        max_length=30,
        choices=FeedChoices.choices,
        blank=False,
        null=False,
    )
    content = models.TextField(
        max_length=500,
        blank=True,
        null=True,
    )

    hashtags = models.TextField(
        max_length=500,
        blank=True,
        null=True,
    )

    viewcounts = models.PositiveIntegerField(default=0)
    likecounts = models.PositiveIntegerField(default=0)
    sharecounts = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
