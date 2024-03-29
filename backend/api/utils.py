from django.shortcuts import HttpResponse


def txt_generation(value_list):
    final_list = {}
    for item in value_list:
        name = item[0]
        if name not in final_list:
            final_list[name] = {
                'measurement_unit': item[1],
                'amount': item[2]
            }
        else:
            final_list[name]['amount'] += item[2]

    # Создание текстового файла
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = (
        'attachment; '
        'filename="shopping_list.txt"'
    )

    # Запись данных в текстовый файл
    response.write('Список ингредиентов\n\n')
    for i, (name, data) in enumerate(final_list.items(), 1):
        response.write(
            f'<{i}> {name} - {data["amount"]},'
            f' {data["measurement_unit"]}\n')

    return response
