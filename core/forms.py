from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Message, Review, Skill, User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ("title", "description", "price", "category", "status", "image")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ("body",)
        widgets = {
            "body": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "メッセージを入力...",
            }),
        }
        labels = {"body": ""}


_RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=_RATING_CHOICES,
        widget=forms.RadioSelect,
        label="評価（1〜5）",
    )

    class Meta:
        model = Review
        fields = ("rating", "comment")
        widgets = {
            "comment": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }
        labels = {"comment": "コメント（任意）"}
