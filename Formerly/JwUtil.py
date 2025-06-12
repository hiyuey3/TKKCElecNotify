# from io import BytesIO
# import requests
# import time
# import json
# from bs4 import BeautifulSoup
# # from modules.db import func as sql_func
# # from modules import static as static
# from icalendar import Calendar
# import re
# from datetime import datetime, timedelta
#
# def gen_term_lesson_record(xujc_session:requests.Session, target_term: str):
#     per_term_lessons = []
#     for lx in range(1, 3 if target_term.endswith('2') else 2):
#         time.sleep(0.2)
#         response = xujc_session.get(f'http://jw.xujc.com/student/index.php?c=Default&a=exportical&tm_id={target_term}&lx={lx}', headers=static.headers)
#         file_in_memory = BytesIO(response.content)
#         file_in_memory.seek(0)
#         ical_bytes_from_memory = file_in_memory.read().decode('utf-8')
#         analyzed_lessons = analyze_lesson_table(ical_bytes_from_memory)
#         if lx == 2:
#             per_term_lessons[-2:] = analyzed_lessons[-2:]
#         else:
#             per_term_lessons = analyzed_lessons
#     insert_lesson_list = []
#     for week_lessons in per_term_lessons:
#         insert_lesson_list.append((target_term, week_lessons['week'], week_lessons['start_date'], week_lessons['end_date'], json.dumps(week_lessons['per_day_lessons'])))
#     db_conn = sql_func.create_connection()
#     sql_func.insert_term_lessons(db_conn, insert_lesson_list)
#     db_conn.close()
#
# def get_lessons_update(xujc_session:requests.Session) -> tuple:
#     response = xujc_session.get(f'http://jw.xujc.com/student/index.php?c=Default&a=tbk', headers=static.headers)
#     soup = BeautifulSoup(response.text, "html.parser")
#     def extract_table_data(table_id):
#         table = soup.find("table", {"id": table_id})
#         if not table:
#             return []
#         rows = table.find_all("tr")[1:]
#         results = []
#         for row in rows:
#             cols = row.find_all("td")
#             if len(cols) < 9:
#                 continue
#             raw_date = cols[7].text.strip()
#             try:
#                 formatted_date = datetime.strptime(raw_date, "%Y-%m-%d").strftime("%Y%m%d")
#             except ValueError:
#                 formatted_date = raw_date  # 避免崩溃，保留原始日期
#             data = {
#                 "modify_type": cols[1].text.strip(),
#                 "lesson_name": cols[2].text.strip(),
#                 "teacher_name": cols[3].text.strip(),
#                 "week": cols[4].text.strip(),
#                 "day_in_week": cols[5].text.strip(),
#                 "lesson_rank": cols[6].text.strip(),
#                 "date": formatted_date,
#                 "classroom": cols[8].text.strip()
#             }
#             results.append(data)
#         return results
#     adjust_list = extract_table_data("data_table")
#     makeup_list = extract_table_data("data_table2")
#     db_conn = sql_func.create_connection()
#     for adjust_lesson in adjust_list:
#         related_week = sql_func.get_week_data_by_date(db_conn, adjust_lesson['date'])
#         week_lessons = json.loads(related_week['per_day_lessons'])
#         lessons = week_lessons[adjust_lesson['date']]
#         for lesson in lessons:
#             if lesson['lesson_name'] == adjust_lesson['lesson_name'] and lesson['classroom'] == adjust_lesson['classroom'] and lesson['teacher_name'] == adjust_lesson['teacher_name']:
#                 lesson['tag'] = adjust_lesson['modify_type']
#                 lesson['lesson_disabled'] = True
#                 sql_func.update_lesson_by_week(db_conn, (json.dumps(week_lessons), related_week['related_term'], related_week['week'],))
#                 break
#     for makeup_lesson in makeup_list:
#         related_week = sql_func.get_week_data_by_date(db_conn, makeup_lesson['date'])
#         week_lessons = json.loads(related_week['per_day_lessons'])
#         lessons = week_lessons[makeup_lesson['date']]
#         start_time, end_time = date_mapper(makeup_lesson['lesson_rank'])
#         new_lessons = []
#         inserted = False
#         for lesson in lessons:
#             if lesson['lesson_disabled'] and lesson['lesson_name'] == makeup_lesson['lesson_name'] and lesson['teacher_name'] == makeup_lesson['teacher_name'] and lesson['start_time'] == start_time and lesson['end_time'] == end_time:
#                 new_lessons.append({
#                     "classroom": makeup_lesson['classroom'],
#                     "end_time": end_time,
#                     "lesson_disabled": False,
#                     "lesson_name": makeup_lesson['lesson_name'],
#                     "start_time": start_time,
#                     "tag": makeup_lesson['modify_type'],
#                     "teacher_name": makeup_lesson['teacher_name']
#                 })
#                 inserted = True
#             else:
#                 new_lessons.append(lesson)
#         if not inserted:
#                 new_lessons.append({
#                     "classroom": makeup_lesson['classroom'],
#                     "end_time": end_time,
#                     "lesson_disabled": False,
#                     "lesson_name": makeup_lesson['lesson_name'],
#                     "start_time": start_time,
#                     "tag": makeup_lesson['modify_type'],
#                     "teacher_name": makeup_lesson['teacher_name']
#                 })
#         week_lessons[makeup_lesson['date']] = new_lessons
#         sql_func.update_lesson_by_week(db_conn, (json.dumps(week_lessons), related_week['related_term'], related_week['week'],))
#     db_conn.close()
#     return (len(adjust_list), len(makeup_list))
# def date_mapper(lesson_rank: str) -> tuple:
#     START_TIME_MAPPER = {
#         '1': '08:00',
#         '2': '08:55',
#         '3': '10:00',
#         '4': '10:45',
#         '午1': '12:30',
#         '午2': '13:25',
#         '5': '14:30',
#         '6': '15:25',
#         '7': '16:30',
#         '8': '17:25',
#         '9': '19:30',
#         '10': '20:25',
#         '11': '21:20'
#     }
#     END_TIME_MAPPER = {
#         '1': '08:45',
#         '2': '09:40',
#         '3': '10:45',
#         '4': '11:40',
#         '午1': '13:15',
#         '午2': '14:10',
#         '5': '15:15',
#         '6': '16:10',
#         '7': '17:15',
#         '8': '18:10',
#         '9': '20:15',
#         '10': '21:10',
#         '11': '22:05'
#     }
#
#     # 拆解成前后两个部分（开始和结束）
#     start_and_end_rank = lesson_rank.split('-')
#     return (START_TIME_MAPPER.get(start_and_end_rank[0], '08:00'), END_TIME_MAPPER.get(start_and_end_rank[1], '08:45'))
#
# def analyze_lesson_table(ical_data) -> list:
#     cal = Calendar.from_ical(ical_data)
#     weeks_list = []
#     for component in cal.walk():
#         if component.name == "VEVENT":
#             summary = component.get('SUMMARY')
#             location = component.get('LOCATION', None)
#             description = component.get('DESCRIPTION', None)
#             if location is None and description is None:
#                 date_start = component.get('DTSTART').dt
#                 date_end = component.get('DTEND').dt
#                 match = re.search(r"第 (\d+) 周", summary)
#                 if match:
#                     week_number = int(match.group(1))
#                     new_week=dict({ 'week': week_number, 'start_date': date_start.strftime('%Y%m%d'), 'end_date': (date_end - timedelta(days=1)).strftime('%Y%m%d'), 'per_day_lessons': dict()})
#                     current_date = date_start
#                     while current_date < date_end:
#                         date_key = current_date.strftime('%Y%m%d')
#                         new_week['per_day_lessons'][date_key] = []
#                         current_date += timedelta(days=1)
#                     weeks_list.append(new_week)
#             else:
#                 dtstart = component.get('DTSTART').dt.replace(tzinfo=None)
#                 dtend = component.get('DTEND').dt.replace(tzinfo=None)
#                 rrule = component.get('RRULE')
#                 until = rrule.get('UNTIL')[0].replace(tzinfo=None)
#                 interval = rrule.get('INTERVAL')[0]
#                 start_time = f'{dtstart.hour:02d}:{dtstart.minute:02d}'
#                 end_time = f'{dtend.hour:02d}:{dtend.minute:02d}'
#                 teacher_name_regex = re.match(r"([^ -]+)", description)
#                 if teacher_name_regex:
#                     teacher_name = teacher_name_regex.group(1)
#                 else:
#                     teacher_name = '未知'
#                 lesson_data = {
#                     'lesson_name': str(summary),
#                     'teacher_name': teacher_name,
#                     'classroom': str(location),
#                     'start_time': start_time,
#                     'end_time': end_time,
#                     'lesson_disabled': False,
#                     'tag': ""
#                 }
#                 current_date = dtstart
#                 week_number = 0
#                 for week in weeks_list:
#                     start_date = datetime.strptime(week['start_date'], "%Y%m%d")
#                     end_date = datetime.strptime(week['end_date'], "%Y%m%d")
#                     if current_date >= start_date and current_date <= end_date:
#                         break
#                     else:
#                         week_number += 1
#                 try:
#                     while current_date <= until:
#                         date_str = current_date.strftime('%Y%m%d')
#                         weeks_list[week_number]['per_day_lessons'][date_str].append(lesson_data)
#                         current_date += timedelta(weeks=interval)
#                         week_number += interval
#                 except:
#                     pass
#
#     for week_data in weeks_list:
#         for date_key in week_data['per_day_lessons']:
#             lessons = week_data['per_day_lessons'][date_key]
#             sorted_lessons = sorted(lessons, key=lambda x: x['start_time'])
#             week_data['per_day_lessons'][date_key] = sorted_lessons
#     return weeks_list