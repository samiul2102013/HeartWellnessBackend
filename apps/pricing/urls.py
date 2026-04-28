from django.urls import path
from . import views

urlpatterns = [
    # ── User / Mobile ─────────────────────────────────────────
    path('pricing/plans/', views.PlanListView.as_view()),
    path('pricing/subscribe/', views.SubscribeView.as_view()),
    path('pricing/my-subscription/', views.MySubscriptionView.as_view()),
    path('pricing/cancel/', views.CancelSubscriptionView.as_view()),
    path('pricing/history/', views.MySubscriptionHistoryView.as_view()),

    # ── Admin ─────────────────────────────────────────────────
    path('admin/pricing/plans/', views.AdminPlanListCreateView.as_view()),
    path('admin/pricing/plans/<int:pk>/', views.AdminPlanDetailView.as_view()),
    path('admin/pricing/features/', views.AdminPlanFeatureListCreateView.as_view()),
    path('admin/pricing/features/<int:pk>/', views.AdminPlanFeatureDetailView.as_view()),
    path('admin/pricing/subscriptions/', views.AdminSubscriptionListView.as_view()),
    path('admin/pricing/subscriptions/<int:pk>/', views.AdminSubscriptionDetailView.as_view()),
    path('admin/pricing/stats/', views.AdminPricingStatsView.as_view()),
]