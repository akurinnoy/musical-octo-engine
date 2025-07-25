#!/bin/bash

# Скрипт для завантаження попередньо навченої моделі BitNet з Hugging Face.

# Визначення змінних
MODEL_REPO="microsoft/bitnet-b1.58-2B-4T-gguf"
MODEL_DIR="models/BitNet-b1.58-2B-4T"

# Створення директорії для моделі, якщо вона не існує
echo "Створення директорії для моделі: $MODEL_DIR"
mkdir -p $MODEL_DIR

# Завантаження моделі за допомогою huggingface-cli
# Використовуємо --local-dir-use-symlinks False для уникнення проблем із символічними посиланнями в контейнері
echo "Завантаження моделі $MODEL_REPO..."
huggingface-cli download $MODEL_REPO --local-dir $MODEL_DIR --local-dir-use-symlinks False

echo "Завантаження моделі завершено."
