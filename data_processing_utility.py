import os
from collections import Counter

def detect_delimiter(file_path, sample_lines=5):
    common_delimiters = [',', ';', '\t', '|', ':']

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = []
            for i, line in enumerate(f):
                if i >= sample_lines:
                    break
                if line.strip():
                    lines.append(line.strip())
            
        if not lines:
            return ',', 0
        
        best_delimiter = ','
        best_score = 0
        best_field_count = 0
        
        for delimiter in common_delimiters:
            field_counts = []
            for line in lines:
                if line:
                    fields = line.split(delimiter)
                    non_empty_fields = [f for f in fields if f.strip()]
                    if non_empty_fields:
                        field_counts.append(len(non_empty_fields))
            
            if field_counts:
                counter = Counter(field_counts)
                most_common = counter.most_common(1)[0]
                
                common_field_count = most_common[0]
                frequency = most_common[1]
                
                score = frequency * common_field_count
                
                if score > best_score:
                    best_score = score
                    best_delimiter = delimiter
                    best_field_count = common_field_count
        
        return best_delimiter, best_field_count
    
    except Exception:
        return ',', 3  

def detect_column_types(file_path, delimiter, sample_lines=10):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            samples = []
            for i, line in enumerate(f):
                if i >= sample_lines:
                    break
                line = line.strip()
                if line:
                    parts = line.split(delimiter)
                    parts = [p.strip() for p in parts]
                    samples.append(parts)
        
        if not samples:
            return ['string']  #по умолчанию
        
        #определяем типы для каждого столбца
        column_types = []
        num_columns = len(samples[0])
        
        for col_idx in range(num_columns):
            column_values = []
            for sample in samples:
                if col_idx < len(sample):
                    column_values.append(sample[col_idx])
            
            #анализируем значения в столбце
            if not column_values:
                column_types.append('string')
                continue
            
            #пробуем определить тип
            could_be_int = True
            could_be_float = True
            
            for value in column_values:
                if not value:  #пустое значение
                    could_be_int = False
                    could_be_float = False
                    break
                
                #проверка на целое число
                if could_be_int:
                    try:
                        int(value)
                    except ValueError:
                        could_be_int = False
                
                #рроверка на дробное число
                if could_be_float:
                    try:
                        float(value)
                    except ValueError:
                        could_be_float = False
            
            #определяем итоговый тип
            if could_be_int:
                column_types.append('int')
            elif could_be_float:
                column_types.append('float')
            else:
                column_types.append('string')
        
        return column_types
    
    except Exception:
        return ['string']  #по умолчанию при ошибке

def suggest_column_names(field_count, delimiter, file_path, sample_lines=3):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
        
        if first_line:
            parts = first_line.split(delimiter)
            parts = [p.strip() for p in parts if p.strip()]
            
            #если в первой строке есть данные, которые выглядят как заголовки
            could_be_headers = True
            for part in parts:
                if len(part) > 30:  #слишком длинные для заголовков
                    could_be_headers = False
                    break
                #проверяем, не число ли это
                try:
                    float(part)
                    could_be_headers = False  #это число, значит не заголовок
                    break
                except ValueError:
                    pass
            
            if could_be_headers and len(parts) == field_count:
                return parts  #используем первую строку как заголовки
        
        #генерация автоназваний
        return [f"column_{i+1}" for i in range(field_count)]
    
    except Exception:
        return [f"column_{i+1}" for i in range(field_count)]

#проверка поля на корректность
def validate_field(field_name, value, field_type='string'):
    errors = []
    
    if not value.strip():
        errors.append("пустое значение")
        return errors, None
    
    try:
        if field_type == 'int':
            converted = int(value)
            if converted <= 0:
                errors.append("не положительное число")
            return errors, converted
            
        elif field_type == 'float':
            converted = float(value)
            if converted < 0:
                errors.append("отрицательное число")
            return errors, converted
            
        else:  #string
            return errors, value.strip()
            
    except ValueError:
        if field_type == 'int':
            errors.append("не целое число")
        elif field_type == 'float':
            errors.append("не число")
        return errors, None

def save_report(file_path, total_lines, correct_count, incorrect_count, incorrect_records):
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    report_file = f"{base_name}_report.txt"
    
    #получаем текущую директорию
    current_dir = os.getcwd()
    full_report_path = os.path.join(current_dir, report_file)
    
    #если файл существует - добавляем номер
    counter = 1
    while os.path.exists(full_report_path):
        report_file = f"{base_name}_report_{counter}.txt"
        full_report_path = os.path.join(current_dir, report_file)
        counter += 1
    
    with open(full_report_path, 'w', encoding='utf-8') as f:
        #общее количество записей в файле
        f.write("Отчет об обработке данных\n")
        f.write("\n\n")
        f.write(f"Общее количество записей: {total_lines}\n\n")
        
        #количество корректных и некорректных записей
        f.write(f"Количество корректных записей: {correct_count}\n")
        f.write(f"Количество неккоректных записей: {incorrect_count}\n\n")
        
        #ошибки с указанием причины
        if incorrect_records:
            f.write("Список ошибок:\n")
            f.write("\n")
            for record in incorrect_records:
                f.write(f"\nСтрока {record['line_num']}:\n")
                f.write(f"  Данные: {record['line']}\n")
                f.write(f"  Причина: {record['error']}\n")
        else:
            f.write("Ошибок не обнаружено\n")
    
    return full_report_path

while True:
    file_path = input("\nВведите путь к файлу: ").strip()
    
    if not file_path:
        print("Ошибка! Вы не указали путь к файлу.")
        continue
    
    if not os.path.isfile(file_path):
        print(f"Ошибка! Файл '{file_path}' не найден.")
        print("Пожалуйста, проверьте путь и попробуйте снова.")
        continue
    
    #если файл найден - выходим из цикла
    break

#определение разделителя
print("\nОпределение разделителя...")
delimiter, expected_field_count = detect_delimiter(file_path)

if expected_field_count == 0:
    print("Не удалось определить структуру файла.")
    delimiter = ','
    expected_field_count = 3
    print(f"Используются значения по умолчанию: разделитель '{delimiter}', {expected_field_count} полей")
else:
    print(f"Автоматически определен разделитель: '{delimiter}'")
    print(f"Ожидаемое количество полей: {expected_field_count}")

#ручной ввод разделителя
change = input("\nИзменить разделитель? (y/n): ").strip().lower()
if change == 'y':
    new_delimiter = input(f"Введите новый разделитель (текущий: '{delimiter}'): ").strip()
    if new_delimiter:
        delimiter = new_delimiter
        print(f"Установлен разделитель: '{delimiter}'")

#коррекция полей
print(f"\nФайл содержит {expected_field_count} полей.")

#автоматическое определение названий столбцов
print("\nАвтоматическое определение названий столбцов...")
suggested_names = suggest_column_names(expected_field_count, delimiter, file_path)
print(f"Предложенные названия: {', '.join(suggested_names)}")

field_names_input = input("\nВведите свои названия полей через запятую\n(или Enter для принятия предложенных): ").strip()

if field_names_input:
    field_names = [name.strip() for name in field_names_input.split(',')]
    if len(field_names) != expected_field_count:
        print(f"Указано {len(field_names)} названий, нужно {expected_field_count}")
        print("Используются предложенные названия")
        field_names = suggested_names
else:
    field_names = suggested_names

print(f"Установлены названия полей: {', '.join(field_names)}")

#автоматическое определение типов данных
print("\nАвтоматическое определение типов данных...")
suggested_types = detect_column_types(file_path, delimiter)
print(f"Предложенные типы: {', '.join(suggested_types)}")

field_types_input = input("\nВведите свои типы данных через запятую (int, float, string)\n(или Enter для принятия предложенных): ").strip()

if field_types_input:
    field_types = [t.strip().lower() for t in field_types_input.split(',')]
    type_map = {'int': 'int', 'integer': 'int',
                'float': 'float', 'decimal': 'float',
                'string': 'string', 'str': 'string'}
    
    field_types = [type_map.get(t, 'string') for t in field_types]
    
    #проверяем количество типов
    if len(field_types) != expected_field_count:
        print(f"Указано {len(field_types)} типов, нужно {expected_field_count}")
        print("Используются предложенные типы")
        field_types = suggested_types
    else:
        print(f"Установлены типы: {', '.join(field_types)}")
else:
    field_types = suggested_types
    print(f"Установлены предложенные типы: {', '.join(field_types)}")

print(f"\nЗапущена обработка файла...")

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        correct_records = []
        incorrect_records = []
        total_lines = 0
        
        #пропускаем первую строку, если она была использована как заголовки
        first_line_skipped = False
        if field_names == suggested_names and len(suggested_names) == expected_field_count:
            #проверяем, не была ли первая строка заголовками
            try:
                f.seek(0)
                first_line = f.readline().strip()
                if first_line:
                    first_parts = first_line.split(delimiter)
                    first_parts = [p.strip() for p in first_parts if p.strip()]
                    if first_parts == field_names:
                        first_line_skipped = True
                        print("Первая строка распознана как заголовки - пропускается")
            except:
                pass
        
        #возвращаемся к началу файла
        f.seek(0)
        if first_line_skipped:
            next(f)  #пропускаем первую строку
        
        for line_num, line in enumerate(f, start=2 if first_line_skipped else 1):
            line = line.strip()
            if not line:
                continue
            
            total_lines += 1
            
            #разделение строки
            parts = line.split(delimiter)
            parts = [p.strip() for p in parts]
            
            #проверка количества полей
            if len(parts) != expected_field_count:
                incorrect_records.append({
                    'line_num': line_num,
                    'line': line,
                    'error': f"Неверное количество полей: {len(parts)} вместо {expected_field_count}"
                })
                continue
            
            #проверка каждого поля
            record_errors = []
            record_data = {}
            
            for field_name, field_type, value in zip(field_names, field_types, parts):
                errors, converted = validate_field(field_name, value, field_type)
                
                if errors:
                    for error in errors:
                        record_errors.append(f"{field_name}: {error}")
                else:
                    record_data[field_name] = converted
            
            #разделение на корректные и ошибочные
            if record_errors:
                incorrect_records.append({
                    'line_num': line_num,
                    'line': line,
                    'error': "; ".join(record_errors)
                })
            else:
                correct_records.append(record_data)
        
        #вывод ошибок
        print(f"\nОбработка завершена!")
        print(f"\nВсего записей: {total_lines}")
        print(f"Корректных: {len(correct_records)}")
        print(f"Некорректных: {len(incorrect_records)}")
        
        if incorrect_records:
            print(f"\nПримеры ошибок:")
            for record in incorrect_records[:3]:
                print(f"  Строка {record['line_num']}: {record['line']}")
                print(f"    → {record['error']}")
        
        print(f"\nСохранение отчета...")
        report_file = save_report(file_path, total_lines, 
                                 len(correct_records), len(incorrect_records),
                                 incorrect_records)
        
        print(f"Отчет сохранен в файл: {report_file}")
        
        print(f"\nСодержание отчета:")
        print("\n")
        with open(report_file, 'r', encoding='utf-8') as report:
            for line in report:
                print(line.rstrip())

except FileNotFoundError:
    print(f"Ошибка! Файл '{file_path}' не найден.")
    exit(1)
except Exception as e:
    print(f"Ошибка при обработке: {e}")
    exit(1)