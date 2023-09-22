import numpy as np
import calendar
import pandas as pd

# Number of workers
num_workers = 18

# Number of days in a week
num_days_week = 7

# Number of shifts per day
num_shifts_day = 3

# Number of workers per shift
workers_per_shift = num_workers // num_shifts_day

# Number of weeks in a year
num_weeks_year = 52

# Number of days in a year
num_days_year = 365

# Initialize the schedule with -1, indicating no shift assigned
schedule = -1 * np.ones((num_days_year, num_workers), dtype=int)

# Define shift names
shift_names = ["Manhã", "Tarde", "Noite"]

# Initialize array to hold weekly hours for each worker
worker_hours = np.zeros((num_weeks_year, num_workers), dtype=int)

# Assign shifts and track hours
day_of_year = 0
for week in range(num_weeks_year):
    for day_of_week in range(num_days_week):
        # Assign shift for 5 days of the week (worker's shift changes every week)
        for worker in range(num_workers):
            shift = (worker // workers_per_shift + week) % num_shifts_day
            if day_of_week > 1:  # Workers rest on days 0 and 1
                schedule[day_of_year, worker] = shift
                # Add 8 hours to this worker's weekly hours
                worker_hours[week, worker] += 8
        day_of_year += 1
    # Skip days after the last week of the year
    if day_of_year >= num_days_year:
        break

# Define day names
day_names = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]

# Prepare data for Excel
excel_data = []
worker_hours_data = []
day_of_year = 0
for month in range(1, 13):
    for day_of_month in range(1, calendar.monthrange(2023, month)[1] + 1):
        day_of_week = day_of_year % num_days_week
        for shift in range(num_shifts_day):
            workers_in_shift = [worker+1 for worker in range(num_workers) if schedule[day_of_year, worker] == shift]
            if workers_in_shift:
                excel_data.append({
                    "Data": f"{day_of_month} de {calendar.month_name[month]}",
                    "Dia da Semana": day_names[day_of_week],
                    "Turno": shift_names[shift],
                    "Trabalhadores": ', '.join(map(str, workers_in_shift))
                })
        day_of_year += 1

# Add weekly hours to Excel data
for week in range(num_weeks_year):
    for worker in range(num_workers):
        worker_hours_data.append({
            "Semana": week+1,
            "Trabalhador": worker+1,
            "Horas Trabalhadas": worker_hours[week, worker]
        })

# Convert to DataFrame
df = pd.DataFrame(excel_data)
df_hours = pd.DataFrame(worker_hours_data)

# Write to Excel
with pd.ExcelWriter('schedule.xlsx') as writer:
    df.to_excel(writer, sheet_name='Schedule', index=False)
    df_hours.to_excel(writer, sheet_name='Worker Hours', index=False)
