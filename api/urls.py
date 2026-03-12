from django.urls import path
from .views import (
    # Authentification
    LoginView,
    LogoutView,
    GetProfileView,

    # Inscription
    EmployeRegisterView,
    AdministrateurRegisterView,

    # Gestion employés
    EmployeListView,
    EmployeDetailView,

    # Gestion profil utilisateur
    UpdateUserProfileView,
    UpdateProfilePhotoView,
    DeleteProfilePhotoView,
    ChangePasswordView,

    # Réinitialisation mot de passe
    RequestPasswordResetView,
    VerifyResetCodeView,
    ResetPasswordView,
)

urlpatterns = [
    # ── Authentification ──────────────────────────────────────────
    path('auth/login/',                     LoginView.as_view(),                    name='login'),
    path('auth/logout/',                    LogoutView.as_view(),                   name='logout'),
    path('auth/me/',                        GetProfileView.as_view(),               name='me'),

    # ── Inscription ───────────────────────────────────────────────
    path('auth/register/employe/',          EmployeRegisterView.as_view(),          name='register-employe'),
    path('auth/register/admin/',            AdministrateurRegisterView.as_view(),   name='register-admin'),

    # ── Gestion des employés (Admin seulement) ────────────────────
    path('admin/employes/',                 EmployeListView.as_view(),              name='employes-list'),
    path('admin/employes/<int:pk>/',        EmployeDetailView.as_view(),            name='employes-detail'),

    # ── Profil employé (soi-même) ─────────────────────────────────
    path('employe/me/',                     EmployeDetailView.as_view(),            name='employe-me'),

    # ── Gestion du profil utilisateur ────────────────────────────
    path('profile/update/',                 UpdateUserProfileView.as_view(),        name='profile-update'),
    path('profile/photo/',                  UpdateProfilePhotoView.as_view(),       name='profile-photo-update'),
    path('profile/photo/delete/',           DeleteProfilePhotoView.as_view(),       name='profile-photo-delete'),
    path('profile/change-password/',        ChangePasswordView.as_view(),           name='change-password'),

    # ── Réinitialisation mot de passe (3 étapes) ─────────────────
    path('auth/password-reset/request/',    RequestPasswordResetView.as_view(),     name='password-reset-request'),
    path('auth/password-reset/verify/',     VerifyResetCodeView.as_view(),          name='password-reset-verify'),
    path('auth/password-reset/confirm/',    ResetPasswordView.as_view(),            name='password-reset-confirm'),
]