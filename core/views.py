import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Avg, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .forms import MessageForm, RegisterForm, ReviewForm, SkillForm
from .models import Order, Review, Skill, User

stripe.api_key = settings.STRIPE_SECRET_KEY


# ── 認証 ──────────────────────────────────────────────────────────────────────

def index(request):
    return render(request, "core/index.html")


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"ようこそ、{user.username} さん！")
            return redirect("index")
    else:
        form = RegisterForm()
    return render(request, "core/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("index")
        messages.error(request, "ユーザー名またはパスワードが正しくありません。")
    return render(request, "core/login.html")


def logout_view(request):
    if request.method == "POST":
        logout(request)
    return redirect("index")


@login_required
def mypage(request):
    return render(request, "core/mypage.html")


# ── スキル CRUD ────────────────────────────────────────────────────────────────

def skill_list(request):
    skills = Skill.objects.filter(status="active").select_related("user")

    category = request.GET.get("category", "").strip()
    keyword = request.GET.get("keyword", "").strip()

    if category:
        skills = skills.filter(category=category)
    if keyword:
        skills = skills.filter(
            Q(title__icontains=keyword) | Q(description__icontains=keyword)
        )

    categories = (
        Skill.objects.filter(status="active")
        .values_list("category", flat=True)
        .distinct()
        .order_by("category")
    )

    paginator = Paginator(skills, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "core/skill_list.html", {
        "page_obj": page_obj,
        "categories": categories,
        "selected_category": category,
        "keyword": keyword,
    })


def skill_detail(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    return render(request, "core/skill_detail.html", {"skill": skill})


@login_required
def skill_new(request):
    if request.method == "POST":
        form = SkillForm(request.POST, request.FILES)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user = request.user
            skill.save()
            messages.success(request, "スキルを出品しました！")
            return redirect("skill_detail", pk=skill.pk)
    else:
        form = SkillForm()
    return render(request, "core/skill_form.html", {"form": form, "action": "出品する"})


@login_required
def skill_edit(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    if skill.user != request.user:
        raise PermissionDenied
    if request.method == "POST":
        form = SkillForm(request.POST, request.FILES, instance=skill)
        if form.is_valid():
            form.save()
            messages.success(request, "スキルを更新しました。")
            return redirect("skill_detail", pk=skill.pk)
    else:
        form = SkillForm(instance=skill)
    return render(request, "core/skill_form.html", {
        "form": form,
        "action": "更新する",
        "skill": skill,
    })


@login_required
def skill_delete(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    if skill.user != request.user:
        raise PermissionDenied
    if request.method == "POST":
        skill.delete()
        messages.success(request, "スキルを削除しました。")
        return redirect("skill_list")
    return render(request, "core/skill_confirm_delete.html", {"skill": skill})


# ── 決済 ──────────────────────────────────────────────────────────────────────

@login_required
def checkout(request, skill_id):
    """Stripe Checkout セッションを作成して決済ページへリダイレクト"""
    if request.method != "POST":
        return redirect("skill_detail", pk=skill_id)

    skill = get_object_or_404(Skill, pk=skill_id, status="active")

    if skill.user == request.user:
        messages.error(request, "自分のスキルは購入できません。")
        return redirect("skill_detail", pk=skill_id)

    # Order を pending で先に保存
    order = Order.objects.create(
        buyer=request.user,
        skill=skill,
        price=skill.price,
        status="pending",
    )

    success_url = (
        request.build_absolute_uri(reverse("checkout_success"))
        + "?session_id={CHECKOUT_SESSION_ID}"
    )
    cancel_url = request.build_absolute_uri(reverse("skill_detail", kwargs={"pk": skill_id}))

    # JPY はゼロ小数点通貨のため unit_amount はそのまま円単位
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "jpy",
                "product_data": {"name": skill.title},
                "unit_amount": skill.price,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"order_id": order.pk},
    )

    return redirect(session.url, permanent=False)


@login_required
def checkout_success(request):
    """Stripe 決済完了後のコールバック処理"""
    session_id = request.GET.get("session_id", "")
    if not session_id:
        return redirect("index")

    session = stripe.checkout.Session.retrieve(session_id)

    if session.payment_status != "paid":
        messages.error(request, "決済が完了していません。")
        return redirect("index")

    order_id = session.metadata.get("order_id")
    order = get_object_or_404(Order, pk=order_id, buyer=request.user, status="pending")
    order.stripe_payment_id = session.payment_intent
    order.status = "in_progress"
    order.save()

    messages.success(request, "取引を開始しました！出品者からの連絡をお待ちください。")
    return render(request, "core/checkout_success.html", {"order": order})


@login_required
def order_list(request):
    """自分が購入した注文一覧"""
    orders = (
        Order.objects.filter(buyer=request.user)
        .select_related("skill", "skill__user")
        .order_by("-created_at")
    )
    return render(request, "core/order_list.html", {"orders": orders})


# ── 取引詳細・メッセージ ───────────────────────────────────────────────────────

@login_required
def order_detail(request, pk):
    """取引詳細＋メッセージ一覧・送信（購入者または出品者のみ）"""
    order = get_object_or_404(
        Order.objects.select_related("skill", "skill__user", "buyer"),
        pk=pk,
    )
    is_buyer = order.buyer == request.user
    is_seller = order.skill.user == request.user
    if not (is_buyer or is_seller):
        raise PermissionDenied

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.order = order
            msg.sender = request.user
            msg.save()
            return redirect("order_detail", pk=pk)  # PRG
    else:
        form = MessageForm()

    thread = order.messages.select_related("sender").order_by("sent_at")

    existing_review = None
    if order.status == "completed" and is_buyer:
        existing_review = Review.objects.filter(order=order).first()

    return render(request, "core/order_detail.html", {
        "order": order,
        "form": form,
        "thread": thread,
        "is_buyer": is_buyer,
        "is_seller": is_seller,
        "existing_review": existing_review,
    })


@login_required
def order_complete(request, pk):
    """出品者が取引を完了にする"""
    order = get_object_or_404(Order, pk=pk)
    if order.skill.user != request.user:
        raise PermissionDenied
    if request.method == "POST" and order.status == "in_progress":
        order.status = "completed"
        order.save()
        messages.success(request, "取引を完了しました。")
    return redirect("order_detail", pk=pk)


# ── レビュー ──────────────────────────────────────────────────────────────────

@login_required
def order_review(request, pk):
    """購入者がレビューを投稿（completed のみ・1回限り）"""
    order = get_object_or_404(Order, pk=pk, buyer=request.user, status="completed")

    existing_review = Review.objects.filter(order=order).first()
    if existing_review:
        return render(request, "core/review_form.html", {
            "order": order,
            "existing_review": existing_review,
        })

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.order = order
            review.reviewer = request.user
            review.save()
            messages.success(request, "レビューを投稿しました。")
            return redirect("order_detail", pk=pk)
    else:
        form = ReviewForm()

    return render(request, "core/review_form.html", {"form": form, "order": order})


# ── ユーザープロフィール ───────────────────────────────────────────────────────

def user_profile(request, pk):
    """出品者プロフィール：スキル一覧＋受け取ったレビュー"""
    profile_user = get_object_or_404(User, pk=pk)
    skills = Skill.objects.filter(user=profile_user, status="active").order_by("-created_at")
    reviews = (
        Review.objects.filter(order__skill__user=profile_user)
        .select_related("reviewer", "order__skill")
        .order_by("-created_at")
    )
    avg_rating = reviews.aggregate(avg=Avg("rating"))["avg"]

    return render(request, "core/user_profile.html", {
        "profile_user": profile_user,
        "skills": skills,
        "reviews": reviews,
        "avg_rating": avg_rating,
    })
