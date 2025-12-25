from docx import Document
import os
import re
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_FILE = os.path.join(BASE_DIR, "tests.docx")
OUTPUT_FILE = os.path.join(BASE_DIR, "tests.ts")

doc = Document(SOURCE_FILE)

TEST_RE = re.compile(r"^ТЕСТ\s+([А-ЯA-ZЁ]{3})")
QUESTION_RE = re.compile(r"^Задание\s*№\d+:\s*(.+)")
INSTRUCTION_RE = re.compile(r"^Инструкция:\s*(.+)")

tests = {}
current_test = None
questions = []
current_question = None

def flush_question():
    global current_question, questions
    if current_question:
        correct_count = sum(1 for a in current_question["answers"] if a["is_correct"])
        if correct_count > 1:
            current_question["qtype"] = "multiple"
        questions.append(current_question)
        current_question = None

def flush_test():
    global current_test, questions, tests
    if current_test:
        tests[current_test] = {"questions": questions}
        questions = []


def sanitize_name(name: str) -> str:
    # Преобразуем имя теста в валидное название переменной на английском
    name = name.upper()
    name = re.sub(r"[А-ЯЁ]", lambda m: {"А": "A", "Б": "B", "В": "V", "Г": "G", "Д": "D", "Е": "E", "Ж": "ZH",
                                        "З": "Z", "И": "I", "Й": "Y", "К": "K", "Л": "L", "М": "M",
                                        "Н": "N", "О": "O", "П": "P", "Р": "R", "С": "S", "Т": "T",
                                        "У": "U", "Ф": "F", "Х": "H", "Ц": "TS", "Ч": "CH", "Ш": "SH",
                                        "Щ": "SCH", "Ъ": "", "Ы": "Y", "Ь": "", "Э": "E", "Ю": "YU", "Я": "YA"}[m.group(0)], name)
    # Остальные символы заменяем на _
    name = re.sub(r"[^A-Z0-9_]", "_", name)
    return name

for p in doc.paragraphs:
    text = p.text.strip()
    if not text:
        continue

    m_test = TEST_RE.match(text)
    if m_test:
        flush_question()
        flush_test()
        current_test = sanitize_name(f"TEST_{m_test.group(1)}")
        continue

    m_q = QUESTION_RE.match(text)
    if m_q:
        flush_question()
        current_question = {
            "name": m_q.group(1).strip(),
            "instruction": "",
            "qtype": "single",
            "answers": []
        }
        continue

    if not current_question:
        continue

    m_instr = INSTRUCTION_RE.match(text)
    if m_instr:
        instr = m_instr.group(1).strip()
        current_question["instruction"] = instr
        if "можно выбрать несколько" in instr.lower():
            current_question["qtype"] = "multiple"
        continue

    is_correct = "✅" in text
    clean_text = text.replace("✅", "").strip("•●-❏□ ").strip()

    if clean_text:
        current_question["answers"].append({
            "text": clean_text,
            "is_correct": is_correct
        })

flush_question()
flush_test()

# --- сохранение в один TS файл ---
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("export const tests: any = {\n")
    for name, data in tests.items():
        json_str = json.dumps(data, ensure_ascii=False, indent=4)
        # добавляем отступы для красивого TS
        json_str = "\n".join("    " + line for line in json_str.splitlines())
        f.write(f"  '{name}': {json_str},\n")
    f.write("};\n")

print(f"Готово. Создано тестов: {len(tests)}")
