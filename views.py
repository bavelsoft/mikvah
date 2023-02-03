from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo
from zmanim.zmanim_calendar import ZmanimCalendar
from zmanim.util.geo_location import GeoLocation
from re import compile
from .models import Appointment

#configurable values
best_time = time(18, 0) #TODO table with key-value pairs in database
weekday_appointment_minutes = 15
minutes_open = 4*60
prep_minutes = {'bath':60, 'shower':30, '':0} #currently needs to be a multiple of appointment_minutes

def index(request):
    #TODO display if already scheduled, secure cookie
    ##TODO cancel button
    ##TODO optional password
    days = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun',] #TODO share this with below, and hardcoded Fri
    for x in range(today().weekday()):
        days.append(days.pop(0))
    return render(request, 'pick_day.html', {'contact':request.COOKIES.get('contact', ''),
        'days':days, })

def times(request):
    day_param = request.GET.get('day', '')
    earlier_param = request.GET.get('earlier', '')
    prep_param = request.GET.get('prep', '') #TODO remember from cookie?
    contact_param = request.GET.get('contact', '')
    later_param = request.GET.get('later', '')
    textable_param = request.GET.get('textable', False) #TODO

    #TODO complain about missing contact

    start = date_from_param(day_param)
    stop = start + timedelta(days=2) #why does this ned to be 2?
    appointments = Appointment.objects.filter(datetime__gte=start, datetime__lte=stop)
    appointment_times = list(localize(a)+timedelta(minutes=a.minutes_offset) for a in appointments)

    zman = get_zman(start)
    if day_param == "Fri":
        prep_param = ''
        appointment_minutes = 5
    else:
        appointment_minutes = weekday_appointment_minutes
    earliest = zman - timedelta(minutes=zman.minute%appointment_minutes)
    #earliest = zman timedelta(minutes=appointment_minutes-(zman.minute%appointment_minutes))
    latest = earliest + timedelta(minutes=minutes_open)

    times = []
    if earlier_param:
        candidate = earliest
    elif later_param:
        candidate = combine(start, time_from_param(later_param))
    else:
        if day_param == "Fri":
            candidate = earliest
        else:
            candidate = combine(start, best_time)

    candidate += timedelta(minutes=prep_minutes[prep_param])

    later_available = True
    for i in range(100): #just not infinite for safety
        if candidate > latest:
            later_available = False
            break
        if candidate not in appointment_times:
            times.append(candidate)
        candidate += timedelta(minutes=appointment_minutes)
        if len(times) == 3 or len(times) == 1 and day_param == "Fri":
            break

    if prep_param:
        for i in range(len(times)):
            times[i] -= timedelta(minutes=prep_minutes[prep_param])

    formatted_times = [nice_time(t) for t in times]

    response = render(request, 'pick_time.html', {'times':formatted_times, 'date':nice_date(start),
        'day':day_param, 'contact':contact_param, 'prep':prep_param, 'zman':nice_time(zman),
        'later_available':later_available, 'earlier':earlier_param,
        #'debug':str(appointment_times)+" " +str(times),
        })
    if contact_param:
        response.set_cookie('contact', contact_param, max_age=60*60*24*365)
    return response

def get_zman(d):
    location = GeoLocation('New York, NY', 40.85139828693182, -73.93642913006643, 'America/New_York', elevation=0)
    calendar = ZmanimCalendar(geo_location=location, date=d)
    zman = calendar.sunset_offset_by_degrees(97.3) # seems to be three small stars
    return zman.replace(second=0, microsecond=0)

def schedule(request):
    day_param = request.POST.get('day')
    time_param = request.POST.get('time')
    contact_param = request.POST.get('contact', 'unknown')
    prep_param = request.POST.get('prep', '')
    entry = combine(date_from_param(day_param), time_from_param(time_param))
    #TODO remove other appointment for same contact (other than unknown
    appointment = Appointment(datetime=entry, contact=contact_param, textable=False)
    appointment.minutes_offset = prep_minutes[prep_param]
    appointment.save()
    return render(request, 'pick_scheduled.html', {'day':entry.date(), 'time':time_param, #'debug':entry,
        })

def attendant(request):
    appointments = Appointment.objects.filter(datetime__gte=today()).order_by('datetime')
    formatted_appointments = [{
        'xday':a.datetime.date().strftime("%A"),
        'xtime':nice_time(localize(a)),
        'ttime':nice_time(localize(a)+timedelta(minutes=a.minutes_offset)),
        'contact':a.contact} for a in appointments]
    return render(request, 'attendant.html', {'appointments':formatted_appointments,})

def nice_date(d):
    return d.strftime("%A, %Y-%m-%d")

def nice_time(t):
    return t.time().strftime("%I:%M")

def localize(dt):
    return dt.datetime.astimezone(ZoneInfo("America/New_York")) #TODO share

def date_from_param(day_param):
    day = {'Mon':0,'Tue':1,'Wed':2,'Thu':3,'Fri':4,'Sat':5,'Sun':6}.get(day_param)
    #TODO error handling?
    days = day - today().weekday()
    if days < 0:
        days += 7
    return today() + timedelta(days)

time_re = compile(r'(\d+):(\d+)')

def time_from_param(time_param):
    (hour, minute) = time_re.match(time_param).groups()
    return time(12+int(hour), int(minute))

def combine(d, t):
    return datetime.combine(d, t, tzinfo=ZoneInfo("America/New_York"))

def today():
    return datetime.now(tz=ZoneInfo("America/New_York")).date()
