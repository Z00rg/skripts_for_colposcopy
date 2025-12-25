from docx import Document
import os
import re
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_FILE = os.path.join(BASE_DIR, "tests.docx")
OUTPUT_DIR = os.path.join(BASE_DIR, "tests_json")

os.makedirs(OUTPUT_DIR, exist_ok=True)

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
        # если несколько правильных → multiple
        correct_count = sum(1 for a in current_question["answers"] if a["is_correct"])
        if correct_count > 1:
            current_question["qtype"] = "multiple"
        questions.append(current_question)
        current_question = None

def flush_test():
    global current_test, questions
    if current_test:
        tests[current_test] = {"questions": questions}
        questions = []

for p in doc.paragraphs:
    text = p.text.strip()
    if not text:
        continue

    # --- ТЕСТ ---
    m_test = TEST_RE.match(text)
    if m_test:
        flush_question()
        flush_test()
        current_test = f"ТЕСТ_{m_test.group(1)}"
        continue

    # --- ВОПРОС ---
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

    # --- ИНСТРУКЦИЯ ---
    m_instr = INSTRUCTION_RE.match(text)
    if m_instr:
        instr = m_instr.group(1).strip()
        current_question["instruction"] = instr
        if "можно выбрать несколько" in instr.lower():
            current_question["qtype"] = "multiple"
        continue

    # --- ОТВЕТ (любой текст) ---
    is_correct = "✅" in text
    clean_text = text.replace("✅", "").strip("•●-❏□ ").strip()

    if clean_text:
        current_question["answers"].append({
            "text": clean_text,
            "is_correct": is_correct
        })

# финальный сброс
flush_question()
flush_test()

# --- сохранение ---
for name, data in tests.items():
    path = os.path.join(OUTPUT_DIR, f"{name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

print(f"Готово. Создано тестов: {len(tests)}")
