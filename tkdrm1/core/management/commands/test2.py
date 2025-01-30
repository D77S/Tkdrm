from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """."""

    def handle(self, *args, **options):
        """."""
        IN = (('1', 'АПП'), ('2', 'ВПП'), ('3', 'ЖДПП'),
              ('4', 'МПП'), ('5', 'ППП'), ('6', 'РПП'),
              ('7', 'СПП'))

        print(f'IN={IN}')

        OUT_1 = [i for i in range(0, len(IN)) if IN[i][1] == 'ВПП'][0]
        OUT_1 += 1

        OUT_2 = [i for i, item in enumerate(IN, start=1) if item[1] == 'ВПП'][0]  # noqa

        print(f'OUT_1={OUT_1}')
        print(f'OUT_2={OUT_2}')
