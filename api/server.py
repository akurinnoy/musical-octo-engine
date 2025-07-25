# api/server.py
import subprocess
import os
import threading
from queue import Queue, Empty

class BitNetInference:
    """
    Керує постійним інтерактивним підпроцесом для виконуваного файлу BitNet C++.
    Цей клас призначений для одноразового завантаження моделі та взаємодії з нею через stdin/stdout.
    """
    def __init__(self):
        # Визначаємо шляхи відносно кореня проєкту
        self.executable_path = os.path.abspath('./BitNet/build/bin/chat')
        self.model_path = os.path.abspath('./models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf')
        self.process = None
        self.output_queue = Queue()
        self.lock = threading.Lock() # Для безпечної обробки одночасних запитів

    def start_process(self):
        """Запускає та ініціалізує підпроцес C++."""
        if not os.path.exists(self.executable_path):
            raise FileNotFoundError(f"Виконуваний файл не знайдено: {self.executable_path}. Будь ласка, спершу запустіть задачу 'prepare-environment'.")
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Файл моделі не знайдено: {self.model_path}. Будь ласка, спершу запустіть задачу 'prepare-environment'.")

        # Команда для запуску інтерактивного чату. Прапори базуються на офіційному скрипті run_inference.py.
        command = [
            self.executable_path,
            "-m", self.model_path,
            "-i"
        ]

        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )

        # Потік для читання stdout без блокування основного потоку
        thread = threading.Thread(target=self._read_output)
        thread.daemon = True
        thread.start()

        self._wait_for_prompt()
        print("Модель BitNet завантажена і готова до роботи.")

    def _read_output(self):
        """Читає вивід з процесу і додає його в чергу."""
        for line in iter(self.process.stdout.readline, ''):
            self.output_queue.put(line)

    def _wait_for_prompt(self, timeout=180):
        """Очікує на початковий індикатор готовності ('>') від процесу."""
        output = ""
        # Ми читаємо рядки, доки не побачимо символ запрошення, що свідчить про готовність.
        while not output.strip().endswith('>'):
            try:
                output += self.output_queue.get(timeout=timeout)
            except Empty:
                raise TimeoutError("Процес BitNet не відповів вчасно під час завантаження моделі.")

    def generate(self, prompt: str) -> str:
        """Надсилає промпт до моделі та отримує відповідь."""
        with self.lock:
            if not self.process or self.process.poll() is not None:
                raise RuntimeError("Процес BitNet не запущено.")

            self.process.stdin.write(prompt + '\n')
            self.process.stdin.flush()

            response_lines = []
            while True:
                line = self.output_queue.get()
                # Застосунок C++ друкує '>' у новому рядку, коли готовий до наступного вводу.
                if line.strip() == '>':
                    break
                response_lines.append(line)
            
            # Відповідь може містити відлуння промпту, яке ми можемо обрізати.
            full_response = "".join(response_lines).strip()
            return full_response

    def stop_process(self):
        """Зупиняє підпроцес C++."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("Процес BitNet зупинено.")

# Створюємо єдиний глобальний екземпляр для використання додатком FastAPI
bitnet_inference_server = BitNetInference()
