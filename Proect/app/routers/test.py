
from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from fastapi.responses import HTMLResponse, RedirectResponse
from app import database,  models
from app.services import timer, scorer, results_saver


router = APIRouter(prefix="/test",tags=["test"])
templates = Jinja2Templates(directory="app/templates")

questions = [{
    "id":1,
    "text": "Что такое EDA (Exploratory Data Analysis) в работе аналитика данных?",
    "options": {"A": "Метод шифрования данных перед анализом", "B": "Процесс визуализации готовых отчётов для руководства",
                "C":"Исследовательский анализ данных для поиска закономерностей, аномалий и проверки гипотез",
                "D": "Способ сжатия больших массивов данных"
                },
    "correct": "C"},{
    "id":2,
    "text": "Какой инструмент чаще всего используют аналитики данных для выполнения сложных запросов к базам данных?",
    "options": {"A": "Microsoft Excel", "B": "SQL (Structured Query Language)",
                "C":"Python (только для машинного обучения)", "D": "HTML"},
    "correct": "B"},
    {"id":3,
    "text": "Что из перечисленного является примером задачи описательной аналитики (descriptive analytics)?",
    "options": {"A": "Прогнозирование продаж на следующий месяц",
                "B": " Составление отчёта «Суммарная выручка по регионам за прошлый квартал»",
                "C":"Определение оптимальной цены товара",
                "D": "Рекомендация товаров пользователю на основе покупок"},
    "correct": "B"},
    {"id":4,
    "text": "Какая библиотека Python является стандартом для манипуляции табличными данными и их анализа?",
    "options": {"A": "Matplotlib", "B": "Pandas", "C":"Scikit-learn", "D": "NumPy (только для массивов)"},
    "correct": "B"},
    {"id":5,
    "text": "Что из перечисленного относится к этапу «очистка данных» (data cleaning)?",
    "options": {"A": "Построение столбчатой диаграммы", "B": "Обучение модели линейной регрессии",
                "C":"Замена пропущенных значений на среднее или медиану",
                "D": "Написание SQL-запроса для выборки данных"},
    "correct": "C"},
    {"id":6,
    "text": "Какой тип диаграммы лучше всего подходит для демонстрации распределения одной числовой переменной (например, возраста клиентов)?",
    "options": {"A": "Круговая диаграмма", "B": "Линейный график", "C":" Гистограмма (или ящик с усами – boxplot)",
                "D": "Точечная диаграмма (scatter plot)"},
    "correct": "C"},
    {"id":7,
    "text": "Что такое «ложная корреляция» (spurious correlation) в анализе данных?",
    "options": {"A": " Корреляция, которая подтверждена p-value < 0.05",
                "B": "Статистически значимая связь между двумя переменными, которая не имеет причинно-следственной основы и возникает случайно",
                "C":" Коэффициент корреляции Пирсона больше 0.9", "D": " Отсутствие какой-либо связи между данными"},
    "correct": "B"},{
    "id":8,
    "text": "Какой из перечисленных методов относится к предсказательной аналитике (predictive analytics)?",
    "options": {"A": "Построение отчёта по продажам за прошлый год",
                "B": "Группировка клиентов по полу и возрасту", "C":"Обучение модели для прогноза оттока пользователей",
                "D": "Визуализация текущих показателей на дашборде"},
    "correct": "C"},
    {"id":9,
    "text": "Какая мера центральной тенденции наиболее устойчива к выбросам (экстремальным значениям)?",
    "options": {"A": "Среднее арифметическое",
                "B": "Медиана",
                "C": "Мода","D": "Дисперсия" },
    "correct": "B"},
    {"id":10,
    "text": "Что такое «дашборд» (dashboard) в контексте аналитики данных?",
    "options": {"A": "Интерактивная панель с ключевыми метриками и визуализациями в реальном времени",
                "B": "Нерабочая область на экране компьютера",
                "C":"Текстовый отчёт объёмом 100+ страниц",
                "D": "Программный код для сбора данных"},
    "correct": "A"}
]


@router.get("/", response_class=HTMLResponse)
async def show_test(request: Request, db: Session = Depends(database.get_db)):
    token =request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/auth/login", status_code=303)
    if token.startswith("Bearer "):
        token = token[7:]
    #user = await auth.get_current_user(token, db)
    #if not user:
        #return RedirectResponse(url="/auth/login", status_code=303)
    try:
        from app.auth import SECRET_KEY, ALGORITHM
        from jose import jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            return RedirectResponse(url="/auth/login", status_code=303)
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user:
            return RedirectResponse(url="/auth/login", status_code=303)
    except Exception:
        return RedirectResponse(url="/auth/login", status_code=303)
    session = timer.start_new_session(db, user.id)
    start_time = session.started_at.isoformat()
    return templates.TemplateResponse("test.html",
                                      {"request": request,
                                       "questions": questions,
                                       "start_time": start_time,
                                       "duration_minutes": timer.TEST_DURATION_MINUTES})

@router.post("/", response_class=HTMLResponse)
async def submit_test(request: Request, db: Session = Depends(database.get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/auth/login", status_code=303)
    if token.startswith("Bearer "):
        token = token[7:]
    try:
        from app.auth import SECRET_KEY, ALGORITHM
        from jose import jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            return RedirectResponse(url="/auth/login", status_code=303)
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user:
            return RedirectResponse(url="/auth/login", status_code=303)
    except Exception:
        return RedirectResponse(url="/auth/login", status_code=303)

    #проверка таймера
    if not timer.is_session_valid(db, user.id):
        return templates.TemplateResponse("result.html",{
            "request": request,
            "error": "Время теста истекло (20 минут). Попробуйте пройти тест занаво.",
            "correct_count": None,
            "total": len(questions),
            "advice": "",
            "resources": [],
            "detailed_result": []
        })
    form = await request.form()
    user_answers = {}
    for key, value in form.items():
        if key.startswith('q'):
            qid = int(key[1:])  # 'q1' -> 1
            user_answers[qid] = value
    correct_count = 0
    for q in questions:
        qid =q["id"]
        if str(user_answers.get(qid)) == q["correct"]:
            correct_count += 1
    advice, resources = scorer.get_advice_and_resources(correct_count, len(questions))
    results_saver.save_attempt(db, user.id, correct_count, len(questions), advice)
    timer.complete_session(db, user.id)
    detailed_result = []
    for q in questions:
        qid = q["id"]
        user_ans = user_answers.get(qid, "")
        correct_text = q["options"].get(q["correct"], "")
        user_ans_text = q["options"].get(user_ans, "Не выбрано")
        detailed_result.append({
            "text": q["text"],
            "user_choice_text": user_ans_text,
            "correct_answer_text": correct_text,
            "is_correct": (user_ans == q["correct"])
        })
    return templates.TemplateResponse("result.html",{
            "request": request,
            "correct_count": correct_count,
            "total": len(questions),
            "advice": advice,
            "resources": resources,
            "detailed_result": detailed_result
        })
