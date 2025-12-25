import os
import shutil
import re

TESTS_DIR = "tests_split"
SERVER_DIR = "server"

# 3 буквы после ТЕСТ_
TEST_FILE_REGEX = re.compile(r"^ТЕСТ_([А-ЯA-ZЁ]{3})", re.IGNORECASE)
FOLDER_CODE_REGEX = re.compile(r"^([А-ЯA-ZЁ]{3})")

tests_map = {}

# --- собираем тесты ---
for file in os.listdir(TESTS_DIR):
    if not file.lower().endswith(".docx"):
        continue

    match = TEST_FILE_REGEX.match(file)
    if not match:
        continue

    code = match.group(1)
    tests_map[code] = os.path.join(TESTS_DIR, file)

print(f"Найдено тестов: {len(tests_map)}")

# --- проходим server ---
for topic in os.listdir(SERVER_DIR):
    topic_path = os.path.join(SERVER_DIR, topic)
    if not os.path.isdir(topic_path):
        continue

    for subfolder in os.listdir(topic_path):
        subfolder_path = os.path.join(topic_path, subfolder)
        if not os.path.isdir(subfolder_path):
            continue

        folder_match = FOLDER_CODE_REGEX.match(subfolder)
        if not folder_match:
            continue

        code = folder_match.group(1)

        if code in tests_map:
            src = tests_map[code]
            dst = os.path.join(subfolder_path, os.path.basename(src))

            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                print(f"✔ {code} → {subfolder_path}")
            else:
                print(f"⚠ Уже есть: {dst}")

print("Готово.")
