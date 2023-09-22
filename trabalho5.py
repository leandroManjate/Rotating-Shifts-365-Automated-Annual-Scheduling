from flask import Flask, request, render_template
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from datetime import date


app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index5.html')

@app.route('/schedule', methods=['POST'])
def schedule():
    num_workers = int(request.form.get('num_workers', 18))
    num_shifts_day = int(request.form.get('num_shifts_day', 3))
    num_days_year = int(request.form.get('num_days_year', 365))
    start_date_str = request.form.get('start_date', date.today().isoformat())
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

    workers_per_shift = num_workers // num_shifts_day

    df_shifts = pd.DataFrame()
    df_hours = pd.DataFrame()
    df_weekly_hours = pd.DataFrame()

    for worker in range(num_workers):
        worker_shifts = []
        worker_hours = []
        worker_weekly_hours = []
        weekly_hours = 0
        for day in range(num_days_year):
            shift = (worker // workers_per_shift + day // 7) % num_shifts_day
            if day % 7 not in [(worker + 5) % 7, (worker + 6) % 7]:
                worker_shifts.append(shift)
                worker_hours.append(8)
                weekly_hours += 8
            else:
                worker_shifts.append(-1)
                worker_hours.append(0)

            if day % 7 == 6:
                worker_weekly_hours.append(weekly_hours)
                weekly_hours = 0

        df_shifts[f'Trabalhador {worker+1}'] = worker_shifts
        df_hours[f'Trabalhador {worker+1}'] = worker_hours
        df_weekly_hours[f'Trabalhador {worker+1}'] = worker_weekly_hours

    df_shifts = df_shifts.replace({0: 'Manhã', 1: 'Tarde', 2: 'Noite', -1: 'Folga'})

    date_range = [start_date + timedelta(days=day) for day in range(num_days_year)]
    df_shifts.index = date_range
    df_hours.index = date_range

    with pd.ExcelWriter('schedule.xlsx') as writer:
        df_shifts.to_excel(writer, sheet_name='Turnos')
        df_hours.to_excel(writer, sheet_name='Horas Diárias')
        df_weekly_hours.to_excel(writer, sheet_name='Horas Semanais')

    return "Schedule created successfully"

if __name__ == "__main__":
    app.debug = True
    app.run()
