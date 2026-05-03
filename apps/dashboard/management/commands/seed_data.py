"""
Seed the database with realistic sample data.

Usage:
    python manage.py seed_data
    python manage.py seed_data --clear   # wipe and re-seed
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Populate the database with sample data for development/demo.'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data first')

    def handle(self, *args, **options):
        if options['clear']:
            self._clear()

        self.stdout.write('[*] Seeding HEALTHAPP database...\n')
        self._create_admin()
        doctors  = self._create_doctors()
        labs     = self._create_labs()
        pharmas  = self._create_pharmacists()
        patients = self._create_patients()
        self._create_requests(patients, doctors, labs, pharmas)
        self._create_conversations(patients, doctors, pharmas)
        self._create_medications(patients)
        self.stdout.write(self.style.SUCCESS('\n[OK] Seed complete!\n'))
        self.stdout.write('  Admin login: admin@healthapp.local / Admin1234!\n')
        self.stdout.write('  Patient:     patient1@healthapp.local / Patient1234!\n')
        self.stdout.write('  Doctor:      dr.smith@healthapp.local / Doctor1234!\n')

    # ── helpers ──────────────────────────────────────────────────────

    def _clear(self):
        from apps.accounts.models import User
        User.objects.exclude(email='').delete()
        self.stdout.write('  Cleared existing users.\n')

    def _make_user(self, email, password, role, first, last, phone, address,
                   approve=True, **extra):
        from apps.accounts.models import User, Role
        if User.objects.filter(email=email).exists():
            return User.objects.get(email=email)
        u = User.objects.create_user(
            email=email, password=password, role=role,
            first_name=first, last_name=last,
            phone=phone, address=address,
            is_approved=approve, is_email_verified=True,
            **extra,
        )
        return u

    # ── admin ────────────────────────────────────────────────────────

    def _create_admin(self):
        from apps.accounts.models import Role
        u = self._make_user(
            'admin@healthapp.local', 'Admin1234!', Role.ADMIN,
            'Admin', 'HEALTHAPP', '+1-800-000-0000', '1 Admin Plaza',
            approve=True,
        )
        u.is_staff = True
        u.is_superuser = True
        u.save()
        self.stdout.write('  [+] Admin created')

    # ── doctors ──────────────────────────────────────────────────────

    def _create_doctors(self):
        from apps.accounts.models import Role
        from apps.doctors.models import DoctorProfile
        data = [
            ('dr.smith@healthapp.local',   'James',   'Smith',   'Cardiology',       'LIC-DR-001', 15, 80, 120),
            ('dr.chen@healthapp.local',    'Li',      'Chen',    'General Practice', 'LIC-DR-002',  8, 50,  90),
            ('dr.garcia@healthapp.local',  'Maria',   'Garcia',  'Pediatrics',       'LIC-DR-003', 12, 60, 100),
            ('dr.johnson@healthapp.local', 'Robert',  'Johnson', 'Neurology',        'LIC-DR-004', 20, 90, 150),
            ('dr.patel@healthapp.local',   'Priya',   'Patel',   'Dermatology',      'LIC-DR-005',  6, 55,  85),
        ]
        doctors = []
        for email, first, last, spec, lic, exp, cfee, hfee in data:
            u = self._make_user(
                email, 'Doctor1234!', Role.DOCTOR,
                first, last, '+1-555-01' + lic[-2:],
                f'{random.randint(1,999)} Medical Ave',
            )
            profile, _ = DoctorProfile.objects.get_or_create(
                user=u,
                defaults=dict(
                    specialty=spec, license_number=lic,
                    years_of_experience=exp,
                    consultation_fee=cfee, home_visit_fee=hfee,
                    is_available=True, rating_avg=round(random.uniform(3.8, 5.0), 1),
                    rating_count=random.randint(5, 120),
                    bio=f'Board-certified {spec} specialist with {exp} years of clinical experience.',
                ),
            )
            doctors.append(profile)
        self.stdout.write(f'  [+] {len(doctors)} doctors created')
        return doctors

    # ── labs ─────────────────────────────────────────────────────────

    def _create_labs(self):
        from apps.accounts.models import Role
        from apps.labs.models import LabProfile
        data = [
            ('lab.central@healthapp.local', 'Central', 'Labs',    'CentralLab',   'LIC-LAB-001', 45),
            ('lab.biotest@healthapp.local',  'Bio',     'Testing', 'BioTest Labs', 'LIC-LAB-002', 35),
        ]
        labs = []
        for email, first, last, labname, lic, fee in data:
            u = self._make_user(
                email, 'Lab1234!', Role.LAB,
                first, last, '+1-555-020' + lic[-1:],
                f'{random.randint(1,99)} Lab Street',
            )
            profile, _ = LabProfile.objects.get_or_create(
                user=u,
                defaults=dict(
                    lab_name=labname, license_number=lic,
                    services_offered='CBC Glucose Lipid-Panel HbA1c Thyroid Urine-Analysis',
                    home_visit_fee=fee, is_available=True,
                    rating_avg=round(random.uniform(3.9, 5.0), 1),
                    rating_count=random.randint(10, 80),
                ),
            )
            labs.append(profile)
        self.stdout.write(f'  [+] {len(labs)} labs created')
        return labs

    # ── pharmacists ──────────────────────────────────────────────────

    def _create_pharmacists(self):
        from apps.accounts.models import Role
        from apps.pharmacy.models import PharmacistProfile, PharmacyProduct
        data = [
            ('pharma.medplus@healthapp.local',  'Med',   'Plus',  'MedPlus Pharmacy',   'LIC-PH-001', 5),
            ('pharma.quickrx@healthapp.local',  'Quick', 'Rx',    'QuickRx Pharmacy',   'LIC-PH-002', 0),
        ]
        pharmas = []
        for email, first, last, pname, lic, dfee in data:
            u = self._make_user(
                email, 'Pharma1234!', Role.PHARMACIST,
                first, last, '+1-555-030' + lic[-1:],
                f'{random.randint(1,99)} Pharmacy Blvd',
            )
            profile, created = PharmacistProfile.objects.get_or_create(
                user=u,
                defaults=dict(
                    pharmacy_name=pname, license_number=lic,
                    delivery_fee=dfee, is_open=True,
                    rating_avg=round(random.uniform(3.7, 5.0), 1),
                    rating_count=random.randint(20, 200),
                ),
            )
            if created:
                products = [
                    ('Metformin 500mg', 'Diabetes management', 12.99, False),
                    ('Atorvastatin 20mg', 'Cholesterol control', 18.50, True),
                    ('Lisinopril 10mg', 'Blood pressure medication', 9.99, True),
                    ('Vitamin D3 2000IU', 'Vitamin supplement', 7.49, False),
                    ('Amoxicillin 500mg', 'Antibiotic — prescription required', 14.00, True),
                    ('Paracetamol 500mg', 'Pain and fever relief', 4.99, False),
                    ('Omeprazole 20mg', 'Acid reflux treatment', 11.25, True),
                    ('Cetirizine 10mg', 'Antihistamine / allergy', 6.99, False),
                ]
                for name, desc, price, rx in products:
                    PharmacyProduct.objects.create(
                        pharmacy=profile, name=name, description=desc,
                        price=price, in_stock=True, requires_prescription=rx,
                    )
            pharmas.append(profile)
        self.stdout.write(f'  [+] {len(pharmas)} pharmacists + products created')
        return pharmas

    # ── patients ─────────────────────────────────────────────────────

    def _create_patients(self):
        from apps.accounts.models import Role
        from apps.patients.models import PatientProfile, BloodGroup
        data = [
            ('patient1@healthapp.local',  'Alice',  'Martin',  date(1990, 3, 15), 'Paris',      'A+'),
            ('patient2@healthapp.local',  'Bob',    'Williams', date(1978, 7, 22), 'Lyon',       'O-'),
            ('patient3@healthapp.local',  'Claire', 'Dubois',  date(2000, 11, 8), 'Marseille',  'B+'),
            ('patient4@healthapp.local',  'David',  'Bernard', date(1965, 1, 30), 'Bordeaux',   'AB+'),
            ('patient5@healthapp.local',  'Emma',   'Petit',   date(1995, 6, 19), 'Nice',       'O+'),
        ]
        patients = []
        for email, first, last, dob, pob, bg in data:
            u = self._make_user(
                email, 'Patient1234!', Role.PATIENT,
                first, last, '+33-6-' + str(random.randint(10000000, 99999999)),
                f'{random.randint(1,100)} Rue de la Santé',
            )
            profile, _ = PatientProfile.objects.get_or_create(
                user=u,
                defaults=dict(
                    date_of_birth=dob, place_of_birth=pob,
                    blood_group=bg,
                    emergency_contact_name=f'{first} Emergency Contact',
                    emergency_contact_phone='+33-6-00000001',
                ),
            )
            patients.append(profile)
        self.stdout.write(f'  [+] {len(patients)} patients created')
        return patients

    # ── service requests ─────────────────────────────────────────────

    def _create_requests(self, patients, doctors, labs, pharmas):
        from apps.services.models import ServiceRequest, ServiceType, RequestStatus, Urgency
        samples = [
            (ServiceType.DOCTOR_HOME,    'Fever and headache check-up',     RequestStatus.COMPLETED, Urgency.NORMAL),
            (ServiceType.LAB_HOME,       'Blood panel CBC + lipid profile',  RequestStatus.ACCEPTED,  Urgency.NORMAL),
            (ServiceType.PHARMACY_ORDER, 'Monthly insulin refill',           RequestStatus.IN_PROGRESS, Urgency.HIGH),
            (ServiceType.CONSULTATION,   'Allergy symptoms follow-up',       RequestStatus.COMPLETED, Urgency.LOW),
            (ServiceType.DOCTOR_HOME,    'Back pain evaluation',             RequestStatus.PENDING,   Urgency.NORMAL),
            (ServiceType.LAB_HOME,       'Thyroid function test',            RequestStatus.PENDING,   Urgency.LOW),
            (ServiceType.PHARMACY_ORDER, 'Blood pressure medication delivery', RequestStatus.COMPLETED, Urgency.NORMAL),
            (ServiceType.CONSULTATION,   'Skin rash — need advice',          RequestStatus.ACCEPTED,  Urgency.HIGH),
            (ServiceType.DOCTOR_HOME,    'Post-surgery follow-up visit',     RequestStatus.COMPLETED, Urgency.HIGH),
            (ServiceType.LAB_HOME,       'HbA1c and glucose test',           RequestStatus.PENDING,   Urgency.NORMAL),
        ]
        created = 0
        for i, (stype, title, status, urgency) in enumerate(samples):
            patient = patients[i % len(patients)]
            provider_user = None
            if status != RequestStatus.PENDING:
                if stype == ServiceType.DOCTOR_HOME or stype == ServiceType.CONSULTATION:
                    provider_user = doctors[i % len(doctors)].user
                elif stype == ServiceType.LAB_HOME:
                    provider_user = labs[i % len(labs)].user
                elif stype == ServiceType.PHARMACY_ORDER:
                    provider_user = pharmas[i % len(pharmas)].user

            days_ago = random.randint(1, 30)
            sr = ServiceRequest.objects.create(
                patient=patient.user,
                provider=provider_user,
                service_type=stype,
                status=status,
                urgency=urgency,
                title=title,
                description=f'Sample request: {title}. Patient requires prompt service.',
                address=patient.user.address or '123 Sample Street',
                preferred_datetime=timezone.now() + timedelta(hours=random.randint(2, 72)),
                estimated_cost=round(random.uniform(40, 200), 2),
                created_at=timezone.now() - timedelta(days=days_ago),
            )
            if status == RequestStatus.COMPLETED:
                sr.completed_at = timezone.now() - timedelta(days=random.randint(1, days_ago))
                sr.final_cost = round(float(sr.estimated_cost) * random.uniform(0.9, 1.1), 2)
                sr.save()
            created += 1
        self.stdout.write(f'  [+] {created} service requests created')

    # ── chat conversations ────────────────────────────────────────────

    def _create_conversations(self, patients, doctors, pharmas):
        from apps.chat.models import Conversation, ChatMessage
        pairs = [
            (patients[0].user, doctors[0].user,  [
                ('Hello Doctor, I have had a fever for 2 days.',       False),
                ('Hello Alice! How high is your temperature?',          True),
                ('Around 38.5°C. Should I be worried?',                False),
                ('Monitor it closely. Take paracetamol if needed.',     True),
            ]),
            (patients[1].user, pharmas[0].user,  [
                ('I need a refill of my Metformin 500mg.',              False),
                ('Of course! How many boxes do you need?',              True),
                ('Two boxes please. Can you deliver today?',            False),
                ('Yes, delivery in 2-3 hours. Confirmed!',             True),
            ]),
            (patients[2].user, doctors[1].user,  [
                ('Dr. Chen, I have a question about my test results.',  False),
                ('Of course Claire, go ahead.',                         True),
                ('My glucose was 6.4 mmol/L. Is that okay?',           False),
                ('Slightly elevated. Let us schedule a follow-up.',    True),
            ]),
        ]
        for p_user, prov_user, messages in pairs:
            from django.db.models import Count
            existing = (Conversation.objects
                        .filter(participants=p_user)
                        .filter(participants=prov_user)
                        .annotate(c=Count('participants'))
                        .filter(c=2).first())
            if existing:
                continue
            convo = Conversation.objects.create()
            convo.participants.add(p_user, prov_user)
            for body, from_provider in messages:
                sender = prov_user if from_provider else p_user
                ChatMessage.objects.create(conversation=convo, sender=sender, body=body)
            convo.last_message_at = timezone.now()
            convo.save()
        self.stdout.write('  [+] Sample conversations created')

    # ── medication reminders ──────────────────────────────────────────

    def _create_medications(self, patients):
        from apps.patients.models import MedicationReminder
        meds_data = [
            ('Metformin',     '500mg',   'twice',  0),
            ('Atorvastatin',  '20mg',    'once',   1),
            ('Vitamin D3',    '2000 IU', 'once',   0),
            ('Lisinopril',    '10mg',    'once',   2),
            ('Omeprazole',    '20mg',    'once',   1),
        ]
        count = 0
        for i, med in enumerate(meds_data):
            name, dosage, freq, p_idx = med
            patient = patients[p_idx % len(patients)]
            if MedicationReminder.objects.filter(patient=patient, medication_name=name).exists():
                continue
            MedicationReminder.objects.create(
                patient=patient,
                medication_name=name,
                dosage=dosage,
                frequency=freq,
                start_date=date.today(),
                next_dose_at=timezone.now() + timedelta(hours=random.randint(1, 12)),
                is_active=True,
            )
            count += 1
        self.stdout.write(f'  [+] {count} medication reminders created')
