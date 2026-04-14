import csv
import requests
from datetime import datetime
from config import SHEETS_URL

def get_employees():
    try:
        response = requests.get(SHEETS_URL)
        response.raise_for_status()
        
        lines = response.text.strip().split('\n')
        reader = csv.DictReader(lines)
        
        employees = []
        for row in reader:
            if row.get('ФИО') and row.get('Дата окончания ЭЦП'):
                employees.append({
                    'name': row['ФИО'],
                    'position': row.get('Должность', ''),
                    'start_date': row.get('Дата начала ЭЦП', ''),
                    'end_date': row['Дата окончания ЭЦП'],
                    'status': row.get('Статус', ''),
                    'telegram_id': row.get('Telegram ID', ''),
                    'note': row.get('Примечание', '')
                })
        return employees
    except Exception as e:
        print(f"Error reading spreadsheet: {e}")
        return []

def parse_date(date_str):
    formats = ['%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y']
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None

def get_expiring_soon(days_list=[30, 14, 7, 3, 1]):
    employees = get_employees()
    today = datetime.now().date()
    expiring = {d: [] for d in days_list}
    
    for emp in employees:
        end_date = parse_date(emp['end_date'])
        if not end_date:
            continue
        
        days_left = (end_date.date() - today).days
        
        if days_left in days_list and days_left >= 0:
            expiring[days_left].append(emp)
        elif days_left < 0 and emp['status'] != 'Истекла':
            emp['days_overdue'] = abs(days_left)
            expiring[-1].append(emp)
    
    return expiring

def format_notification(employees, days):
    if not employees:
        return ""
    
    if days == -1:
        title = "⚠️ ПРОСРОЧКА!"
    else:
        title = f"⏰ ЭЦП истекает через {days} дн."
    
    lines = [f"\n{title}\n"]
    for emp in employees:
        lines.append(f"• {emp['name']}")
        lines.append(f"  {emp['position']}")
        if days == -1:
            lines.append(f"  Просрочено на {emp.get('days_overdue', '')} дней!")
        lines.append("")
    
    return "\n".join(lines)
