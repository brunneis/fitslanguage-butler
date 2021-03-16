from requests import Session
import lxml.html
import yaml
import datetime
import logging

logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)-15s [%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

with open('config.yaml', 'r') as input_file:
    config = yaml.safe_load(input_file)

start_date = datetime.datetime.today()
delta = datetime.timedelta(days=1)
current_date = start_date + delta
days = []
for _ in range(40):
    days.append(f'{current_date.year}-{current_date.month}-{current_date.day}')
    current_date += delta

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
headers = {'user-agent': user_agent, 'Content-Type': 'application/x-www-form-urlencoded'}
session = Session()
session.headers.update(headers)

session.post('https://www.fitslanguage.com/login',
             data=f"email={config['email']}&pass={config['password']}&entrar=Iniciar sesión")

for day in days:
    logging.info(f'Checking {day}...')

    response = session.post('https://www.fitslanguage.com/lessons/search',
                            data=f'day={day}&search=Buscar')

    root = lxml.html.document_fromstring(response.content)
    card_elements = root.xpath("//div[@class='ui card']")

    for card_element in card_elements:
        teacher_name = card_element.xpath("./div[@class='content']/a[@class='header']/text()")[0]
        if config['teacher'].lower() in teacher_name.lower():
            slot_times = list(
                filter(lambda x: x, [
                    element.strip()
                    for element in card_element.xpath("./table/tbody/tr/td[1]/text()")
                ]))

            slot_message_cells = card_element.xpath("./table/tbody/tr/td[2]")

            class_ids = [
                class_id
                for class_id in card_element.xpath("./table/tbody/tr/td[2]/form/p/input[1]/@value")
            ]

            class_id_index = 0
            for i, slot_time in enumerate(slot_times):
                try:
                    slot_message = ''.join(slot_message_cells[i].xpath('.//text()')).strip()
                except IndexError:
                    continue

                if slot_message.lower() == 'reservar':
                    if slot_time in config['slots']:
                        class_id = class_ids[class_id_index]
                        logging.info(
                            f'[BOOKING] [{day} {slot_time}] https://www.fitslanguage.com/lessons/view/{class_id}'
                        )
                        session.post('https://www.fitslanguage.com/lessons/book',
                                     data=f'clase={class_id}&confirmar=Reservar')
                    class_id_index += 1
            break
