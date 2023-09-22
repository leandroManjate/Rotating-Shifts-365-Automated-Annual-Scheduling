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
    num_days_year = int(request.form.get('num_days_year', 365))
    start_date_str = request.form.get('start_date', date.today().isoformat())
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

    if num_workers < 3:
        return "Not enough workers for each shift", 400

    df_shifts = pd.DataFrame()
    df_work_days = pd.DataFrame()
    df_days_off = pd.DataFrame()
    df_sundays_off = pd.DataFrame()

    for worker in range(num_workers):
        worker_shifts = []
        worker_work_days = []
        worker_days_off = []
        worker_sundays_off = []
        for day in range(num_days_year):
            cycle_day = (day + worker * 5) % 17
            if cycle_day < 4:  # Morning shift
                shift = 0
                work_day = 1
                day_off = 0
                sunday_off = 0
            elif 4 <= cycle_day < 6:  # Day off
                shift = -1
                work_day = 0
                day_off = 1
                sunday_off = 0
            elif 6 <= cycle_day < 10:  # Afternoon shift
                shift = 1
                work_day = 1
                day_off = 0
                sunday_off = 0
            elif 10 <= cycle_day < 12:  # Day off
                shift = -1
                work_day = 0
                day_off = 1
                sunday_off = 0
            elif 12 <= cycle_day < 15:  # Night shift
                shift = 2
                work_day = 1
                day_off = 0
                sunday_off = 0
            else:  # Day off after night shift
                shift = -1
                work_day = 0
                day_off = 1
                sunday_off = 0

            if (start_date + timedelta(days=day)).weekday() == 6 and shift == -1:  # Check if the day off is Sunday
                sunday_off = 1

            worker_shifts.append(shift)
            worker_work_days.append(work_day)
            worker_days_off.append(day_off)
            worker_sundays_off.append(sunday_off)

        df_shifts[f'Trabalhador {worker+1}'] = worker_shifts
        df_work_days[f'Trabalhador {worker+1}'] = worker_work_days
        df_days_off[f'Trabalhador {worker+1}'] = worker_days_off
        df_sundays_off[f'Trabalhador {worker+1}'] = worker_sundays_off

    df_shifts = df_shifts.replace({0: 'Manhã', 1: 'Tarde', 2: 'Noite', -1: 'Folga'})

    date_range = [start_date + timedelta(days=day) for day in range(num_days_year)]
    df_shifts.index = pd.to_datetime(date_range)
    df_work_days.index = pd.to_datetime(date_range)
    df_days_off.index = pd.to_datetime(date_range)
    df_sundays_off.index = pd.to_datetime(date_range)

    # Total for each worker
    df_total_work_days = pd.DataFrame(df_work_days.sum(), columns=['Total Dias Trabalhados'])
    df_total_days_off = pd.DataFrame(df_days_off.sum(), columns=['Total Dias de Folga'])
    df_total_sundays_off = pd.DataFrame(df_sundays_off.sum(), columns=['Total Domingos de Folga'])

    month_map = {1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
                 7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'}

    # Monthly total for each worker
    df_monthly_work_days = df_work_days.resample('M').sum()
    df_monthly_work_days.index = df_monthly_work_days.index.month
    df_monthly_work_days.index = df_monthly_work_days.index.map(month_map)
    df_monthly_days_off = df_days_off.resample('M').sum()
    df_monthly_days_off.index = df_monthly_days_off.index.month
    df_monthly_days_off.index = df_monthly_days_off.index.map(month_map)
    df_monthly_sundays_off = df_sundays_off.resample('M').sum()
    df_monthly_sundays_off.index = df_monthly_sundays_off.index.month
    df_monthly_sundays_off.index = df_monthly_sundays_off.index.map(month_map)

    with pd.ExcelWriter('HorarioEquipa2.xlsx') as writer:
        df_shifts.T.to_excel(writer, sheet_name='Turnos')
        df_work_days.T.to_excel(writer, sheet_name='Dias Trabalhados')
        df_days_off.T.to_excel(writer, sheet_name='Dias de Folga')
        df_total_work_days.to_excel(writer, sheet_name='Total Anual Dias Trabalhados')
        df_total_days_off.to_excel(writer, sheet_name='Total Anual Dias de Folga')
        df_total_sundays_off.to_excel(writer, sheet_name='Total Anual Domingos de Folga')
        df_monthly_work_days.T.to_excel(writer, sheet_name='Total Mensal Dias Trabalhados')
        df_monthly_days_off.T.to_excel(writer, sheet_name='Total Mensal Dias de Folga')
        df_monthly_sundays_off.T.to_excel(writer, sheet_name='Total Mensal Domingos de Folga')

    return "Schedule created successfully"

if __name__ == "__main__":
    app.run(debug=True)
