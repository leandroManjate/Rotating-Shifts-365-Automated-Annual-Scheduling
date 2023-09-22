from flask import Flask, request, render_template
import pandas as pd
from datetime import datetime, timedelta
from datetime import date

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index11.html')

@app.route('/schedule', methods=['POST'])
def schedule():
    num_workers = int(request.form.get('num_workers', 18))

    num_workers_morning = int(request.form.get('num_workers_morning', 6))
    num_workers_afternoon = int(request.form.get('num_workers_afternoon', 6))
    num_workers_night = int(request.form.get('num_workers_night', 6))

    num_shifts_day = int(request.form.get('num_shifts_day', 3))
    num_days_year = int(request.form.get('num_days_year', 365))
    start_date_str = request.form.get('start_date', date.today().isoformat())
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()

    if num_workers < num_shifts_day:
        return "Not enough workers for each shift", 400
    
    if num_workers != (num_workers_morning + num_workers_afternoon + num_workers_night):
        return "The sum of workers in each shift must equal the total number of workers", 400


    df_shifts = pd.DataFrame()
    df_hours = pd.DataFrame()
    df_weekly_hours = pd.DataFrame()
    df_work_days = pd.DataFrame()
    df_days_off = pd.DataFrame()
    df_sundays_off = pd.DataFrame()

    if num_workers != (num_workers_morning + num_workers_afternoon + num_workers_night):
        return "The sum of workers in each shift must equal the total number of workers", 400


    for worker in range(num_workers):

        if worker < num_workers_morning:
            worker_shift_type = 'morning'
            cycle_length = 6   # 4 work + 2 off
        elif worker < (num_workers_morning + num_workers_afternoon):
            worker_shift_type = 'afternoon'
            cycle_length = 6  # 4 work + 2 off

        else:
            worker_shift_type = 'night'
            cycle_length = 5  # 3 work + 2 off



        worker_shifts = []
        worker_hours = []
        worker_weekly_hours = []
        worker_work_days = []
        worker_days_off = []
        worker_sundays_off = []
        weekly_hours = 0
        for day in range(num_days_year):
            cycle_day = (day + worker * 4) % cycle_length  # now the cycle lasts 19 days
            current_date = start_date + timedelta(days=day)
            is_sunday = current_date.weekday() == 6  # 6 = Sunday

            is_day_off = False  # Inicializando is_day_off antes dos blocos condicionais

            if worker_shift_type == 'morning' or worker_shift_type == 'afternoon':
                if  0 <= cycle_day < 4:  # Morning shift
                    shift = 0 if worker_shift_type == 'morning' else 1# Morning shift
                else:
                    shift = -1  # Day off
                    is_day_off = True
                

            elif worker_shift_type == 'night':
                
                if 0 <= cycle_day < 3:
                    shift = 2
                else:
                    shift = -1  # Day off
                    is_day_off = cycle_day >= 3
                    is_day_off = True

                    
            
            is_work_day = not is_day_off


            worker_shifts.append(shift)
            worker_hours.append(8 if is_work_day else 0)
            worker_work_days.append(1 if is_work_day else 0)
            worker_days_off.append(1 if is_day_off else 0)
            worker_sundays_off.append(1 if is_day_off and is_sunday else 0)  # Mark if it's an off day and also Sunday

            weekly_hours += 8 if is_work_day else 0

            if day % 7 == 6:  # End of the week
                worker_weekly_hours.append(weekly_hours)
                weekly_hours = 0

        df_shifts[f'Trabalhador {worker+1}'] = worker_shifts
        df_hours[f'Trabalhador {worker+1}'] = worker_hours
        df_weekly_hours[f'Trabalhador {worker+1}'] = worker_weekly_hours
        df_work_days[f'Trabalhador {worker+1}'] = worker_work_days
        df_days_off[f'Trabalhador {worker+1}'] = worker_days_off
        df_sundays_off[f'Trabalhador {worker+1}'] = worker_sundays_off

    df_shifts = df_shifts.replace({0: 'Manhã', 1: 'Tarde', 2: 'Noite', -1: 'Folga'})

    date_range = pd.date_range(start=start_date, periods=num_days_year)
    df_shifts.index = date_range
    df_hours.index = date_range
    df_work_days.index = date_range
    df_days_off.index = date_range
    df_sundays_off.index = date_range

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
        df_hours.T.to_excel(writer, sheet_name='Horas Diárias')
        df_weekly_hours.T.to_excel(writer, sheet_name='Horas Semanais')
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
