#!/usr/bin/env python3
"""
Скрипт для запуска всех тестов системы усыновления животных
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Запуск команды с выводом результатов"""
    print(f"\n {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        if result.returncode == 0:
            print(f"{description} - УСПЕШНО")
            if result.stdout.strip():
                print(result.stdout)
        else:
            print(f"{description} - ПРОВАЛЕНО")
            if result.stderr:
                print("Ошибки:", result.stderr)
            if result.stdout:
                print("Вывод:", result.stdout)
        return result.returncode == 0
    except Exception as e:
        print(f"{description} - ОШИБКА: {e}")
        return False

def main():
    """Основная функция запуска тестов"""
    print("Запуск полного тестирования системы усыновления животных")
    print("=" * 60)

    # Проверяем наличие файлов
    test_files = [
        'tests/test_unit_repositories.py',
        'tests/test_integration_endpoints.py'
    ]

    missing_files = []
    for test_file in test_files:
        if not os.path.exists(test_file):
            missing_files.append(test_file)

    if missing_files:
        print(f"Отсутствуют файлы тестов: {', '.join(missing_files)}")
        return False

    # Запускаем unit тесты
    result1 = subprocess.run("python3 tests/test_unit_repositories.py", shell=True, capture_output=True, text=True, cwd=os.getcwd())
    success1 = ("OK" in result1.stderr or "OK" in result1.stdout) and "Ran 10 tests" in result1.stderr
    print(f"Запуск unit тестов репозиториев...")
    if success1:
        print("Запуск unit тестов репозиториев - УСПЕШНО")
    else:
        print("Запуск unit тестов репозиториев - ПРОВАЛЕНО")
        print("Вывод:", result1.stdout)
        print("Ошибки:", result1.stderr)

    # Запускаем интеграционные тесты
    result2 = subprocess.run("python3 tests/test_integration_endpoints.py", shell=True, capture_output=True, text=True, cwd=os.getcwd())
    success2 = ("OK" in result2.stderr or "OK" in result2.stdout) and "Ran 11 tests" in result2.stderr
    print(f"Запуск интеграционных тестов endpoints...")
    if success2:
        print("Запуск интеграционных тестов endpoints - УСПЕШНО")
    else:
        print("Запуск интеграционных тестов endpoints - ПРОВАЛЕНО")
        print("Вывод:", result2.stdout)
        print("Ошибки:", result2.stderr)

    # Итоговый отчет
    print("\n" + "=" * 60)
    print("ИТОГОВЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ")
    print("=" * 60)

    total_tests = 21  # 10 unit + 11 integration
    passed_tests = (10 if success1 else 0) + (11 if success2 else 0)

    print(f"Всего тестов: {total_tests}")
    print(f"Пройдено: {passed_tests}")
    print(f"Провалено: {total_tests - passed_tests}")
    print(".1f")

    if success1 and success2:
        print("\nВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("Система усыновления животных готова к работе.")
        print("Подробный отчет доступен в файле TEST_REPORT.md")
        return True
    else:
        print("\n НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛИЛИСЬ!")
        print("Проверьте логи выше для диагностики проблем.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)