import logging
import os
import requests

from bs4 import BeautifulSoup
from configparser import ConfigParser
from const import IP_URL, IP_GEO_URL, GEOCODE_URL, MUSLIMPRO_URL, CONF_PATH
from datetime import datetime, timedelta
from winotify import Notification, audio

# set logger
logging.basicConfig(filename='daily_prayer_notification.log', 
                    encoding='utf-8',
                    filemode='a', 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger()


class Config(ConfigParser):
    def __init__(self) -> None:
        super().__init__()
    
    def get_config(self):
        """initiates the config from config.ini"""

        
        if os.path.exists(CONF_PATH):
            self.read(CONF_PATH)
            self.location = self.get('LOCATION', 'location', fallback=None)
            self.reminder_time = self.get('NOTIFICATION', 'reminder_time', fallback='10').split(',')
            self.reminder_time = sorted(list(map(self.__int_convert, self.reminder_time)), reverse=True)
            logger.info('Config set')
        else:
            # if config.ini doesn't exist, set default
            self.location = 'auto'
            self.reminder_time = [10]
            logger.warning('Config file not found, run app using default configuration')

    @staticmethod
    def __int_convert(x):
        try:
            return int(x)
        except:
            return 0



class Location:
    """A class containing geo information"""

    def __init__(self, location=None) -> None:
        if location in ['auto', '', None]:
            location = self.get_ip_location()

        geocode = self.get_loc_geocode(location)
        try:
            # these are the informations needed to query the time prayer 
            self.country_code = geocode['data'][0]['country_module']['global']['alpha2']
            self.country_name = geocode['data'][0]['country']
            self.city_name = geocode['data'][0]['name']
            self.coordinates = f"{geocode['data'][0]['latitude']},{geocode['data'][0]['longitude']}"
        except Exception as e:
            logger.error(str(e))
            raise Exception(str(e))
    

    def __str__(self):
        return '\n'.join([f"{k}:{v}" for k,v in self.__dict__.items()])
    

    def get_ip_location(self):
        ip = self.__get_ip()
        response = requests.get(IP_GEO_URL+ip)
        if response.status_code == 200:
            return response.json().get('city')
        else:
            logger.error('Failed getting location')
            raise Exception('failed getting location')


    def get_loc_geocode(self, location):
        params ={
            'query': location
        }
        response = requests.get(GEOCODE_URL, params=params)
        if 'error' in response.json():
            logger.error(str(response.json()))
            raise Exception('failed getting geocode')
        else:
            return response.json()
        

    @staticmethod
    def __get_ip():
        response = requests.get(IP_URL)
        if response.status_code == 200:
            return response.json().get('ip')
        else:
            logger.error('Failed getting IP address')
            raise Exception('failed getting ip address')



class PrayerTime:
    """Main class"""

    def __init__(self) -> None:
        self.prayers = ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha'a"]
        self.prayer_time = []


    def get_prayer_time(self, geocode:Location):
        params = {
            'country_code': geocode.country_code,
            'country_name': geocode.country_name,
            'city_name': geocode.city_name,
            'coordinates': geocode.coordinates
        }
        response = requests.get(MUSLIMPRO_URL, params=params)
        if response.status_code == 200:
            return self.__scrape_time(response.content)
        else:
            logger.error('Failed getting prayer time')
            raise Exception('failed getting prayer time')
    

    def set_prayer_time(self, prayer_time:dict):
        self.date = prayer_time.get('date')
        for prayer in self.prayers:
            try:
                self.prayer_time.append(prayer_time.get(prayer)+":00")
            except:
                self.prayer_time.append(None)


    def start_notify(self, reminder_time=[]):
        now = datetime.now()
        
        if datetime.strftime(now, '%d-%m-%Y') != self.date:
            # if the current date doesn't match the date of the stored prayer time, raise exception
            logger.warning('Date not match')
            raise StopIteration('Date not match')
        
        for minute in reminder_time:
            # check reminder
            delta = now + timedelta(minutes=int(minute))
            delta = datetime.strftime(delta, '%H:%M:%S')
            if delta in self.prayer_time:
                prayer = self.prayers[self.prayer_time.index(delta)]
                self.display_notification(prayer, delta, f"{prayer} in {minute} mins")
        
        hour = datetime.strftime(now, '%H:%M:%S')
        if hour in self.prayer_time:
            prayer = self.prayers[self.prayer_time.index(hour)]
            self.display_notification(prayer, hour)


    @staticmethod
    def __scrape_time(html):
        # scrape prayer time using BeautifulSoup
        soup = BeautifulSoup(html, "html.parser")
        prayer = soup.find_all("span", attrs ={"class": "waktu-solat"})
        time = soup.find_all("span", attrs ={"class": "jam-solat"})

        data = {p.get_text():t.get_text() for p,t in zip(prayer, time)}
        data['date'] = datetime.now().strftime('%d-%m-%Y')

        logger.info('Prayer time scraped')
        return data


    @staticmethod
    def display_notification(prayer, time, msg=None):
        if not msg:
            msg = f"{prayer} time at {time}"
        notif = Notification(app_id='Daily Prayer Notification',
                             title=prayer,
                             msg=msg,
                             duration='long')
        notif.set_audio(audio.Reminder, loop=False)
        notif.show()