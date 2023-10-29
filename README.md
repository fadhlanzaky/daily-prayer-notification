# daily-prayer-notification
A pop-up Windows notification to notify daily prayer time. Built using BeautifulSoup to scrape the prayer time from muslimpro.com and Winotify as the module to show notification toast on Windows.

## Start
- install dependencies `pip install -r requirements.txt`
- config your location and preferred reminder time in `config.ini`
- run the app `python main.py `

## Configuration
configurations are stored in config.ini
```ini
    [LOCATION]
    # set the location to your current location (e.g. Jakarta)
    # if 'auto' or blank, the location will be located based on your IP address (might not be accurate)
    location = auto
    
    [NOTIFICATION]
    # the number of minutes to remind you before the adhan starts.
    # use comma for multiple reminders (e.g. 5, 10, 15)
    reminder_time = 10, 5
```

## Startup
the script can be set to run on Windows startup. The tutorial will be provided soon
