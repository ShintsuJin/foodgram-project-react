from django.core.management.base import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Create sample tags'

    def handle(self, *args, **options):
        # Создаем образцы тегов
        tags_data = [
            {'name': 'Завтрак', 'color': '#ff0000', 'slug': 'breakfast'},
            {'name': 'Обед', 'color': '#00ff00', 'slug': 'lunch'},
            {'name': 'Ужин', 'color': '#0000ff', 'slug': 'dinner'},
        ]

        # Сохраняем образцы в базе данных
        for tag_data in tags_data:
            Tag.objects.create(**tag_data)

        self.stdout.write(self.style.SUCCESS('Образцы тегов успешно созданы!'))
