from django.db.models import Sum
from django.shortcuts import HttpResponse


def txt_generation(value_list):
    # Аннотация queryset с суммой количества ингредиентов
    queryset = (value_list.values(
        'ingredient__name',
        'ingredient__measurement_unit').annotate(
        total_amount=Sum('amount')))

    # Создание текстового файла
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = (
        'attachment; '
        'filename="shopping_list.txt"'
    )

    # Запись данных в текстовый файл
    response.write('Список ингредиентов\n\n')
    for i, item in enumerate(queryset, 1):
        response.write(
            f'<{i}> {item["ingredient__name"]} - {item["total_amount"]},'
            f' {item["ingredient__measurement_unit"]}\n'
        )
    return response
