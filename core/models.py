from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class User(AbstractUser):
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)


class Skill(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="skills")
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.PositiveIntegerField()
    category = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")
    image = models.ImageField(upload_to="skills/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="orders")
    price = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    stripe_payment_id = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} — {self.skill.title}"


class Message(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} on Order #{self.order_id}"


class Review(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="review")
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for Order #{self.order_id} — {self.rating}/5"
