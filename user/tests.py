from django.test import TestCase, Client
from django.urls import reverse
from user.models import User, Role
from candidat.models import Candidat
from entreprise.models import Entreprise
from formateur.models import Formateur


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Création d'un candidat de test
        self.candidat = Candidat.objects.create_user(
            username='candidat_test',
            email='candidat@test.com',
            password='Password123!',
            role=Role.CANDIDAT,
            nom='Dupont',
            prenom='Jean',
            telephone='0612345678',
            adresse='Paris',
            bio='Bio test'
        )

    def test_login_with_username(self):
        """Vérifie la connexion avec le nom d'utilisateur."""
        response = self.client.post(reverse('login'), {
            'username_or_email': 'candidat_test',
            'password': 'Password123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_with_email(self):
        """Vérifie la connexion avec l'adresse email."""
        response = self.client.post(reverse('login'), {
            'username_or_email': 'candidat@test.com',
            'password': 'Password123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_invalid_password(self):
        """Vérifie le rejet d'un mot de passe incorrect."""
        response = self.client.post(reverse('login'), {
            'username_or_email': 'candidat_test',
            'password': 'WrongPassword!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Identifiant ou mot de passe incorrect")

    def test_logout(self):
        """Vérifie la déconnexion et la redirection vers l'accueil."""
        self.client.login(username='candidat_test', password='Password123!')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))

    def test_candidat_registration(self):
        """Vérifie l'inscription complète d'un nouveau candidat."""
        data = {
            'target_role': 'candidat',
            'candidat-username': 'nouveau_candidat',
            'candidat-email': 'nouveau@candidat.fr',
            'candidat-prenom': 'Sophie',
            'candidat-nom': 'Martin',
            'candidat-telephone': '0698765432',
            'candidat-adresse': 'Lyon',
            'candidat-bio': 'Passionnée de Python',
            'candidat-password': 'NouveauPassword123!',
            'candidat-password_confirm': 'NouveauPassword123!',
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

        # Vérifie la présence en BDD
        user = User.objects.get(username='nouveau_candidat')
        self.assertEqual(user.role, Role.CANDIDAT)
        self.assertTrue(hasattr(user, 'candidat'))
        self.assertEqual(user.candidat.nom, 'Martin')

    def test_entreprise_registration(self):
        """Vérifie l'inscription complète d'une nouvelle entreprise."""
        data = {
            'target_role': 'entreprise',
            'entreprise-username': 'nouvelle_boite',
            'entreprise-email': 'contact@nouvelleboite.com',
            'entreprise-nomEntreprise': 'Nouvelle Boite Tech',
            'entreprise-secteur': 'IA & Cloud',
            'entreprise-adresse': 'Marseille',
            'entreprise-siteWeb': 'https://nouvelleboite.com',
            'entreprise-description': 'Startup innovante',
            'entreprise-password': 'NouveauPassword123!',
            'entreprise-password_confirm': 'NouveauPassword123!',
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

        user = User.objects.get(username='nouvelle_boite')
        self.assertEqual(user.role, Role.ENTREPRISE)
        self.assertTrue(hasattr(user, 'entreprise'))
        self.assertEqual(user.entreprise.nomEntreprise, 'Nouvelle Boite Tech')

    def test_formateur_registration(self):
        """Vérifie l'inscription complète d'un nouveau formateur."""
        data = {
            'target_role': 'formateur',
            'formateur-username': 'nouveau_formateur',
            'formateur-email': 'formateur@formation.fr',
            'formateur-prenom': 'Pierre',
            'formateur-nom': 'Durand',
            'formateur-specialite': 'Kubernetes & Docker',
            'formateur-bio': '10 ans d\'expérience',
            'formateur-password': 'NouveauPassword123!',
            'formateur-password_confirm': 'NouveauPassword123!',
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard'))

        user = User.objects.get(username='nouveau_formateur')
        self.assertEqual(user.role, Role.FORMATEUR)
        self.assertTrue(hasattr(user, 'formateur'))
        self.assertEqual(user.formateur.specialite, 'Kubernetes & Docker')

    def test_dashboard_requires_login(self):
        """Vérifie que le dashboard redirige les utilisateurs anonymes vers le login."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_dashboard_authenticated(self):
        """Vérifie que le candidat connecté accède au dashboard."""
        self.client.login(username='candidat_test', password='Password123!')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bienvenue, Jean Dupont")

    def test_profile_view(self):
        """Vérifie la page profil."""
        self.client.login(username='candidat_test', password='Password123!')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "candidat@test.com")
        self.assertContains(response, "Paris")
