from django import template

register = template.Library()

censor_list = ['Казино',
               'Деньги',
               'Займы',
               'Мат'
]

@register.filter()
def censor_start(text):
    for bad_word in censor_list:
        if bad_word in censor_list:
            text = text.replace(bad_word, '*' * len(bad_word))
    return text
