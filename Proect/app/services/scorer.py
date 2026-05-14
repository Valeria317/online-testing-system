def get_advice_and_resources(correct_count: int, total: int = 10):
    if correct_count <= 3:
        advice = "Нужно подтянуть знания.Не расстраивайтесь! Вот несколько хороших ресурсов для старта:"
        resources = [
            {"name": "📘 SQL для начинающих (Stepik)", "url": "https://stepik.org/course/63054"},
            {"name": "🐼 Pandas за 10 минут (официальная документация)",
             "url": "https://pandas.pydata.org/pandas-docs/stable/user_guide/10min.html"},
            {"name": "📊 Визуализация данных с Matplotlib", "url": "https://matplotlib.org/stable/tutorials/index.html"}
        ]
    elif  4 <= correct_count <= 8:
        advice = "Неплохо! Вы уже владеете основами.Сосредоточтесь на вопросах, где ошиблись, и углубитесь в статистику и предсказательную аналитику."
        resources = []
    else:
        advice = "Отлично! Вы прекрасно разбираетесь в аналитике данных. Так держать!"
        resources = []
    return advice, resources