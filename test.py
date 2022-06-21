import datetime
import website.database
dt = datetime.datetime.now()

new =   dt.strftime('%A-%d-%b-%Y  %I:%M %p')
print(new)

def evaluation_duration():
    _questions = 45
    duration = _questions * 15
    time = f"{duration} secs"
    

    if duration > 60:
        mins = int(duration / 60)
        secs = duration - (60 * mins)
        time = f"{mins} mins {secs} secs"

    return time

print(evaluation_duration())
