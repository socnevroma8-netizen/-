from backend.services.schedule_service import ScheduleService


service = ScheduleService()

print("Всего строк:", len(service.rows))
print("Классов:", len(service.class_map))

print("\nРасписание 1О:")
print(service.get_student_schedule("1О", None)[:3])

print("\nРасписание 5Б:")
print(service.get_student_schedule("5Б", None)[:3])