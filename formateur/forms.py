from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from formation.models import Formation
from inscription.models import Inscription
from certification.models import Certification
from formateur.models import Formateur


class FormationForm(forms.ModelForm):
    class Meta:
        model = Formation
        fields = [
            'titre',
            'domaine',
            'niveau',
            'duree',
            'dateDebut',
            'dateFin',
            'nombrePlaces',
            'lieu',
            'description',
            'objectifs',
            'prerequis',
        ]
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Architectures Microservices avec Django & Docker',
                'autofocus': True,
            }),
            'domaine': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Développement Web Back-end, Cloud & DevOps, IA...',
            }),
            'niveau': forms.Select(
                choices=[
                    ('Débutant', 'Débutant'),
                    ('Intermédiaire', 'Intermédiaire'),
                    ('Avancé', 'Avancé'),
                    ('Tous niveaux', 'Tous niveaux'),
                ],
                attrs={'class': 'form-control'}
            ),
            'duree': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 35',
                'min': '1',
            }),
            'dateDebut': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'dateFin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'nombrePlaces': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: 15',
                'min': '1',
            }),
            'lieu': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: En ligne (Visio), Paris 15e, Lyon...',
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Présentation globale de la formation, contexte et méthodologie...',
            }),
            'objectifs': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Objectifs pédagogiques et compétences visées...',
            }),
            'prerequis': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Connaissances préalables recommandées...',
            }),
        }
        labels = {
            'titre': 'Titre de la formation',
            'domaine': 'Domaine d\'expertise',
            'niveau': 'Niveau requis',
            'duree': 'Durée estimée (en heures)',
            'dateDebut': 'Date de début',
            'dateFin': 'Date de fin',
            'nombrePlaces': 'Capacité maximale (places)',
            'lieu': 'Mode / Lieu',
            'description': 'Description détaillée',
            'objectifs': 'Objectifs pédagogiques',
            'prerequis': 'Prérequis',
        }

    def clean_nombrePlaces(self):
        places = self.cleaned_data.get('nombrePlaces')
        if places is not None and places <= 0:
            raise ValidationError("La capacité maximale doit être strictement supérieure à 0.")
        return places

    def clean_duree(self):
        duree = self.cleaned_data.get('duree')
        if duree is not None and duree <= 0:
            raise ValidationError("La durée de la formation doit être strictement positive.")
        return duree

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('dateDebut')
        date_fin = cleaned_data.get('dateFin')

        if date_debut and date_fin:
            if date_fin < date_debut:
                self.add_error(
                    'dateFin',
                    "La date de fin ne peut pas précéder la date de début de la formation."
                )
        return cleaned_data


class CertificationIssueForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['inscription', 'titre', 'dateObtention', 'fichier']
        widgets = {
            'inscription': forms.Select(attrs={'class': 'form-control'}),
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Certificat de réussite - Nom de la formation',
            }),
            'dateObtention': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'fichier': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'inscription': 'Participant & Formation éligible',
            'titre': 'Intitulé de la certification',
            'dateObtention': 'Date de délivrance',
            'fichier': 'Document joint / Justificatif (optionnel)',
        }

    def __init__(self, *args, formateur=None, **kwargs):
        super().__init__(*args, **kwargs)
        if formateur:
            # Filtrer les inscriptions : uniquement les formations du formateur
            # et pour lesquelles aucune certification n'a encore été délivrée
            qs = Inscription.objects.filter(
                formation__formateur=formateur,
                certification__isnull=True
            ).select_related('candidat', 'formation')
            self.fields['inscription'].queryset = qs
            self.fields['inscription'].empty_label = "-- Sélectionnez un participant --"
            self.fields['inscription'].label_from_instance = (
                lambda obj: f"{obj.candidat.prenom} {obj.candidat.nom} — {obj.formation.titre} (Statut: {obj.statut})"
            )
            self.fields['dateObtention'].initial = timezone.now().date()

    def clean_inscription(self):
        inscription = self.cleaned_data.get('inscription')
        if inscription and Certification.objects.filter(inscription=inscription).exists():
            raise ValidationError("Ce participant possède déjà une certification pour cette formation.")
        return inscription


class ParticipantStatusForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = ['statut']
        widgets = {
            'statut': forms.Select(
                choices=[
                    ('EN ATTENTE', 'En attente'),
                    ('CONFIRMEE', 'Confirmée'),
                    ('TERMINEE', 'Terminée'),
                    ('ANNULEE', 'Annulée'),
                ],
                attrs={'class': 'form-control'}
            )
        }
        labels = {
            'statut': 'Statut d\'inscription'
        }


class FormateurProfileExtendedForm(forms.ModelForm):
    email = forms.EmailField(
        label="Adresse email professionnelle",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Formateur
        fields = ['email', 'prenom', 'nom', 'specialite', 'telephone', 'experience', 'bio']
        widgets = {
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'specialite': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 06 12 34 56 78'}),
            'experience': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 8 ans d\'expérience'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'prenom': 'Prénom',
            'nom': 'Nom',
            'specialite': 'Domaine d\'expertise / Titre',
            'telephone': 'Numéro de téléphone',
            'experience': 'Années d\'expérience',
            'bio': 'Biographie et parcours professionnel',
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.first_name = instance.prenom
        instance.last_name = instance.nom
        if commit:
            instance.save()
        return instance
