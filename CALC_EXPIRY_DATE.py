from datetime import timedelta, date,datetime
import calendar


holiday = ['']

def weekly_expiry():
    day = date.today()
    print("TODAY DATE",day)
    expiry = day + timedelta(days=(10-day.weekday()) % 7)
    while is_holiday(expiry):
        expiry = expiry - timedelta(days=1)
    print("Weekly ExpiryDATE: ",expiry)
    return expiry

def monthly_expiry():
    today =  date.today()
    expiry = calendar.monthrange(today.year,today.month)
    expiry = today.replace(day=expiry)
    while expiry.weekday() != 3:
        expiry = expiry - timedelta(days=1)
        
    while is_holiday(expiry):
        expiry = expiry - timedelta(days=1)
    
    print("ExpiryDATE",expiry)
    return expiry


def is_holiday(today):
    #holidays = pd.read_csv(path)
    dates_list = []
    #dates_list = [datetime.strptime(holiday ,"%d/%m/%y").date() for holiday in holidays['date']]
    if today in dates_list:
        return True
    else:
        return False
    
if __name__ == '__main__':
    weekly_expiry()
    #monthly_expiry()
    
    