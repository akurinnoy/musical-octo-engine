# Використовуємо Ubuntu 22.04 як базовий образ для кращого контролю над системними залежностями
FROM ubuntu:22.04

# Уникаємо інтерактивних запитів під час встановлення пакетів
ENV DEBIAN_FRONTEND=noninteractive

# Встановлюємо базові залежності: інструменти для збірки, git, python та утиліти
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    wget \
    ca-certificates \
    gnupg \
    python3 \
    python3-pip \
    python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Встановлюємо актуальну версію Clang (BitNet вимагає >=18)
# Додаємо репозиторій LLVM APT
RUN wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | gpg --dearmor -o /etc/apt/trusted.gpg.d/llvm-archive-keyring.gpg && \
    echo "deb http://apt.llvm.org/jammy/ llvm-toolchain-jammy-18 main" >> /etc/apt/sources.list.d/llvm.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends clang-18 libc++-18-dev libc++abi-18-dev && \
    rm -rf /var/lib/apt/lists/*

# Встановлюємо clang-18 як компілятор C/C++ за замовчуванням
RUN update-alternatives --install /usr/bin/cc cc /usr/bin/clang-18 100 && \
    update-alternatives --install /usr/bin/c++ c++ /usr/bin/clang++-18 100

# Створюємо робочу директорію
WORKDIR /projects/workspace

# Devfile змонтує вихідний код проєкту сюди.
# Ми не копіюємо вихідний код у Dockerfile, щоб зберегти образ загальним
# і дозволити devfile керувати монтуванням коду для розробки.