from django.db import models
from common.models import CommonModel

class Hashtag(models.Model):
    tag = models.CharField(
        max_length=30,
        unique=True,
        blank=False,
        null=False)

    def __str__(self):
        return self.tag

class Board(CommonModel):
    class FeedChoices(models.TextChoices):
        """Feed Choices Definition"""

        FACEBOOK = "facebook", "Facebook"
        TWITTER = "twitter", "Twitter"
        INSTAGRAM = "instagram", "Instagram"
        THREADS = "threads", "Threads"

    content_id = models.AutoField(
        primary_key=True,
        editable=False,
    )

    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="boards",
        blank=False,
    )

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

    hashtags = models.ManyToManyField(
        Hashtag,
        related_name='tagging',
        blank=True,
    )

    # likes = models.BooleanField(default=False)
    liked_users = models.ManyToManyField(
        "users.User",
        related_name="liked_boards",
        blank=True,
    )

    viewcounts = models.PositiveIntegerField(default=0)
    likecounts = models.PositiveIntegerField(default=0)
    sharecounts = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
