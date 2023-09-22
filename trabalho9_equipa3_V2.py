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

    for worker in range(num_workers):
        worker_shifts = []
        for day in range(num_days_year):
            cycle_day = (day + worker * 9) % 28  # The cycle now lasts 28 days, and each worker starts 9 days apart
            if cycle_day < 6:  # Morning shift
                shift = 0
            elif 6 <= cycle_day < 9:  # Day off
                shift = -1
            elif 9 <= cycle_day < 15:  # Afternoon shift
                shift = 1
            elif 15 <= cycle_day < 18:  # Day off
                shift = -1
            elif 18 <= cycle_day < 24:  # Night shift
                shift = 2
            else:  # Day off after night shift
                shift = -1

            worker_shifts.append(shift)

        df_shifts[f'Trabalhador {worker+1}'] = worker_shifts

    df_shifts = df_shifts.replace({0: 'Manhã', 1: 'Tarde', 2: 'Noite', -1: 'Folga'})

    date_range = [start_date + timedelta(days=day) for day in range(num_days_year)]
    df_shifts.index = date_range

    with pd.ExcelWriter('schedule.xlsx') as writer:
        df_shifts.T.to_excel(writer, sheet_name='Turnos')

    return "Schedule created successfully"

if __name__ == "__main__":
    app.run(debug=True)
