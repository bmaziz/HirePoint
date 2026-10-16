import datetime
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.db import transaction

from user.models import User, Role
from entreprise.models import Entreprise
from formateur.models import Formateur
from candidat.models import Candidat
from competence.models import Competence
from offre.models import Offre
from formation.models import Formation
from candidature.models import Candidature, StatutCandidature
from inscription.models import Inscription
from certification.models import Certification
from cv.models import CV
from diplome.models import Diplome
from experience.models import Experience
from notification.models import Notification


class Command(BaseCommand):
    help = "Remplit la base de données HirePoint avec un ensemble complet de données de test réalistes."

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Supprime les données existantes avant de peupler la base.',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING("Suppression des donnees existantes..."))
            self.clear_database()

        self.stdout.write(self.style.NOTICE("Debut du remplissage de la base de donnees..."))
        with transaction.atomic():
            admin_user = self.create_admin()
            competences = self.create_competences()
            entreprises = self.create_entreprises()
            formateurs = self.create_formateurs()
            formations = self.create_formations(formateurs)
            offres = self.create_offres(entreprises, competences)
            candidats = self.create_candidats(competences)
            self.create_cvs(candidats)
            self.create_diplomes(candidats)
            self.create_experiences(candidats)
            self.create_candidatures(candidats, offres)
            inscriptions = self.create_inscriptions(candidats, formations)
            self.create_certifications(inscriptions)
            self.create_notifications(admin_user, candidats, entreprises, formateurs)

        self.stdout.write(self.style.SUCCESS("[OK] Base de donnees remplie avec succes !"))
        self.print_summary()

    def clear_database(self):
        Notification.objects.all().delete()
        Certification.objects.all().delete()
        Inscription.objects.all().delete()
        Candidature.objects.all().delete()
        Experience.objects.all().delete()
        Diplome.objects.all().delete()
        CV.objects.all().delete()
        Offre.objects.all().delete()
        Formation.objects.all().delete()
        Candidat.objects.all().delete()
        Formateur.objects.all().delete()
        Entreprise.objects.all().delete()
        Competence.objects.all().delete()
        User.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("[OK] Donnees precedentes supprimees."))

    def create_admin(self):
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@hirepoint.fr',
                'first_name': 'Admin',
                'last_name': 'HirePoint',
                'role': Role.ADMINISTRATEUR,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()
        self.stdout.write(f"  - Administrateur: {admin_user.username} (mot de passe: admin123)")
        return admin_user

    def create_competences(self):
        skills_data = [
            "Python", "Django", "JavaScript", "TypeScript", "React",
            "Vue.js", "Node.js", "Docker & Kubernetes", "DevOps & CI/CD",
            "SQL & PostgreSQL", "Machine Learning & IA", "Data Science",
            "Cybersécurité", "Agile & Scrum", "Git & GitHub", "UI/UX Design",
            "Java & Spring Boot", "Linux & Bash", "Architecture Microservices",
            "API REST & GraphQL"
        ]
        competences = {}
        for nom in skills_data:
            comp, _ = Competence.objects.get_or_create(nom=nom)
            competences[nom] = comp
        self.stdout.write(f"  - {len(competences)} competences creees.")
        return competences

    def create_entreprises(self):
        entreprises_data = [
            {
                'username': 'technova',
                'email': 'contact@technova.io',
                'nomEntreprise': 'TechNova Solutions',
                'secteur': 'Informatique & Cloud',
                'description': 'TechNova Solutions est une entreprise innovante éditrice de solutions SaaS et d\'infrastructures Cloud haute performance pour grands comptes et startups.',
                'adresse': '12 Rue de Rivoli, 75004 Paris',
                'siteWeb': 'https://technova.io'
            },
            {
                'username': 'fintech_horizon',
                'email': 'rh@fintech-horizon.com',
                'nomEntreprise': 'FinTech Horizon',
                'secteur': 'Banque & Finance Digitale',
                'description': 'Leader européen des solutions de paiement sécurisé, d\'Open Banking et de conformité réglementaire numérique.',
                'adresse': '45 Avenue de l\'Opéra, 75001 Paris',
                'siteWeb': 'https://fintech-horizon.com'
            },
            {
                'username': 'datasphere',
                'email': 'recrutement@datasphere.ai',
                'nomEntreprise': 'DataSphere Analytics',
                'secteur': 'Intelligence Artificielle & Big Data',
                'description': 'Cabinet d\'ingénierie et de conseil expert dans la valorisation de données, l\'analyse prédictive et les modèles d\'IA générative.',
                'adresse': '8 Boulevard Haussmann, 75009 Paris',
                'siteWeb': 'https://datasphere.ai'
            },
            {
                'username': 'greendigital',
                'email': 'jobs@greendigital.fr',
                'nomEntreprise': 'GreenDigital Studio',
                'secteur': 'Numérique Éco-responsable & Web',
                'description': 'Agence digitale engagée dans l\'éco-conception web, l\'optimisation de l\'empreinte carbone logicielle et l\'accessibilité numérique.',
                'adresse': '27 Quai des Chartrons, 33000 Bordeaux',
                'siteWeb': 'https://greendigital.fr'
            },
            {
                'username': 'cybershield',
                'email': 'contact@cybershield.eu',
                'nomEntreprise': 'CyberShield Protect',
                'secteur': 'Cybersécurité & Audit SI',
                'description': 'Spécialiste de la cybersécurité offensive et défensive : tests d\'intrusion, gouvernance de sécurité et réponse aux incidents.',
                'adresse': '10 Allée de la Robertsau, 67000 Strasbourg',
                'siteWeb': 'https://cybershield.eu'
            }
        ]

        entreprises = {}
        for data in entreprises_data:
            username = data['username']
            ent, _ = Entreprise.objects.get_or_create(
                username=username,
                defaults={
                    'email': data['email'],
                    'first_name': data['nomEntreprise'],
                    'nomEntreprise': data['nomEntreprise'],
                    'secteur': data['secteur'],
                    'description': data['description'],
                    'adresse': data['adresse'],
                    'siteWeb': data['siteWeb'],
                    'role': Role.ENTREPRISE,
                }
            )
            ent.set_password('password123')
            ent.save()
            entreprises[username] = ent

        self.stdout.write(f"  - {len(entreprises)} entreprises creees (mot de passe: password123).")
        return entreprises

    def create_formateurs(self):
        formateurs_data = [
            {
                'username': 'mdupont',
                'email': 'marc.dupont@hirepoint.fr',
                'nom': 'Dupont',
                'prenom': 'Marc',
                'specialite': 'Architecte Logiciel Python & Django',
                'bio': '12 ans d\'expérience dans l\'écosystème Python, formateur certifié et contributeur actif à plusieurs bibliothèques Open Source.'
            },
            {
                'username': 'sbenali',
                'email': 'sarah.benali@hirepoint.fr',
                'nom': 'Benali',
                'prenom': 'Sarah',
                'specialite': 'Experte Frontend React & Architecture TypeScript',
                'bio': 'Lead Developer Frontend passionnée par les performances web, le design system et l\'architecture moderne avec React et TypeScript.'
            },
            {
                'username': 'amoreau',
                'email': 'alexandre.moreau@hirepoint.fr',
                'nom': 'Moreau',
                'prenom': 'Alexandre',
                'specialite': 'Consultant DevOps, Kubernetes & Cloud Architecture',
                'bio': 'Ingénieur Cloud & DevOps accompagnant les entreprises dans l\'automatisation de pipelines CI/CD et la conteneurisation à grande échelle.'
            }
        ]

        formateurs = {}
        for data in formateurs_data:
            username = data['username']
            fmt, _ = Formateur.objects.get_or_create(
                username=username,
                defaults={
                    'email': data['email'],
                    'first_name': data['prenom'],
                    'last_name': data['nom'],
                    'nom': data['nom'],
                    'prenom': data['prenom'],
                    'specialite': data['specialite'],
                    'bio': data['bio'],
                    'role': Role.FORMATEUR,
                }
            )
            fmt.set_password('password123')
            fmt.save()
            formateurs[username] = fmt

        self.stdout.write(f"  - {len(formateurs)} formateurs crees (mot de passe: password123).")
        return formateurs

    def create_formations(self, formateurs):
        today = datetime.date.today()
        formations_data = [
            {
                'titre': 'Maîtriser Django & les APIs REST Avancées',
                'description': 'Programme complet de conception d\'applications web robustes avec Django, Django REST Framework, authentification JWT et bonnes pratiques de testing.',
                'domaine': 'Développement Web Back-end',
                'niveau': 'Intermédiaire',
                'duree': 40,
                'dateDebut': today + datetime.timedelta(days=15),
                'dateFin': today + datetime.timedelta(days=35),
                'nombrePlaces': 15,
                'formateur': formateurs['mdupont']
            },
            {
                'titre': 'React 19 & TypeScript Moderne en Entreprise',
                'description': 'Concevez des interfaces web dynamiques et maintenables avec React 19, les Hooks avancés, TanStack Query, et un typage strict TypeScript.',
                'domaine': 'Développement Web Front-end',
                'niveau': 'Débutant à Intermédiaire',
                'duree': 35,
                'dateDebut': today + datetime.timedelta(days=20),
                'dateFin': today + datetime.timedelta(days=40),
                'nombrePlaces': 20,
                'formateur': formateurs['sbenali']
            },
            {
                'titre': 'DevOps Pratique : Docker, Kubernetes & CI/CD',
                'description': 'Automatisez le cycle de déploiement logiciel avec Docker, Kubernetes, GitHub Actions et le monitoring d\'infrastructures conteneurisées.',
                'domaine': 'Cloud & DevOps',
                'niveau': 'Avancé',
                'duree': 30,
                'dateDebut': today + datetime.timedelta(days=30),
                'dateFin': today + datetime.timedelta(days=45),
                'nombrePlaces': 12,
                'formateur': formateurs['amoreau']
            },
            {
                'titre': 'Intelligence Artificielle & Machine Learning avec Python',
                'description': 'Découverte et application pratique des algorithmes d\'apprentissage automatique (Scikit-Learn, Pandas, NumPy) et initiation aux modèles génératifs.',
                'domaine': 'Data Science & IA',
                'niveau': 'Intermédiaire',
                'duree': 50,
                'dateDebut': today - datetime.timedelta(days=60),
                'dateFin': today - datetime.timedelta(days=20),
                'nombrePlaces': 18,
                'formateur': formateurs['mdupont']
            },
            {
                'titre': 'Cybersécurité : Sécurisation et Audit des Applications Web',
                'description': 'Identification des failles OWASP Top 10, mise en place des défenses applicatives et simulation d\'attaques éthiques.',
                'domaine': 'Cybersécurité',
                'niveau': 'Intermédiaire à Avancé',
                'duree': 25,
                'dateDebut': today + datetime.timedelta(days=45),
                'dateFin': today + datetime.timedelta(days=60),
                'nombrePlaces': 10,
                'formateur': formateurs['amoreau']
            }
        ]

        formations = []
        for data in formations_data:
            form, _ = Formation.objects.get_or_create(
                titre=data['titre'],
                formateur=data['formateur'],
                defaults=data
            )
            formations.append(form)

        self.stdout.write(f"  - {len(formations)} formations creees.")
        return formations

    def create_offres(self, entreprises, competences):
        today = datetime.date.today()
        offres_data = [
            {
                'titre': 'Développeur Fullstack Django / React',
                'description': 'Nous recherchons un développeur Fullstack talentueux pour concevoir et faire évoluer notre plateforme SaaS phare. Vous participerez aux choix d\'architecture et à la création d\'expériences utilisateur fluides.',
                'localisation': 'Paris (75) - Hybride (2j télétravail)',
                'typeContrat': 'CDI',
                'niveauExperience': 'Confirmé (2 à 5 ans)',
                'salaire': 48000.00,
                'dateExpiration': today + datetime.timedelta(days=45),
                'statut': 'ACTIVE',
                'entreprise': entreprises['technova'],
                'skills': ['Python', 'Django', 'React', 'JavaScript', 'SQL & PostgreSQL', 'Git & GitHub']
            },
            {
                'titre': 'Ingénieur DevOps Cloud & Infrastructure',
                'description': 'Dans le cadre de l\'expansion de notre infrastructure AWS, vous piloterez le déploiement de clusters Kubernetes et l\'optimisation de nos pipelines CI/CD.',
                'localisation': 'Paris (75) - Télétravail partiel',
                'typeContrat': 'CDI',
                'niveauExperience': 'Senior (5 ans et +)',
                'salaire': 62000.00,
                'dateExpiration': today + datetime.timedelta(days=60),
                'statut': 'ACTIVE',
                'entreprise': entreprises['technova'],
                'skills': ['Docker & Kubernetes', 'DevOps & CI/CD', 'Linux & Bash', 'Architecture Microservices']
            },
            {
                'titre': 'Développeur Backend Python Senior',
                'description': 'Rejoignez le pôle core-banking de FinTech Horizon pour bâtir des APIs financières résilientes, à très haute disponibilité et faible latence.',
                'localisation': 'Paris (75) - Sur site',
                'typeContrat': 'CDI',
                'niveauExperience': 'Senior (5 ans et +)',
                'salaire': 68000.00,
                'dateExpiration': today + datetime.timedelta(days=30),
                'statut': 'ACTIVE',
                'entreprise': entreprises['fintech_horizon'],
                'skills': ['Python', 'Django', 'SQL & PostgreSQL', 'Architecture Microservices', 'API REST & GraphQL']
            },
            {
                'titre': 'Data Scientist / Machine Learning Engineer',
                'description': 'Vous interviendrez auprès de nos clients stratégiques pour créer des modèles d\'analyse prédictive et intégrer des solutions d\'IA dans des environnements de production.',
                'localisation': 'Lyon (69) - Hybride',
                'typeContrat': 'CDI',
                'niveauExperience': 'Confirmé (3 à 5 ans)',
                'salaire': 54000.00,
                'dateExpiration': today + datetime.timedelta(days=40),
                'statut': 'ACTIVE',
                'entreprise': entreprises['datasphere'],
                'skills': ['Python', 'Data Science', 'Machine Learning & IA', 'SQL & PostgreSQL']
            },
            {
                'titre': 'Stagiaire Développeur Web Frontend',
                'description': 'Stage de 6 mois au sein d\'une équipe créative et engagée. Vous contribuerez au développement de sites web à faible impact environnemental et accessibles.',
                'localisation': 'Bordeaux (33) - Sur site',
                'typeContrat': 'Stage',
                'niveauExperience': 'Débutant / Étudiant',
                'salaire': 1200.00,
                'dateExpiration': today + datetime.timedelta(days=25),
                'statut': 'ACTIVE',
                'entreprise': entreprises['greendigital'],
                'skills': ['JavaScript', 'TypeScript', 'React', 'UI/UX Design']
            },
            {
                'titre': 'Développeur Web Vue.js & TypeScript',
                'description': 'GreenDigital renforce ses équipes pour créer des applications web écoconçues. Bonne maîtrise de TypeScript et de l\'intégration responsive attendue.',
                'localisation': 'Bordeaux (33) - Hybride',
                'typeContrat': 'CDD',
                'niveauExperience': 'Junior (1 à 2 ans)',
                'salaire': 36000.00,
                'dateExpiration': today + datetime.timedelta(days=50),
                'statut': 'ACTIVE',
                'entreprise': entreprises['greendigital'],
                'skills': ['JavaScript', 'TypeScript', 'Vue.js', 'UI/UX Design']
            },
            {
                'titre': 'Consultant Sécurité des Systèmes d\'Information & Pentest',
                'description': 'Réalisation d\'audits d\'architecture, de tests d\'intrusion (web, mobile, réseau) et accompagnement des équipes techniques sur la remédiation.',
                'localisation': 'Strasbourg (67) - Hybride',
                'typeContrat': 'CDI',
                'niveauExperience': 'Senior (4 ans et +)',
                'salaire': 58000.00,
                'dateExpiration': today + datetime.timedelta(days=35),
                'statut': 'ACTIVE',
                'entreprise': entreprises['cybershield'],
                'skills': ['Cybersécurité', 'Linux & Bash', 'DevOps & CI/CD']
            },
            {
                'titre': 'Lead Developer Java / Spring Boot',
                'description': 'Encadrement d\'une squad de 5 développeurs sur notre passerelle de paiement. Connaissance approfondie de Spring Boot, des transactions distribuées et de Kafka.',
                'localisation': 'Paris (75) - Hybride',
                'typeContrat': 'CDI',
                'niveauExperience': 'Senior (6 ans et +)',
                'salaire': 72000.00,
                'dateExpiration': today + datetime.timedelta(days=45),
                'statut': 'ACTIVE',
                'entreprise': entreprises['fintech_horizon'],
                'skills': ['Java & Spring Boot', 'SQL & PostgreSQL', 'Architecture Microservices', 'Agile & Scrum']
            }
        ]

        offres = []
        for data in offres_data:
            skills = data.pop('skills')
            offre, _ = Offre.objects.get_or_create(
                titre=data['titre'],
                entreprise=data['entreprise'],
                defaults=data
            )
            for skill_name in skills:
                if skill_name in competences:
                    offre.competences.add(competences[skill_name])
            offres.append(offre)

        self.stdout.write(f"  - {len(offres)} offres d'emploi creees.")
        return offres

    def create_candidats(self, competences):
        candidats_data = [
            {
                'username': 'tbernard',
                'email': 'thomas.bernard@email.fr',
                'nom': 'Bernard',
                'prenom': 'Thomas',
                'telephone': '06 12 34 56 78',
                'adresse': '18 Rue Victor Hugo, 75011 Paris',
                'bio': 'Développeur Fullstack passionné par Python, Django et l\'écosystème React. 3 ans d\'expérience dans des startups dynamiques, rigoureux et adepte du code propre.',
                'skills': ['Python', 'Django', 'JavaScript', 'React', 'SQL & PostgreSQL', 'Git & GitHub']
            },
            {
                'username': 'claurent',
                'email': 'camille.laurent@email.fr',
                'nom': 'Laurent',
                'prenom': 'Camille',
                'telephone': '06 98 76 54 32',
                'adresse': '5 Rue Nationale, 69002 Lyon',
                'bio': 'Data Scientist et ingénieure en apprentissage automatique. Forte expérience en modélisation prédictive, analyse exploratoire de données et déploiement de modèles.',
                'skills': ['Python', 'Data Science', 'Machine Learning & IA', 'SQL & PostgreSQL', 'Git & GitHub']
            },
            {
                'username': 'jmartin',
                'email': 'julien.martin@email.fr',
                'nom': 'Martin',
                'prenom': 'Julien',
                'telephone': '07 45 67 89 01',
                'adresse': '14 Rue Sainte-Catherine, 33000 Bordeaux',
                'bio': 'Développeur Frontend enthousiaste, sensible au design, à l\'expérience utilisateur (UX) et aux performances web modernes avec React et Vue.js.',
                'skills': ['JavaScript', 'TypeScript', 'React', 'Vue.js', 'UI/UX Design']
            },
            {
                'username': 'adiallo',
                'email': 'amina.diallo@email.fr',
                'nom': 'Diallo',
                'prenom': 'Amina',
                'telephone': '06 55 44 33 22',
                'adresse': '8 Boulevard de Strasbourg, 75010 Paris',
                'bio': 'Ingénieure DevOps orientée automatisation, Docker, Kubernetes et sécurité Cloud. Passionnée par la culture CI/CD et l\'infrastructure as Code.',
                'skills': ['Docker & Kubernetes', 'DevOps & CI/CD', 'Linux & Bash', 'Cybersécurité', 'Git & GitHub']
            },
            {
                'username': 'lpetit',
                'email': 'lucas.petit@email.fr',
                'nom': 'Petit',
                'prenom': 'Lucas',
                'telephone': '06 11 22 33 44',
                'adresse': '21 Rue des Lilas, 44000 Nantes',
                'bio': 'Jeune diplômé curieux et motivé en développement logiciel. Prêt à s\'investir dans des projets concrets, curieux des architectures web actuelles.',
                'skills': ['Python', 'Django', 'JavaScript', 'SQL & PostgreSQL', 'Git & GitHub', 'Agile & Scrum']
            }
        ]

        candidats = {}
        for data in candidats_data:
            username = data['username']
            skills = data.pop('skills')
            cand, _ = Candidat.objects.get_or_create(
                username=username,
                defaults={
                    'email': data['email'],
                    'first_name': data['prenom'],
                    'last_name': data['nom'],
                    'nom': data['nom'],
                    'prenom': data['prenom'],
                    'telephone': data['telephone'],
                    'adresse': data['adresse'],
                    'bio': data['bio'],
                    'role': Role.CANDIDAT,
                }
            )
            cand.set_password('password123')
            cand.save()
            for skill_name in skills:
                if skill_name in competences:
                    cand.competences.add(competences[skill_name])
            candidats[username] = cand

        self.stdout.write(f"  - {len(candidats)} candidats crees (mot de passe: password123).")
        return candidats

    def create_cvs(self, candidats):
        count = 0
        for cand in candidats.values():
            if not hasattr(cand, 'cv'):
                dummy_content = f"CV de {cand.prenom} {cand.nom}\nEmail: {cand.email}\nTel: {cand.telephone}\nBio: {cand.bio}\n".encode('utf-8')
                cv = CV(candidat=cand)
                cv.fichier.save(f"cv_{cand.username}.txt", ContentFile(dummy_content), save=True)
                count += 1
        self.stdout.write(f"  - {count} CVs generes.")

    def create_diplomes(self, candidats):
        diplomes_data = [
            # Thomas Bernard
            {'candidat': candidats['tbernard'], 'titre': 'Master Informatique & Génie Logiciel', 'etablissement': 'Université Paris-Saclay', 'dateObtention': datetime.date(2023, 7, 5)},
            {'candidat': candidats['tbernard'], 'titre': 'Licence Informatique Générale', 'etablissement': 'Université Paris-Cité', 'dateObtention': datetime.date(2021, 6, 28)},
            # Camille Laurent
            {'candidat': candidats['claurent'], 'titre': 'Diplôme d\'Ingénieur en Data Science & IA', 'etablissement': 'INSA Lyon', 'dateObtention': datetime.date(2022, 9, 15)},
            {'candidat': candidats['claurent'], 'titre': 'Classes Préparatoires MPSI / MP', 'etablissement': 'Lycée du Parc Lyon', 'dateObtention': datetime.date(2019, 6, 20)},
            # Julien Martin
            {'candidat': candidats['jmartin'], 'titre': 'Licence Pro Métiers de l\'Internet & Applications Web', 'etablissement': 'IUT de Bordeaux', 'dateObtention': datetime.date(2024, 6, 25)},
            {'candidat': candidats['jmartin'], 'titre': 'DUT Informatique', 'etablissement': 'IUT de Bordeaux', 'dateObtention': datetime.date(2023, 6, 20)},
            # Amina Diallo
            {'candidat': candidats['adiallo'], 'titre': 'Master Systèmes Répartis, Cloud & Sécurité', 'etablissement': 'Sorbonne Université', 'dateObtention': datetime.date(2021, 7, 10)},
            # Lucas Petit
            {'candidat': candidats['lpetit'], 'titre': 'BTS Services Informatiques aux Organisations (SLAM)', 'etablissement': 'Lycée La Joliverie Nantes', 'dateObtention': datetime.date(2025, 6, 30)},
        ]

        for d in diplomes_data:
            Diplome.objects.get_or_create(
                candidat=d['candidat'],
                titre=d['titre'],
                defaults=d
            )
        self.stdout.write(f"  - {len(diplomes_data)} diplomes enregistres.")

    def create_experiences(self, candidats):
        exp_data = [
            # Thomas Bernard
            {
                'candidat': candidats['tbernard'],
                'poste': 'Développeur Fullstack Django / React',
                'entreprise': 'WebAgency Paris',
                'description': 'Conception et refonte d\'applications web clientes, intégration d\'APIs REST sous Django et modernisation de composants React.',
                'dateDebut': datetime.date(2023, 9, 1),
                'dateFin': None
            },
            {
                'candidat': candidats['tbernard'],
                'poste': 'Développeur Web Stagiaire',
                'entreprise': 'StartupLab Incubateur',
                'description': 'Développement de prototypes MVP en Python et automatisation de scripts d\'extraction de données.',
                'dateDebut': datetime.date(2022, 3, 1),
                'dateFin': datetime.date(2022, 8, 31)
            },
            # Camille Laurent
            {
                'candidat': candidats['claurent'],
                'poste': 'Data Analyst & Machine Learning',
                'entreprise': 'BigData Consulting Lyon',
                'description': 'Mise en place de dashboards décisionnels, nettoyage de données volumineuses et entraînement d\'algorithmes prédictifs pour le secteur retail.',
                'dateDebut': datetime.date(2022, 10, 1),
                'dateFin': None
            },
            # Julien Martin
            {
                'candidat': candidats['jmartin'],
                'poste': 'Développeur Frontend Junior',
                'entreprise': 'CreativeCode Bordeaux',
                'description': 'Intégration d\'interfaces interactives sous React et Tailwind CSS, optimisation SEO et accessibilité RGAA.',
                'dateDebut': datetime.date(2024, 9, 1),
                'dateFin': None
            },
            # Amina Diallo
            {
                'candidat': candidats['adiallo'],
                'poste': 'Ingénieure DevOps Cloud',
                'entreprise': 'CloudForge Paris',
                'description': 'Gestion de l\'infrastructure Kubernetes sur AWS, mise en place des chaînes de build CI/CD GitLab et monitoring Datadog.',
                'dateDebut': datetime.date(2021, 9, 1),
                'dateFin': None
            },
            # Lucas Petit
            {
                'candidat': candidats['lpetit'],
                'poste': 'Stagiaire Développement Web',
                'entreprise': 'SoftOuest Nantes',
                'description': 'Participation à la maintenance applicative d\'un portail d\'intranet d\'entreprise et rédaction de tests unitaires.',
                'dateDebut': datetime.date(2025, 1, 15),
                'dateFin': datetime.date(2025, 4, 30)
            }
        ]

        for exp in exp_data:
            Experience.objects.get_or_create(
                candidat=exp['candidat'],
                poste=exp['poste'],
                entreprise=exp['entreprise'],
                defaults=exp
            )
        self.stdout.write(f"  - {len(exp_data)} experiences professionnelles enregistrees.")

    def create_candidatures(self, candidats, offres):
        # Associons des offres
        offres_map = {o.titre: o for o in offres}

        candidatures_data = [
            {
                'candidat': candidats['tbernard'],
                'offre': offres_map.get('Développeur Fullstack Django / React'),
                'lettreMotivation': 'Madame, Monsieur,\nTrès motivé par les projets ambitieux de TechNova Solutions, je serais ravi d\'apporter mes compétences en Django et React au sein de votre équipe.',
                'statut': StatutCandidature.ACCEPTEE
            },
            {
                'candidat': candidats['tbernard'],
                'offre': offres_map.get('Développeur Backend Python Senior'),
                'lettreMotivation': 'Passionné par les systèmes distribués et le Clean Architecture sous Python, je souhaite contribuer à vos services bancaires haute performance.',
                'statut': StatutCandidature.EN_ATTENTE
            },
            {
                'candidat': candidats['claurent'],
                'offre': offres_map.get('Data Scientist / Machine Learning Engineer'),
                'lettreMotivation': 'Forte de mon expérience en modélisation prédictive, je suis enthousiaste à l\'idée de rejoindre DataSphere Analytics.',
                'statut': StatutCandidature.EN_ATTENTE
            },
            {
                'candidat': candidats['jmartin'],
                'offre': offres_map.get('Stagiaire Développeur Web Frontend'),
                'lettreMotivation': 'Sensible au numérique durable et à l\'éco-conception, je souhaite participer au développement de vos projets innovants.',
                'statut': StatutCandidature.ACCEPTEE
            },
            {
                'candidat': candidats['jmartin'],
                'offre': offres_map.get('Développeur Web Vue.js & TypeScript'),
                'lettreMotivation': 'Mon profil axé front-end moderne correspond particulièrement aux exigences techniques du poste.',
                'statut': StatutCandidature.EN_ATTENTE
            },
            {
                'candidat': candidats['adiallo'],
                'offre': offres_map.get('Ingénieur DevOps Cloud & Infrastructure'),
                'lettreMotivation': 'Mon parcours me permet de prendre en charge vos environnements conteneurisés et d\'optimiser la chaîne de livraison continue.',
                'statut': StatutCandidature.ACCEPTEE
            },
            {
                'candidat': candidats['adiallo'],
                'offre': offres_map.get('Consultant Sécurité des Systèmes d\'Information & Pentest'),
                'lettreMotivation': 'Intéressée par la sécurité offensive, je postule avec enthousiasme chez CyberShield Protect.',
                'statut': StatutCandidature.REFUSEE
            },
            {
                'candidat': candidats['lpetit'],
                'offre': offres_map.get('Stagiaire Développeur Web Frontend'),
                'lettreMotivation': 'Jeune diplômé dynamique, je souhaite faire mes premiers pas professionnels au sein de GreenDigital Studio.',
                'statut': StatutCandidature.EN_ATTENTE
            }
        ]

        count = 0
        for cand_app in candidatures_data:
            if cand_app['offre']:
                Candidature.objects.get_or_create(
                    candidat=cand_app['candidat'],
                    offre=cand_app['offre'],
                    defaults=cand_app
                )
                count += 1
        self.stdout.write(f"  - {count} candidatures creees.")

    def create_inscriptions(self, candidats, formations):
        formations_map = {f.titre: f for f in formations}

        inscriptions_data = [
            {
                'candidat': candidats['tbernard'],
                'formation': formations_map.get('DevOps Pratique : Docker, Kubernetes & CI/CD'),
                'statut': 'CONFIRMEE'
            },
            {
                'candidat': candidats['claurent'],
                'formation': formations_map.get('Intelligence Artificielle & Machine Learning avec Python'),
                'statut': 'TERMINEE'
            },
            {
                'candidat': candidats['jmartin'],
                'formation': formations_map.get('React 19 & TypeScript Moderne en Entreprise'),
                'statut': 'CONFIRMEE'
            },
            {
                'candidat': candidats['adiallo'],
                'formation': formations_map.get('Maîtriser Django & les APIs REST Avancées'),
                'statut': 'TERMINEE'
            },
            {
                'candidat': candidats['lpetit'],
                'formation': formations_map.get('Maîtriser Django & les APIs REST Avancées'),
                'statut': 'EN ATTENTE'
            },
            {
                'candidat': candidats['lpetit'],
                'formation': formations_map.get('React 19 & TypeScript Moderne en Entreprise'),
                'statut': 'CONFIRMEE'
            }
        ]

        inscriptions = []
        for insc in inscriptions_data:
            if insc['formation']:
                obj, _ = Inscription.objects.get_or_create(
                    candidat=insc['candidat'],
                    formation=insc['formation'],
                    defaults=insc
                )
                inscriptions.append(obj)

        self.stdout.write(f"  - {len(inscriptions)} inscriptions aux formations creees.")
        return inscriptions

    def create_certifications(self, inscriptions):
        certifs = []
        for insc in inscriptions:
            if insc.statut == 'TERMINEE':
                cert_title = f"Certificat de réussite - {insc.formation.titre}"
                cert, _ = Certification.objects.get_or_create(
                    inscription=insc,
                    defaults={
                        'titre': cert_title,
                        'dateObtention': insc.formation.dateFin,
                    }
                )
                if not cert.fichier:
                    content = f"Certification d'aptitude délivrée à {insc.candidat.prenom} {insc.candidat.nom} pour la formation {insc.formation.titre}".encode('utf-8')
                    cert.fichier.save(f"certif_{insc.candidat.username}_{insc.id}.txt", ContentFile(content), save=True)
                certifs.append(cert)

        self.stdout.write(f"  - {len(certifs)} certifications generees.")

    def create_notifications(self, admin_user, candidats, entreprises, formateurs):
        notifications_data = [
            # Admin
            {
                'user': admin_user,
                'type': 'SYSTEME',
                'message': 'Bienvenue sur la plateforme HirePoint ! Le système est opérationnel et les données de test sont chargées.',
                'lue': False
            },
            # Candidats
            {
                'user': candidats['tbernard'],
                'type': 'CANDIDATURE',
                'message': 'Bonne nouvelle ! Votre candidature pour le poste "Développeur Fullstack Django / React" chez TechNova Solutions a été ACCEPTÉE.',
                'lue': False
            },
            {
                'user': candidats['tbernard'],
                'type': 'FORMATION',
                'message': 'Votre inscription à la formation "DevOps Pratique : Docker, Kubernetes & CI/CD" a été confirmée.',
                'lue': True
            },
            {
                'user': candidats['claurent'],
                'type': 'FORMATION',
                'message': 'Félicitations ! Votre certificat pour la formation "Intelligence Artificielle & Machine Learning" est désormais disponible.',
                'lue': False
            },
            {
                'user': candidats['adiallo'],
                'type': 'CANDIDATURE',
                'message': 'Votre candidature pour le poste "Ingénieur DevOps Cloud & Infrastructure" a été validée par TechNova Solutions.',
                'lue': False
            },
            {
                'user': candidats['jmartin'],
                'type': 'CANDIDATURE',
                'message': 'GreenDigital Studio a accepté votre candidature pour le poste de Stagiaire Frontend !',
                'lue': False
            },
            # Entreprises
            {
                'user': entreprises['technova'],
                'type': 'CANDIDATURE',
                'message': 'Vous avez reçu une nouvelle candidature de Thomas Bernard pour le poste "Développeur Fullstack Django / React".',
                'lue': True
            },
            {
                'user': entreprises['fintech_horizon'],
                'type': 'CANDIDATURE',
                'message': 'Nouvelle candidature en attente d\'examen pour le poste "Développeur Backend Python Senior".',
                'lue': False
            },
            {
                'user': entreprises['datasphere'],
                'type': 'CANDIDATURE',
                'message': 'Camille Laurent a postulé à votre offre "Data Scientist / Machine Learning Engineer".',
                'lue': False
            },
            # Formateurs
            {
                'user': formateurs['mdupont'],
                'type': 'FORMATION',
                'message': 'Un nouveau participant (Lucas Petit) s\'est inscrit à votre session "Maîtriser Django & les APIs REST".',
                'lue': False
            },
            {
                'user': formateurs['sbenali'],
                'type': 'FORMATION',
                'message': 'Votre formation "React 19 & TypeScript Moderne" compte 2 nouvelles inscriptions validées.',
                'lue': False
            }
        ]

        for notif in notifications_data:
            Notification.objects.get_or_create(
                user=notif['user'],
                message=notif['message'],
                defaults=notif
            )

        self.stdout.write(f"  - {len(notifications_data)} notifications envoyees.")

    def print_summary(self):
        models = [
            User, Candidat, Entreprise, Formateur, Competence,
            Offre, Formation, Candidature, Inscription,
            Certification, CV, Diplome, Experience, Notification
        ]
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(" BILAN DU CONTENU DE LA BASE DE DONNEES ")
        self.stdout.write("=" * 50)
        for m in models:
            self.stdout.write(f"  {m.__name__:<18}: {m.objects.count()} enregistrements")
        self.stdout.write("=" * 50)
        self.stdout.write("Identifiants par defaut :")
        self.stdout.write("  - Super Admin : admin / admin123")
        self.stdout.write("  - Utilisateurs: [username] / password123")
        self.stdout.write("=" * 50 + "\n")
