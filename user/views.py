from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme

from .models import User, Role
from .forms import (
    LoginForm,
    CandidatRegisterForm,
    EntrepriseRegisterForm,
    FormateurRegisterForm,
    CandidatProfileForm,
    EntrepriseProfileForm,
    FormateurProfileForm,
    AdminProfileForm,
)

# Import des modèles métier pour les métriques du dashboard
from offre.models import Offre
from formation.models import Formation
from candidat.models import Candidat
from entreprise.models import Entreprise
from formateur.models import Formateur
from candidature.models import Candidature
from inscription.models import Inscription
from certification.models import Certification


def home_view(request):
    """Page d'accueil principale de la plateforme HirePoint."""
    total_offres = Offre.objects.count()
    total_formations = Formation.objects.count()
    total_candidats = Candidat.objects.count()
    total_entreprises = Entreprise.objects.count()

    recent_offres = Offre.objects.select_related('entreprise').order_by('-datePublication')[:3]
    recent_formations = Formation.objects.select_related('formateur').order_by('dateDebut')[:3]

    context = {
        'total_offres': total_offres,
        'total_formations': total_formations,
        'total_candidats': total_candidats,
        'total_entreprises': total_entreprises,
        'recent_offres': recent_offres,
        'recent_formations': recent_formations,
    }
    return render(request, 'home.html', context)


def login_view(request):
    """Vue de connexion avec support nom d'utilisateur OU email."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    next_url = request.GET.get('next', '')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            ident = form.cleaned_data['username_or_email']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me', True)

            user = authenticate(request, username=ident, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    if not remember_me:
                        # Expire à la fermeture du navigateur
                        request.session.set_expiry(0)
                    else:
                        # 2 semaines par défaut
                        request.session.set_expiry(1209600)

                    messages.success(request, f"Ravi de vous revoir, {user.display_name} !")

                    # Redirection sécurisée
                    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
                        return redirect(next_url)
                    return redirect('dashboard')
                else:
                    messages.error(request, "Ce compte est désactivé. Veuillez contacter un administrateur.")
            else:
                messages.error(request, "Identifiant ou mot de passe incorrect. Veuillez réessayer.")
    else:
        form = LoginForm()

    return render(request, 'user/login.html', {
        'form': form,
        'next': next_url,
    })


def register_view(request):
    """Vue d'inscription multi-rôles (Candidat, Entreprise, Formateur)."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    active_tab = request.GET.get('role', 'candidat').lower()
    if active_tab not in ['candidat', 'entreprise', 'formateur']:
        active_tab = 'candidat'

    candidat_form = CandidatRegisterForm(prefix='candidat')
    entreprise_form = EntrepriseRegisterForm(prefix='entreprise')
    formateur_form = FormateurRegisterForm(prefix='formateur')

    if request.method == 'POST':
        target_role = request.POST.get('target_role', 'candidat')
        active_tab = target_role

        if target_role == 'candidat':
            candidat_form = CandidatRegisterForm(request.POST, prefix='candidat')
            if candidat_form.is_valid():
                user = candidat_form.save()
                login(request, user, backend='user.backends.EmailOrUsernameModelBackend')
                messages.success(request, f"Bienvenue {user.display_name} ! Votre compte Candidat est prêt.")
                return redirect('dashboard')
            else:
                messages.error(request, "Veuillez corriger les erreurs indiquées dans le formulaire.")

        elif target_role == 'entreprise':
            entreprise_form = EntrepriseRegisterForm(request.POST, prefix='entreprise')
            if entreprise_form.is_valid():
                user = entreprise_form.save()
                login(request, user, backend='user.backends.EmailOrUsernameModelBackend')
                messages.success(request, f"Bienvenue {user.display_name} ! Votre compte Entreprise est actif.")
                return redirect('dashboard')
            else:
                messages.error(request, "Veuillez corriger les erreurs indiquées dans le formulaire.")

        elif target_role == 'formateur':
            formateur_form = FormateurRegisterForm(request.POST, prefix='formateur')
            if formateur_form.is_valid():
                user = formateur_form.save()
                login(request, user, backend='user.backends.EmailOrUsernameModelBackend')
                messages.success(request, f"Bienvenue {user.display_name} ! Votre compte Formateur est créé.")
                return redirect('dashboard')
            else:
                messages.error(request, "Veuillez corriger les erreurs indiquées dans le formulaire.")

    context = {
        'active_tab': active_tab,
        'candidat_form': candidat_form,
        'entreprise_form': entreprise_form,
        'formateur_form': formateur_form,
    }
    return render(request, 'user/register.html', context)


def logout_view(request):
    """Déconnexion de l'utilisateur."""
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, "Vous avez été déconnecté avec succès. À très bientôt sur HirePoint !")
    return redirect('home')


@login_required
def dashboard_view(request):
    """Tableau de bord personnalisé selon le rôle de l'utilisateur connecté."""
    user = request.user
    context = {'user': user}

    if user.is_candidat:
        candidat_obj = getattr(user, 'candidat', None)
        if candidat_obj:
            candidatures = Candidature.objects.filter(
                candidat=candidat_obj
            ).select_related('offre__entreprise').order_by('-dateCandidature')[:5]
            
            inscriptions = Inscription.objects.filter(
                candidat=candidat_obj
            ).select_related('formation').order_by('-dateInscription')[:5]

            context.update({
                'candidat_obj': candidat_obj,
                'candidatures': candidatures,
                'candidatures_count': Candidature.objects.filter(candidat=candidat_obj).count(),
                'inscriptions': inscriptions,
                'inscriptions_count': Inscription.objects.filter(candidat=candidat_obj).count(),
                'certifications_count': Certification.objects.filter(inscription__candidat=candidat_obj).count(),
                'offres_recentes': Offre.objects.select_related('entreprise').order_by('-datePublication')[:4],
            })

    elif user.is_entreprise:
        entreprise_obj = getattr(user, 'entreprise', None)
        if entreprise_obj:
            mes_offres = Offre.objects.filter(entreprise=entreprise_obj).order_by('-datePublication')
            candidatures_recues = Candidature.objects.filter(
                offre__entreprise=entreprise_obj
            ).select_related('candidat', 'offre').order_by('-dateCandidature')[:6]

            context.update({
                'entreprise_obj': entreprise_obj,
                'mes_offres': mes_offres[:5],
                'mes_offres_count': mes_offres.count(),
                'candidatures_recues': candidatures_recues,
                'candidatures_count': Candidature.objects.filter(offre__entreprise=entreprise_obj).count(),
            })

    elif user.is_formateur:
        from formateur.views import dashboard_view as formateur_dashboard
        return formateur_dashboard(request)

    else:
        # Administrateur ou staff
        context.update({
            'total_users': User.objects.count(),
            'total_candidats': Candidat.objects.count(),
            'total_entreprises': Entreprise.objects.count(),
            'total_formateurs': Formateur.objects.count(),
            'total_offres': Offre.objects.count(),
            'total_formations': Formation.objects.count(),
            'total_candidatures': Candidature.objects.count(),
        })

    return render(request, 'user/dashboard.html', context)


@login_required
def profile_view(request):
    """Page de consultation du profil."""
    user = request.user
    profile_obj = user.profile_object

    context = {
        'user': user,
        'profile_obj': profile_obj,
    }
    return render(request, 'user/profile.html', context)


@login_required
def profile_edit_view(request):
    """Modification des informations du profil."""
    user = request.user
    profile_obj = user.profile_object

    if user.is_candidat and hasattr(user, 'candidat'):
        FormClass = CandidatProfileForm
        instance = user.candidat
    elif user.is_entreprise and hasattr(user, 'entreprise'):
        FormClass = EntrepriseProfileForm
        instance = user.entreprise
    elif user.is_formateur and hasattr(user, 'formateur'):
        FormClass = FormateurProfileForm
        instance = user.formateur
    else:
        FormClass = AdminProfileForm
        instance = user

    if request.method == 'POST':
        form = FormClass(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès !")
            return redirect('profile')
        else:
            messages.error(request, "Veuillez vérifier les informations renseignées.")
    else:
        form = FormClass(instance=instance)

    return render(request, 'user/profile_edit.html', {
        'form': form,
        'user': user,
        'profile_obj': profile_obj,
    })


@login_required
def password_change_view(request):
    """Changement de mot de passe sécurisé."""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Maintient l'utilisateur connecté après le changement de mot de passe
            update_session_auth_hash(request, user)
            messages.success(request, "Votre mot de passe a été modifié avec succès !")
            return redirect('profile')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'user/password_change.html', {'form': form})
