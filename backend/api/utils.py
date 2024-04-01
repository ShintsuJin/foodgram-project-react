from django.shortcuts import HttpResponse
from django.db.models import Sum

from recipes.models import IngredientRecipe


def txt_generation(value_list):
    # Аннотация queryset с суммой количества ингредиентов
    queryset = IngredientRecipe.objects.filter(
        id__in=[item[0] for item in value_list]
    ).values('ingredient__name', 'ingredient__measurement_unit').annotate(
        total_amount=Sum('amount')
    )

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

    # final_list = {}
    # for item in value_list:
    #     name = item[0]
    #     if name not in final_list:
    #         final_list[name] = {
    #             'measurement_unit': item[1],
    #             'amount': item[2]
    #         }
    #     else:
    #         final_list[name]['amount'] += item[2]
    #
    # # Создание текстового файла
    # response = HttpResponse(content_type='text/plain')
    # response['Content-Disposition'] = (
    #     'attachment; '
    #     'filename="shopping_list.txt"'
    # )
    #
    # # Запись данных в текстовый файл
    # response.write('Список ингредиентов\n\n')
    # for i, (name, data) in enumerate(final_list.items(), 1):
    #     response.write(
    #         f'<{i}> {name} - {data["amount"]},'
    #         f' {data["measurement_unit"]}\n')
    #
    # return response
