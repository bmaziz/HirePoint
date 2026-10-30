from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta, date

from user.models import User, Role
from formateur.models import Formateur
from candidat.models import Candidat
from formation.models import Formation
from inscription.models import Inscription
from certification.models import Certification
from notification.models import Notification


class FormateurModuleTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Formateur 1
        self.formateur1 = Formateur.objects.create_user(
            username='formateur1',
            email='formateur1@hirepoint.fr',
            password='Password123!',
            role=Role.FORMATEUR,
            nom='Dupont',
            prenom='Marc',
            specialite='Django & Architecture Web',
            telephone='0611223344',
            experience='10 ans',
            bio='Formateur senior en développement back-end.'
        )

        # Formateur 2
        self.formateur2 = Formateur.objects.create_user(
            username='formateur2',
            email='formateur2@hirepoint.fr',
            password='Password123!',
            role=Role.FORMATEUR,
            nom='Benali',
            prenom='Sarah',
            specialite='React & Front-end Moderne',
            telephone='0699887766',
            experience='7 ans',
            bio='Formatrice UI/UX et React.'
        )

        # Candidat
        self.candidat = Candidat.objects.create_user(
            username='candidat1',
            email='candidat1@email.fr',
            password='Password123!',
            role=Role.CANDIDAT,
            nom='Martin',
            prenom='Julien',
            telephone='0601020304',
            adresse='Paris',
            bio='Développeur junior en reconversion.'
        )

        # Formation créée par Formateur 1
        today = timezone.now().date()
        self.formation1 = Formation.objects.create(
            titre='Maîtriser Django Avancé',
            description='Conception d applications web avec Django.',
            domaine='Développement Web',
            niveau='Intermédiaire',
            duree=40,
            dateDebut=today + timedelta(days=5),
            dateFin=today + timedelta(days=20),
            nombrePlaces=15,
            lieu='En ligne',
            formateur=self.formateur1
        )

        # Formation créée par Formateur 2
        self.formation2 = Formation.objects.create(
            titre='React 19 & TypeScript',
            description='Front-end moderne avec React.',
            domaine='Front-end',
            niveau='Débutant',
            duree=30,
            dateDebut=today + timedelta(days=2),
            dateFin=today + timedelta(days=15),
            nombrePlaces=20,
            lieu='Paris 15e',
            formateur=self.formateur2
        )

        # Inscription du candidat à la formation 1
        self.inscription1 = Inscription.objects.create(
            candidat=self.candidat,
            formation=self.formation1,
            statut='CONFIRMEE'
        )

    # -------------------------------------------------------------------------
    # Scénario 1 : Le formateur peut se connecter
    # -------------------------------------------------------------------------
    def test_01_trainer_can_login(self):
        login_success = self.client.login(username='formateur1', password='Password123!')
        self.assertTrue(login_success)

        # Accès au dashboard formateur
        response = self.client.get(reverse('formateur:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Marc Dupont')
        self.assertContains(response, 'Architecture Web')

    # -------------------------------------------------------------------------
    # Scénario 2 : Le formateur peut consulter et modifier son profil
    # -------------------------------------------------------------------------
    def test_02_trainer_profile_view_and_edit(self):
        self.client.login(username='formateur1', password='Password123!')

        # Consultation
        resp_view = self.client.get(reverse('formateur:profile'))
        self.assertEqual(resp_view.status_code, 200)
        self.assertContains(resp_view, 'Marc Dupont')
        self.assertContains(resp_view, '0611223344')

        # Modification
        resp_edit = self.client.post(reverse('formateur:profile_edit'), {
            'prenom': 'Marc-Antoine',
            'nom': 'Dupont',
            'email': 'marc.antoine@hirepoint.fr',
            'specialite': 'Lead Architecte Django & Cloud',
            'telephone': '0699001122',
            'experience': '12 ans',
            'bio': 'Nouvelle bio mise à jour.',
        })
        self.assertRedirects(resp_edit, reverse('formateur:profile'))

        self.formateur1.refresh_from_db()
        self.assertEqual(self.formateur1.prenom, 'Marc-Antoine')
        self.assertEqual(self.formateur1.specialite, 'Lead Architecte Django & Cloud')
        self.assertEqual(self.formateur1.email, 'marc.antoine@hirepoint.fr')

    # -------------------------------------------------------------------------
    # Scénario 3 : Le formateur peut créer une formation
    # -------------------------------------------------------------------------
    def test_03_trainer_can_create_course(self):
        self.client.login(username='formateur1', password='Password123!')
        today = timezone.now().date()

        data = {
            'titre': 'Docker & Kubernetes pour Développeurs',
            'domaine': 'Cloud & DevOps',
            'niveau': 'Avancé',
            'duree': 25,
            'dateDebut': today + timedelta(days=10),
            'dateFin': today + timedelta(days=25),
            'nombrePlaces': 12,
            'lieu': 'En ligne',
            'description': 'Automatisation CI/CD et déploiement.',
            'objectifs': 'Savoir conteneuriser une application.',
            'prerequis': 'Connaissances Linux de base.',
        }
        response = self.client.post(reverse('formateur:formation_create'), data)
        self.assertEqual(response.status_code, 302)

        # Vérification en base de données
        new_course = Formation.objects.get(titre='Docker & Kubernetes pour Développeurs')
        self.assertEqual(new_course.formateur, self.formateur1)
        self.assertEqual(new_course.nombrePlaces, 12)
        self.assertEqual(new_course.duree, 25)

    # -------------------------------------------------------------------------
    # Scénario 3bis : Validation des erreurs de date et capacité
    # -------------------------------------------------------------------------
    def test_03bis_formation_validation_rules(self):
        self.client.login(username='formateur1', password='Password123!')
        today = timezone.now().date()

        # Date de fin antérieure à la date de début
        invalid_data = {
            'titre': 'Formation Invalide',
            'domaine': 'Test',
            'niveau': 'Débutant',
            'duree': 10,
            'dateDebut': today + timedelta(days=10),
            'dateFin': today + timedelta(days=5),  # Invalide !
            'nombrePlaces': 10,
            'lieu': 'En ligne',
            'description': 'Description...',
        }
        response = self.client.post(reverse('formateur:formation_create'), invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'La date de fin ne peut pas précéder la date de début')

        # Capacité négative ou nulle
        invalid_data2 = {
            'titre': 'Formation Invalide Places',
            'domaine': 'Test',
            'niveau': 'Débutant',
            'duree': 10,
            'dateDebut': today + timedelta(days=5),
            'dateFin': today + timedelta(days=10),
            'nombrePlaces': 0,  # Invalide !
            'lieu': 'En ligne',
            'description': 'Description...',
        }
        response2 = self.client.post(reverse('formateur:formation_create'), invalid_data2)
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, 'strictement supérieure à 0')

    # -------------------------------------------------------------------------
    # Scénario 4 & 5 : Consulter, modifier et supprimer ses propres formations
    # -------------------------------------------------------------------------
    def test_04_05_trainer_read_update_delete_own_courses(self):
        self.client.login(username='formateur1', password='Password123!')

        # Liste des formations
        resp_list = self.client.get(reverse('formateur:formation_list'))
        self.assertEqual(resp_list.status_code, 200)
        self.assertContains(resp_list, 'Maîtriser Django Avancé')
        # La formation du formateur 2 ne doit PAS apparaître dans sa liste
        self.assertNotContains(resp_list, 'React 19 & TypeScript')

        # Détail de sa formation
        resp_detail = self.client.get(reverse('formateur:formation_detail', args=[self.formation1.id]))
        self.assertEqual(resp_detail.status_code, 200)
        self.assertContains(resp_detail, 'Maîtriser Django Avancé')

        # Modification
        today = timezone.now().date()
        resp_update = self.client.post(reverse('formateur:formation_update', args=[self.formation1.id]), {
            'titre': 'Maîtriser Django Avancé & REST APIs',
            'domaine': 'Développement Web',
            'niveau': 'Avancé',
            'duree': 45,
            'dateDebut': today + timedelta(days=5),
            'dateFin': today + timedelta(days=25),
            'nombrePlaces': 18,
            'lieu': 'Distanciel & Présentiel',
            'description': 'Description mise à jour.',
        })
        self.assertRedirects(resp_update, reverse('formateur:formation_detail', args=[self.formation1.id]))
        self.formation1.refresh_from_db()
        self.assertEqual(self.formation1.titre, 'Maîtriser Django Avancé & REST APIs')
        self.assertEqual(self.formation1.nombrePlaces, 18)

        # Suppression
        resp_delete = self.client.post(reverse('formateur:formation_delete', args=[self.formation1.id]))
        self.assertRedirects(resp_delete, reverse('formateur:formation_list'))
        self.assertFalse(Formation.objects.filter(id=self.formation1.id).exists())

    # -------------------------------------------------------------------------
    # Scénario 6 : Un formateur ne peut PAS modifier ni supprimer la formation d'un autre
    # -------------------------------------------------------------------------
    def test_06_trainer_cannot_access_or_modify_other_trainer_course(self):
        # Connexion en tant que Formateur 1
        self.client.login(username='formateur1', password='Password123!')

        # Tentative de consultation du détail de la formation 2 (appartient à Formateur 2)
        resp_detail = self.client.get(reverse('formateur:formation_detail', args=[self.formation2.id]))
        self.assertEqual(resp_detail.status_code, 403)

        # Tentative de modification de la formation 2
        resp_update = self.client.post(reverse('formateur:formation_update', args=[self.formation2.id]), {
            'titre': 'Piratage de titre',
            'domaine': 'Hacking',
            'niveau': 'Avancé',
            'duree': 10,
            'dateDebut': timezone.now().date(),
            'dateFin': timezone.now().date() + timedelta(days=5),
            'nombrePlaces': 10,
            'description': 'Test fail',
        })
        self.assertEqual(resp_update.status_code, 403)

        # Tentative de suppression de la formation 2
        resp_delete = self.client.post(reverse('formateur:formation_delete', args=[self.formation2.id]))
        self.assertEqual(resp_delete.status_code, 403)
        self.assertTrue(Formation.objects.filter(id=self.formation2.id).exists())

    # -------------------------------------------------------------------------
    # Scénario 7 : Gestion des participants et isolation des données
    # -------------------------------------------------------------------------
    def test_07_trainer_views_only_own_participants(self):
        # Formateur 1 connecté : doit voir Julien Martin inscrit à sa formation 1
        self.client.login(username='formateur1', password='Password123!')
        resp1 = self.client.get(reverse('formateur:participant_list'))
        self.assertEqual(resp1.status_code, 200)
        self.assertContains(resp1, 'Julien Martin')

        # Formateur 2 connecté : ne doit PAS voir Julien Martin car inscrit à la formation 1
        self.client.login(username='formateur2', password='Password123!')
        resp2 = self.client.get(reverse('formateur:participant_list'))
        self.assertEqual(resp2.status_code, 200)
        self.assertNotContains(resp2, 'Julien Martin')

    # -------------------------------------------------------------------------
    # Scénario 8 & 9 : Délivrance de certification, unicité et anti-doublon
    # -------------------------------------------------------------------------
    def test_08_09_certification_issuance_and_uniqueness(self):
        self.client.login(username='formateur1', password='Password123!')
        today = timezone.now().date()

        # Émission d'une certification pour l'inscription 1
        data = {
            'inscription': self.inscription1.id,
            'titre': 'Certificat d Excellence Django',
            'dateObtention': str(today),
        }
        response = self.client.post(reverse('formateur:certification_issue'), data)
        self.assertEqual(response.status_code, 302)

        # Vérification en base
        cert = Certification.objects.get(inscription=self.inscription1)
        self.assertEqual(cert.titre, 'Certificat d Excellence Django')
        self.assertTrue(cert.reference.startswith(f"CERT-{today.year}-"))
        self.assertEqual(self.inscription1.candidat, cert.inscription.candidat)

        # Vérification qu'un fichier d'attestation a été généré
        self.assertTrue(bool(cert.fichier))

        # Vérification que le statut de l'inscription est passé à TERMINEE
        self.inscription1.refresh_from_db()
        self.assertEqual(self.inscription1.statut, 'TERMINEE')

        # Vérification de l'anti-doublon : ré-essayer de certifier la même inscription
        response_duplicate = self.client.post(reverse('formateur:certification_issue'), data)
        # Le formulaire rejette la sélection car déjà certifié
        self.assertNotEqual(response_duplicate.status_code, 302)

    # -------------------------------------------------------------------------
    # Scénario 10 : Gestion des notifications
    # -------------------------------------------------------------------------
    def test_10_trainer_notifications(self):
        # Création d'une notification pour Formateur 1
        notif1 = Notification.objects.create(
            user=self.formateur1,
            type='FORMATION',
            message='Nouvel apprenant inscrit à Django.',
            lue=False
        )
        # Création d'une notification pour Formateur 2
        notif2 = Notification.objects.create(
            user=self.formateur2,
            type='FORMATION',
            message='Message privé pour formateur 2.',
            lue=False
        )

        self.client.login(username='formateur1', password='Password123!')
        resp = self.client.get(reverse('formateur:notification_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Nouvel apprenant inscrit à Django.')
        self.assertNotContains(resp, 'Message privé pour formateur 2.')

        # Marquer comme lue
        resp_mark = self.client.get(reverse('formateur:notification_mark_read', args=[notif1.id]))
        self.assertRedirects(resp_mark, reverse('formateur:notification_list'))
        notif1.refresh_from_db()
        self.assertTrue(notif1.lue)

    # -------------------------------------------------------------------------
    # Scénario 11 : Sécurité & Non-régression (Candidat ne peut pas accéder aux pages Formateur)
    # -------------------------------------------------------------------------
    def test_11_candidate_cannot_access_trainer_module(self):
        self.client.login(username='candidat1', password='Password123!')

        # Un candidat essaie d'accéder au dashboard formateur
        response = self.client.get(reverse('formateur:dashboard'))
        self.assertRedirects(response, reverse('dashboard'))

        # Un candidat essaie de créer une formation
        response_create = self.client.get(reverse('formateur:formation_create'))
        self.assertRedirects(response_create, reverse('dashboard'))
