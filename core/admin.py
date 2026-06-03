from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Message, Order, Review, Skill, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Profile", {"fields": ("bio", "avatar_url")}),
    )


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "category", "price", "status", "created_at")
    list_filter = ("status", "category")
    search_fields = ("title", "user__username")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "buyer", "skill", "price", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("buyer__username", "skill__title", "stripe_payment_id")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "sender", "sent_at")
    search_fields = ("sender__username",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "reviewer", "rating", "created_at")
    list_filter = ("rating",)
