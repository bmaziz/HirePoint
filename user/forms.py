from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, Role
from candidat.models import Candidat
from entreprise.models import Entreprise
from formateur.models import Formateur


class LoginForm(forms.Form):
    username_or_email = forms.CharField(
        label="Identifiant",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom d\'utilisateur ou adresse email',
            'id': 'login-identifier',
            'autocomplete': 'username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre mot de passe',
            'id': 'login-password',
            'autocomplete': 'current-password',
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=True,
        label="Se souvenir de moi",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'remember-me-checkbox',
        })
    )


class BaseRegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: jdupont'})
    )
    email = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ex: contact@exemple.fr'})
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Au moins 8 caractères'})
    )
    password_confirm = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Retapez votre mot de passe'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Ce nom d'utilisateur est déjà utilisé.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Cette adresse email est déjà associée à un compte.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')

        if p1 and p2:
            if p1 != p2:
                self.add_error('password_confirm', "Les mots de passe ne correspondent pas.")
            else:
                try:
                    validate_password(p1)
                except ValidationError as error:
                    self.add_error('password', error)
        return cleaned_data


class CandidatRegisterForm(BaseRegistrationForm):
    prenom = forms.CharField(
        max_length=100,
        label="Prénom",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Julien'})
    )
    nom = forms.CharField(
        max_length=100,
        label="Nom",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Martin'})
    )
    telephone = forms.CharField(
        max_length=20,
        label="Téléphone",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 06 12 34 56 78'})
    )
    adresse = forms.CharField(
        max_length=255,
        label="Adresse / Ville",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Paris, France'})
    )
    bio = forms.CharField(
        required=False,
        label="Brève présentation / Bio",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Parlez-nous brièvement de votre parcours et de vos objectifs...'
        })
    )

    def save(self):
        data = self.cleaned_data
        candidat = Candidat.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data['prenom'],
            last_name=data['nom'],
            role=Role.CANDIDAT,
            nom=data['nom'],
            prenom=data['prenom'],
            telephone=data['telephone'],
            adresse=data['adresse'],
            bio=data.get('bio', '')
        )
        return candidat


class EntrepriseRegisterForm(BaseRegistrationForm):
    nomEntreprise = forms.CharField(
        max_length=255,
        label="Nom de l'entreprise",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: TechNova Solutions'})
    )
    secteur = forms.CharField(
        max_length=255,
        label="Secteur d'activité",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Informatique, Finance, Santé...'})
    )
    adresse = forms.CharField(
        max_length=255,
        label="Adresse du siège",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 12 Rue de Rivoli, 75004 Paris'})
    )
    siteWeb = forms.URLField(
        required=False,
        label="Site Web",
        widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://monentreprise.com'})
    )
    description = forms.CharField(
        required=False,
        label="Description de l'entreprise",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Présentez les activités et la vision de votre entreprise...'
        })
    )

    def save(self):
        data = self.cleaned_data
        entreprise = Entreprise.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data['nomEntreprise'],
            role=Role.ENTREPRISE,
            nomEntreprise=data['nomEntreprise'],
            secteur=data['secteur'],
            adresse=data['adresse'],
            siteWeb=data.get('siteWeb', ''),
            description=data.get('description', '')
        )
        return entreprise


class FormateurRegisterForm(BaseRegistrationForm):
    prenom = forms.CharField(
        max_length=100,
        label="Prénom",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Marc'})
    )
    nom = forms.CharField(
        max_length=100,
        label="Nom",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Dupont'})
    )
    specialite = forms.CharField(
        max_length=255,
        label="Spécialité / Domaine d'expertise",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Architecte Python & Cloud'})
    )
    bio = forms.CharField(
        required=False,
        label="Biographie / Expérience pédagogique",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Décrivez votre parcours d\'instructeur et vos compétences clés...'
        })
    )

    def save(self):
        data = self.cleaned_data
        formateur = Formateur.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data['prenom'],
            last_name=data['nom'],
            role=Role.FORMATEUR,
            nom=data['nom'],
            prenom=data['prenom'],
            specialite=data['specialite'],
            bio=data.get('bio', '')
        )
        return formateur


# --- Formulaires de mise à jour de profil ---

class CandidatProfileForm(forms.ModelForm):
    email = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Candidat
        fields = ['email', 'prenom', 'nom', 'telephone', 'adresse', 'bio']
        widgets = {
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.first_name = instance.prenom
        instance.last_name = instance.nom
        if commit:
            instance.save()
        return instance


class EntrepriseProfileForm(forms.ModelForm):
    email = forms.EmailField(
        label="Adresse email de contact",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Entreprise
        fields = ['email', 'nomEntreprise', 'secteur', 'siteWeb', 'adresse', 'description']
        widgets = {
            'nomEntreprise': forms.TextInput(attrs={'class': 'form-control'}),
            'secteur': forms.TextInput(attrs={'class': 'form-control'}),
            'siteWeb': forms.URLInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.first_name = instance.nomEntreprise
        if commit:
            instance.save()
        return instance


class FormateurProfileForm(forms.ModelForm):
    email = forms.EmailField(
        label="Adresse email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Formateur
        fields = ['email', 'prenom', 'nom', 'specialite', 'bio']
        widgets = {
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'specialite': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.first_name = instance.prenom
        instance.last_name = instance.nom
        if commit:
            instance.save()
        return instance


class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
