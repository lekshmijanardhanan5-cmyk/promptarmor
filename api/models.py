from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User


class PromptLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='prompt_logs'
    )
    prompt = models.TextField(blank=True, default="")
    decision = models.CharField(max_length=10)
    risk_score = models.IntegerField()
    triggers = models.JSONField(default=list)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User: {self.user.username} | Decision: {self.decision} | Score: {self.risk_score}"
