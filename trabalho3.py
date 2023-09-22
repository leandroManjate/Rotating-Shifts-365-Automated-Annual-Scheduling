import numpy as np
import pandas as pd
import calendar
from datetime import date, timedelta

# Number of workers
num_workers = 18

# Number of shifts per day
num_shifts_day = 3

# Number of workers per shift
workers_per_shift = num_workers // num_shifts_day

# Number of days in a year
num_days_year = 365

# Create an empty DataFrame for shifts and hours
df_shifts = pd.DataFrame()
df_hours = pd.DataFrame()

# Assign shifts and hours
for worker in range(num_workers):
    worker_shifts = []
    worker_hours = []
    for day in range(num_days_year):
        # Shift changes every week
        shift = (worker // workers_per_shift + day // 7) % num_shifts_day
        # Workers rest on two days of their weekly cycle, which are staggered for each worker
        if day % 7 not in [(worker + 5) % 7, (worker + 6) % 7]:
            worker_shifts.append(shift)
            worker_hours.append(8)  # 8 hours of work per shift
        else:
            worker_shifts.append(-1)  # -1 indicates a day off
            worker_hours.append(0)  # 0 hours of work on a day off
    df_shifts[f'Trabalhador {worker+1}'] = worker_shifts
    df_hours[f'Trabalhador {worker+1}'] = worker_hours

# Change shift numbers to shift names
df_shifts = df_shifts.replace({0: 'Manhã', 1: 'Tarde', 2: 'Noite', -1: 'Folga'})

# Create a date range for the index
start_date = date.today()
date_range = [start_date + timedelta(days=day) for day in range(num_days_year)]
df_shifts.index = date_range
df_hours.index = date_range

# Save to Excel
with pd.ExcelWriter('schedule.xlsx') as writer:
    df_shifts.to_excel(writer, sheet_name='Turnos')
    df_hours.to_excel(writer, sheet_name='Horas')


import numpy as np
import pandas as pd
from datetime import date, timedelta

# Number of workers
num_workers = 18

# Number of shifts per day
num_shifts_day = 3

# Number of workers per shift
workers_per_shift = num_workers // num_shifts_day

# Number of days in a year
num_days_year = 365

# Create an empty DataFrame for shifts, hours and weekly hours
df_shifts = pd.DataFrame()
df_hours = pd.DataFrame()
df_weekly_hours = pd.DataFrame()

# Assign shifts and hours
for worker in range(num_workers):
    worker_shifts = []
    worker_hours = []
    worker_weekly_hours = []
    weekly_hours = 0
    for day in range(num_days_year):
        # Shift changes every week
        shift = (worker // workers_per_shift + day // 7) % num_shifts_day
        # Workers rest on two days of their weekly cycle, which are staggered for each worker
        if day % 7 not in [(worker + 5) % 7, (worker + 6) % 7]:
            worker_shifts.append(shift)
            worker_hours.append(8)  # 8 hours of work per shift
            weekly_hours += 8
        else:
            worker_shifts.append(-1)  # -1 indicates a day off
            worker_hours.append(0)  # 0 hours of work on a day off

        # At the end of the week, record the total hours and reset the counter
        if day % 7 == 6:
            worker_weekly_hours.append(weekly_hours)
            weekly_hours = 0

    df_shifts[f'Trabalhador {worker+1}'] = worker_shifts
    df_hours[f'Trabalhador {worker+1}'] = worker_hours
    df_weekly_hours[f'Trabalhador {worker+1}'] = worker_weekly_hours

# Change shift numbers to shift names
df_shifts = df_shifts.replace({0: 'Manhã', 1: 'Tarde', 2: 'Noite', -1: 'Folga'})

# Create a date range for the index
start_date = date.today()
date_range = [start_date + timedelta(days=day) for day in range(num_days_year)]
df_shifts.index = date_range
df_hours.index = date_range

# Save to Excel
with pd.ExcelWriter('schedule.xlsx') as writer:
    df_shifts.to_excel(writer, sheet_name='Turnos')
    df_hours.to_excel(writer, sheet_name='Horas Diárias')
    df_weekly_hours.to_excel(writer, sheet_name='Horas Semanais')
