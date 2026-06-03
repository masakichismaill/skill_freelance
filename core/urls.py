from django.urls import path

from . import views

urlpatterns = [
    # 認証
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("mypage/", views.mypage, name="mypage"),
    path("mypage/orders/", views.order_list, name="order_list"),
    # スキル
    path("skills/", views.skill_list, name="skill_list"),
    path("skills/new/", views.skill_new, name="skill_new"),
    path("skills/<int:pk>/", views.skill_detail, name="skill_detail"),
    path("skills/<int:pk>/edit/", views.skill_edit, name="skill_edit"),
    path("skills/<int:pk>/delete/", views.skill_delete, name="skill_delete"),
    # 決済
    path("orders/checkout/<int:skill_id>/", views.checkout, name="checkout"),
    path("orders/success/", views.checkout_success, name="checkout_success"),
    # 取引・メッセージ・レビュー
    path("orders/<int:pk>/", views.order_detail, name="order_detail"),
    path("orders/<int:pk>/complete/", views.order_complete, name="order_complete"),
    path("orders/<int:pk>/review/", views.order_review, name="order_review"),
    # ユーザープロフィール
    path("users/<int:pk>/", views.user_profile, name="user_profile"),
]
