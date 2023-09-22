from flask import Flask, request, render_template
import pandas as pd
from datetime import datetime, timedelta
from datetime import date

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index10.html')

@app.route('/schedule', methods=['POST'])
def schedule():
    num_workers = int(request.form.get('num_workers', 18))
    num_shifts_day = int(request.form.get('num_shifts_day', 3))
    num_days_year = int(request.form.get('num_days_year', 365))
    start_date_str = request.form.get('start_date', date.today().isoformat())
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

    if num_workers < num_shifts_day:
        return "Not enough workers for each shift", 400

    df_shifts = pd.DataFrame()
    df_hours = pd.DataFrame()
    df_weekly_hours = pd.DataFrame()
    df_work_days = pd.DataFrame()
    df_days_off = pd.DataFrame()
    df_sundays_off = pd.DataFrame()

    for worker in range(num_workers):
        worker_shifts = []
        worker_hours = []
        worker_weekly_hours = []
        worker_work_days = []
        worker_days_off = []
        worker_sundays_off = []
        weekly_hours = 0
        for day in range(num_days_year):
            cycle_day = (day + worker * 4) % 19  # now the cycle lasts 19 days
            if cycle_day < 4:  # Morning shift
                shift = 0
            elif 4 <= cycle_day < 6 or 10 <= cycle_day < 12:  # Day off
                shift = -1
            elif 6 <= cycle_day < 10:  # Afternoon shift
                shift = 1
            elif 12 <= cycle_day < 16:  # Night shift
                shift = 2
            else:  # Day off after night shift
                shift = -1

            is_day_off = cycle_day in [4, 5, 10, 11, 16, 17, 18]
            is_sunday = (start_date + timedelta(days=day)).weekday() == 6  # 6 = Sunday

            if is_day_off:
                worker_shifts.append(-1)
                worker_hours.append(0)
                worker_work_days.append(0)
                worker_days_off.append(1)
                worker_sundays_off.append(is_sunday)
            else:
                worker_shifts.append(shift)
                worker_hours.append(8)
                worker_work_days.append(1)
                worker_days_off.append(0)
                worker_sundays_off.append(0)
                weekly_hours += 8

            if day % 7 == 6:
                worker_weekly_hours.append(weekly_hours)
                weekly_hours = 0

        df_shifts[f'Trabalhador {worker+1}'] = worker_shifts
        df_hours[f'Trabalhador {worker+1}'] = worker_hours
        df_weekly_hours[f'Trabalhador {worker+1}'] = worker_weekly_hours
        df_work_days[f'Trabalhador {worker+1}'] = worker_work_days
        df_days_off[f'Trabalhador {worker+1}'] = worker_days_off
        df_sundays_off[f'Trabalhador {worker+1}'] = worker_sundays_off

    df_shifts = df_shifts.replace({0: 'Manhã', 1: 'Tarde', 2: 'Noite', -1: 'Folga'})

    date_range = [start_date + timedelta(days=day) for day in range(num_days_year)]
    df_shifts.index = date_range
    df_hours.index = date_range
    df_work_days.index = date_range
    df_days_off.index = date_range
    df_sundays_off.index = date_range

    df_total_work_days = pd.DataFrame(df_work_days.sum(), columns=['Total Dias Trabalhados'])
    df_total_days_off = pd.DataFrame(df_days_off.sum(), columns=['Total Dias de Folga'])
    df_total_sundays_off = pd.DataFrame(df_sundays_off.sum(), columns=['Total Domingos de Folga'])

    with pd.ExcelWriter('schedule.xlsx') as writer:
        df_shifts.T.to_excel(writer, sheet_name='Turnos')
        df_hours.T.to_excel(writer, sheet_name='Horas Diárias')
        df_weekly_hours.T.to_excel(writer, sheet_name='Horas Semanais')
        df_work_days.T.to_excel(writer, sheet_name='Dias Trabalhados')
        df_days_off.T.to_excel(writer, sheet_name='Dias de Folga')
        df_total_work_days.to_excel(writer, sheet_name='Total Anual Dias Trabalhados')
        df_total_days_off.to_excel(writer, sheet_name='Total Anual Dias de Folga')
        df_total_sundays_off.to_excel(writer, sheet_name='Total Anual Domingos de Folga')

    return "Schedule created successfully"

if __name__ == "__main__":
    app.run(debug=True)
