from django.core.management.base import BaseCommand
from procedures.models import Toothcode

PERMANENT = list(range(11, 19)) + list(range(21, 29)) + list(range(31, 39)) + list(range(41, 49))
PRIMARY = list(range(51, 56)) + list(range(61, 66)) + list(range(71, 76)) + list(range(81, 86))

class Command(BaseCommand):
    help = "Seed Toothcode with FDI numbers"

    def handle(self, *args, **options):
        created = 0
        for v in PERMANENT:
            _, c = Toothcode.objects.get_or_create(tooth_number=str(v), tooth_type="permanent")
            created += int(c)
        for v in PRIMARY:
            _, c = Toothcode.objects.get_or_create(tooth_number=str(v), tooth_type="primary")
            created += int(c)
        self.stdout.write(self.style.SUCCESS(f"Toothcodes seeded. New rows: {created}"))