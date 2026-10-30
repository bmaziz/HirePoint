from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone

from formation.models import Formation
from inscription.models import Inscription
from certification.models import Certification
from notification.models import Notification
from formateur.models import Formateur

from .forms import (
    FormationForm,
    CertificationIssueForm,
    ParticipantStatusForm,
    FormateurProfileExtendedForm,
)


def formateur_required(view_func):
    """Décorateur de sécurité restreignant l'accès aux formateurs connectés."""
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not getattr(request.user, 'is_formateur', False) or not hasattr(request.user, 'formateur'):
            messages.error(request, "Accès refusé. Cette section est strictement réservée aux formateurs.")
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


# ==========================================
# 1. TABLEAU DE BORD FORMATEUR
# ==========================================

@formateur_required
def dashboard_view(request):
    """Tableau de bord principal du formateur avec métriques réelles et flux d'activité."""
    formateur = request.user.formateur

    # Formations
    formations_qs = Formation.objects.filter(formateur=formateur)
    total_formations = formations_qs.count()

    # Inscriptions / Participants
    inscriptions_qs = Inscription.objects.filter(formation__formateur=formateur)
    total_participants = inscriptions_qs.count()
    inscriptions_en_attente = inscriptions_qs.filter(statut='EN ATTENTE').count()
    inscriptions_confirmees = inscriptions_qs.filter(statut='CONFIRMEE').count()
    inscriptions_terminees = inscriptions_qs.filter(statut='TERMINEE').count()

    # Certifications
    certifications_qs = Certification.objects.filter(inscription__formation__formateur=formateur)
    total_certifications = certifications_qs.count()

    # Récentes
    recent_formations = formations_qs.order_by('-dateDebut')[:4]
    recent_inscriptions = inscriptions_qs.select_related('candidat', 'formation').order_by('-dateInscription')[:6]
    recent_certifications = certifications_qs.select_related('inscription__candidat', 'inscription__formation').order_by('-dateObtention')[:4]

    # Notifications du formateur
    recent_notifications = Notification.objects.filter(user=request.user).order_by('-dateCreation')[:5]
    unread_notifications_count = Notification.objects.filter(user=request.user, lue=False).count()

    context = {
        'formateur': formateur,
        'total_formations': total_formations,
        'total_participants': total_participants,
        'total_certifications': total_certifications,
        'inscriptions_en_attente': inscriptions_en_attente,
        'inscriptions_confirmees': inscriptions_confirmees,
        'inscriptions_terminees': inscriptions_terminees,
        'recent_formations': recent_formations,
        'recent_inscriptions': recent_inscriptions,
        'recent_certifications': recent_certifications,
        'recent_notifications': recent_notifications,
        'unread_notifications_count': unread_notifications_count,
        'active_menu': 'dashboard',
    }
    return render(request, 'formateur/dashboard.html', context)


# ==========================================
# 2. GESTION DES FORMATIONS (CRUD)
# ==========================================

@formateur_required
def formation_list_view(request):
    """Liste de toutes les formations créées par le formateur connecté."""
    formateur = request.user.formateur
    formations = Formation.objects.filter(formateur=formateur).annotate(
        inscrits_count=Count('inscriptions')
    )

    # Recherche
    q = request.GET.get('q', '').strip()
    if q:
        formations = formations.filter(
            Q(titre__icontains=q) |
            Q(domaine__icontains=q) |
            Q(niveau__icontains=q) |
            Q(description__icontains=q)
        )

    # Filtre de statut temporel
    today = timezone.now().date()
    period = request.GET.get('periode', 'all')
    if period == 'a_venir':
        formations = formations.filter(dateDebut__gt=today)
    elif period == 'en_cours':
        formations = formations.filter(dateDebut__lte=today, dateFin__gte=today)
    elif period == 'terminee':
        formations = formations.filter(dateFin__lt=today)

    context = {
        'formations': formations,
        'q': q,
        'periode': period,
        'today': today,
        'active_menu': 'formations',
    }
    return render(request, 'formateur/formation_list.html', context)


@formateur_required
def formation_detail_view(request, pk):
    """Détails complets d'une formation avec liste de ses participants et certifications."""
    formateur = request.user.formateur
    formation = get_object_or_404(Formation, pk=pk)

    # Contrôle de sécurité au niveau de l'objet
    if formation.formateur != formateur:
        messages.error(request, "Vous n'êtes pas autorisé à consulter cette formation.")
        raise PermissionDenied("Vous n'êtes pas le propriétaire de cette formation.")

    inscriptions = formation.inscriptions.select_related('candidat', 'certification').order_by('-dateInscription')
    certifications = Certification.objects.filter(inscription__formation=formation).select_related('inscription__candidat')

    context = {
        'formation': formation,
        'inscriptions': inscriptions,
        'certifications': certifications,
        'today': timezone.now().date(),
        'active_menu': 'formations',
    }
    return render(request, 'formateur/formation_detail.html', context)


@formateur_required
def formation_create_view(request):
    """Création d'une nouvelle formation avec validation et assignation au formateur."""
    formateur = request.user.formateur

    if request.method == 'POST':
        form = FormationForm(request.POST)
        if form.is_valid():
            formation = form.save(commit=False)
            formation.formateur = formateur
            formation.save()

            # Notification système pour le formateur
            Notification.objects.create(
                user=request.user,
                type='FORMATION',
                message=f"Votre session de formation '{formation.titre}' a été créée avec succès."
            )

            messages.success(request, f"La session « {formation.titre} » a été publiée avec succès !")
            return redirect('formateur:formation_detail', pk=formation.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = FormationForm()

    context = {
        'form': form,
        'is_edit': False,
        'active_menu': 'formations_create',
    }
    return render(request, 'formateur/formation_form.html', context)


@formateur_required
def formation_update_view(request, pk):
    """Modification d'une formation existante avec vérification stricte de propriété."""
    formateur = request.user.formateur
    formation = get_object_or_404(Formation, pk=pk)

    # Contrôle de sécurité
    if formation.formateur != formateur:
        messages.error(request, "Vous n'avez pas le droit de modifier une formation qui ne vous appartient pas.")
        raise PermissionDenied("Vous n'êtes pas le formateur responsable.")

    if request.method == 'POST':
        form = FormationForm(request.POST, instance=formation)
        if form.is_valid():
            form.save()
            messages.success(request, f"La formation « {formation.titre} » a été mise à jour.")
            return redirect('formateur:formation_detail', pk=formation.pk)
        else:
            messages.error(request, "Veuillez corriger les erreurs indiquées.")
    else:
        form = FormationForm(instance=formation)

    context = {
        'form': form,
        'formation': formation,
        'is_edit': True,
        'active_menu': 'formations',
    }
    return render(request, 'formateur/formation_form.html', context)


@formateur_required
def formation_delete_view(request, pk):
    """Suppression d'une formation après confirmation explicite."""
    formateur = request.user.formateur
    formation = get_object_or_404(Formation, pk=pk)

    # Contrôle de sécurité
    if formation.formateur != formateur:
        messages.error(request, "Action non autorisée sur cette formation.")
        raise PermissionDenied("Tentative de suppression d'une formation tierce.")

    if request.method == 'POST':
        titre = formation.titre
        nb_inscriptions = formation.inscriptions.count()
        formation.delete()

        Notification.objects.create(
            user=request.user,
            type='FORMATION',
            message=f"La formation '{titre}' a été supprimée définitivement."
        )

        messages.success(
            request,
            f"La formation « {titre} » ({nb_inscriptions} inscription(s) associée(s)) a été supprimée."
        )
        return redirect('formateur:formation_list')

    context = {
        'formation': formation,
        'inscriptions_count': formation.inscriptions.count(),
        'active_menu': 'formations',
    }
    return render(request, 'formateur/formation_confirm_delete.html', context)


# ==========================================
# 3. GESTION DES PARTICIPANTS (APPRENANTS)
# ==========================================

@formateur_required
def participant_list_view(request):
    """Visualisation et filtrage des candidats inscrits aux formations du formateur."""
    formateur = request.user.formateur

    inscriptions = Inscription.objects.filter(
        formation__formateur=formateur
    ).select_related('candidat', 'formation', 'certification').order_by('-dateInscription')

    # Filtrage par formation
    formation_id = request.GET.get('formation', '').strip()
    if formation_id.isdigit():
        inscriptions = inscriptions.filter(formation_id=int(formation_id))

    # Filtrage par statut
    statut = request.GET.get('statut', '').strip()
    if statut:
        inscriptions = inscriptions.filter(statut=statut)

    # Recherche
    q = request.GET.get('q', '').strip()
    if q:
        inscriptions = inscriptions.filter(
            Q(candidat__nom__icontains=q) |
            Q(candidat__prenom__icontains=q) |
            Q(candidat__email__icontains=q) |
            Q(formation__titre__icontains=q)
        )

    mes_formations = Formation.objects.filter(formateur=formateur).order_by('titre')

    context = {
        'inscriptions': inscriptions,
        'mes_formations': mes_formations,
        'selected_formation': formation_id,
        'selected_statut': statut,
        'q': q,
        'active_menu': 'participants',
    }
    return render(request, 'formateur/participant_list.html', context)


@formateur_required
def participant_status_update_view(request, pk):
    """Mise à jour du statut d'une inscription (ex: confirmation, validation de présence)."""
    formateur = request.user.formateur
    inscription = get_object_or_404(Inscription, pk=pk)

    # Contrôle de sécurité
    if inscription.formation.formateur != formateur:
        messages.error(request, "Vous n'avez pas accès à ce participant.")
        raise PermissionDenied("L'inscription n'appartient pas à l'une de vos formations.")

    if request.method == 'POST':
        form = ParticipantStatusForm(request.POST, instance=inscription)
        if form.is_valid():
            nouveau_statut = form.cleaned_data['statut']
            form.save()

            # Notifier le candidat
            Notification.objects.create(
                user=inscription.candidat,
                type='FORMATION',
                message=(
                    f"Votre inscription à la formation « {inscription.formation.titre} » "
                    f"est passée au statut : {nouveau_statut}."
                )
            )

            messages.success(
                request,
                f"Statut d'inscription de {inscription.candidat.prenom} {inscription.candidat.nom} "
                f"mis à jour : {nouveau_statut}."
            )
        else:
            messages.error(request, "Statut invalide.")

    next_url = request.POST.get('next') or request.GET.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('formateur:participant_list')


# ==========================================
# 4. GESTION DES CERTIFICATIONS
# ==========================================

@formateur_required
def certification_list_view(request):
    """Liste de toutes les certifications délivrées par le formateur."""
    formateur = request.user.formateur

    certifications = Certification.objects.filter(
        inscription__formation__formateur=formateur
    ).select_related('inscription__candidat', 'inscription__formation').order_by('-dateObtention')

    # Recherche
    q = request.GET.get('q', '').strip()
    if q:
        certifications = certifications.filter(
            Q(reference__icontains=q) |
            Q(titre__icontains=q) |
            Q(inscription__candidat__nom__icontains=q) |
            Q(inscription__candidat__prenom__icontains=q) |
            Q(inscription__formation__titre__icontains=q)
        )

    context = {
        'certifications': certifications,
        'q': q,
        'active_menu': 'certifications',
    }
    return render(request, 'formateur/certification_list.html', context)


@formateur_required
def certification_issue_view(request):
    """Délivrance d'une nouvelle certification à un participant éligible."""
    formateur = request.user.formateur

    # Pré-sélection optionnelle d'inscription via paramètre GET
    preselected_id = request.GET.get('inscription', '')
    initial_data = {}
    if preselected_id.isdigit():
        try:
            target_insc = Inscription.objects.get(
                pk=int(preselected_id),
                formation__formateur=formateur,
                certification__isnull=True
            )
            initial_data['inscription'] = target_insc
            initial_data['titre'] = f"Certificat de réussite - {target_insc.formation.titre}"
            initial_data['dateObtention'] = target_insc.formation.dateFin or timezone.now().date()
        except Inscription.DoesNotExist:
            pass

    if request.method == 'POST':
        form = CertificationIssueForm(request.POST, request.FILES, formateur=formateur)
        if form.is_valid():
            inscription = form.cleaned_data['inscription']

            # Double vérification d'appartenance et d'unicité
            if inscription.formation.formateur != formateur:
                raise PermissionDenied("Vous ne pouvez pas délivrer de certificat pour une autre formation.")

            if Certification.objects.filter(inscription=inscription).exists():
                messages.error(request, "Une certification a déjà été émise pour cette inscription.")
                return redirect('formateur:certification_list')

            certification = form.save(commit=False)
            certification.save()  # Auto-génère la référence unique

            # Génération automatique du fichier justificatif textuel si aucun fichier uploadé
            if not certification.fichier:
                candidat = inscription.candidat
                formation = inscription.formation
                content = (
                    f"==========================================================\n"
                    f"               ATTESTATION DE CERTIFICATION HIREPOINT     \n"
                    f"==========================================================\n\n"
                    f"Référence Unique : {certification.reference}\n"
                    f"Date d'émission   : {certification.dateObtention}\n\n"
                    f"Délivré à        : {candidat.prenom} {candidat.nom}\n"
                    f"Email Apprenant  : {candidat.email}\n\n"
                    f"Formation validée: {formation.titre}\n"
                    f"Domaine          : {formation.domaine}\n"
                    f"Niveau           : {formation.niveau}\n"
                    f"Volume horaire   : {formation.duree} heures\n\n"
                    f"Formateur agréé  : {formateur.prenom} {formateur.nom}\n"
                    f"Spécialité       : {formateur.specialite}\n\n"
                    f"Cette attestation confirme que l'apprenant a suivi et validé avec succès\n"
                    f"l'ensemble des modules pratiques et évaluations du programme.\n"
                    f"==========================================================\n"
                ).encode('utf-8')
                filename = f"certif_{candidat.username}_{inscription.id}_{certification.reference}.txt"
                certification.fichier.save(filename, ContentFile(content), save=True)

            # Passer le statut de l'inscription à TERMINEE si ce n'est pas déjà le cas
            if inscription.statut != 'TERMINEE':
                inscription.statut = 'TERMINEE'
                inscription.save()

            # Notifications
            Notification.objects.create(
                user=inscription.candidat,
                type='CERTIFICATION',
                message=(
                    f"Félicitations ! Vous avez obtenu votre certification pour « {inscription.formation.titre} ». "
                    f"Référence : {certification.reference}"
                )
            )
            Notification.objects.create(
                user=request.user,
                type='CERTIFICATION',
                message=(
                    f"Certification délivrée avec succès à {inscription.candidat.prenom} {inscription.candidat.nom} "
                    f"(Réf: {certification.reference})."
                )
            )

            messages.success(
                request,
                f"Certification « {certification.reference} » délivrée avec succès à "
                f"{inscription.candidat.prenom} {inscription.candidat.nom} !"
            )
            return redirect('formateur:certification_detail', pk=certification.pk)
        else:
            messages.error(request, "Veuillez vérifier les informations de certification renseignées.")
    else:
        form = CertificationIssueForm(formateur=formateur, initial=initial_data)

    context = {
        'form': form,
        'active_menu': 'certifications_issue',
    }
    return render(request, 'formateur/certification_issue.html', context)


@formateur_required
def certification_detail_view(request, pk):
    """Consultation et impression d'un certificat délivré."""
    formateur = request.user.formateur
    certification = get_object_or_404(Certification, pk=pk)

    # Contrôle de sécurité
    if certification.inscription.formation.formateur != formateur:
        messages.error(request, "Accès interdit à ce certificat.")
        raise PermissionDenied("Vous n'êtes pas l'instructeur ayant émis cette certification.")

    context = {
        'certification': certification,
        'candidat': certification.inscription.candidat,
        'formation': certification.inscription.formation,
        'formateur': formateur,
        'active_menu': 'certifications',
    }
    return render(request, 'formateur/certification_detail.html', context)


# ==========================================
# 5. SYSTÈME DE NOTIFICATIONS
# ==========================================

@formateur_required
def notification_list_view(request):
    """Centre de notifications du formateur connecté."""
    notifications = Notification.objects.filter(user=request.user).order_by('-dateCreation')
    unread_count = notifications.filter(lue=False).count()

    context = {
        'notifications': notifications,
        'unread_count': unread_count,
        'active_menu': 'notifications',
    }
    return render(request, 'formateur/notification_list.html', context)


@formateur_required
def notification_mark_read_view(request, pk):
    """Marque une notification spécifique comme lue."""
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.lue = True
    notif.save()
    messages.success(request, "Notification marquée comme lue.")
    return redirect('formateur:notification_list')


@formateur_required
def notification_mark_all_read_view(request):
    """Marque toutes les notifications non lues du formateur comme lues."""
    updated = Notification.objects.filter(user=request.user, lue=False).update(lue=True)
    messages.success(request, f"{updated} notification(s) marquée(s) comme lue(s).")
    return redirect('formateur:notification_list')


# ==========================================
# 6. GESTION DU PROFIL DU FORMATEUR
# ==========================================

@formateur_required
def profile_view(request):
    """Visualisation du profil formateur et récapitulatif de son activité."""
    formateur = request.user.formateur

    formations_count = Formation.objects.filter(formateur=formateur).count()
    participants_count = Inscription.objects.filter(formation__formateur=formateur).count()
    certifications_count = Certification.objects.filter(inscription__formation__formateur=formateur).count()

    context = {
        'formateur': formateur,
        'formations_count': formations_count,
        'participants_count': participants_count,
        'certifications_count': certifications_count,
        'active_menu': 'profile',
    }
    return render(request, 'formateur/profile.html', context)


@formateur_required
def profile_edit_view(request):
    """Modification du profil et des informations professionnelles du formateur."""
    formateur = request.user.formateur

    if request.method == 'POST':
        form = FormateurProfileExtendedForm(request.POST, instance=formateur)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil de formateur a été mis à jour avec succès !")
            return redirect('formateur:profile')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = FormateurProfileExtendedForm(instance=formateur, initial={'email': formateur.email})

    context = {
        'form': form,
        'formateur': formateur,
        'active_menu': 'profile_edit',
    }
    return render(request, 'formateur/profile_edit.html', context)
