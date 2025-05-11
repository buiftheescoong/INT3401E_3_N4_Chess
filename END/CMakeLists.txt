cmake_minimum_required(VERSION 3.15)
project(END)

# Yêu cầu C++17
set(CMAKE_CXX_STANDARD 17)

# Tìm Python và pybind11 (ưu tiên pybind11 nằm trong thư mục pybind11/)
# Nếu bạn cài pybind11 bằng pip thì có thể bỏ phần add_subdirectory
add_subdirectory(pybind11)

# Bao gồm thư mục header
include_directories(
        ${PROJECT_SOURCE_DIR}
        ${PROJECT_SOURCE_DIR}/chess
)

# Tạo module Python (.pyd)
pybind11_add_module(engine_binding
        bindings.cpp
        ComputeMove.cpp
        heuristic.cpp
        TranspositionTable.cpp
        chess/chess.cpp
)

# Nếu cần thư viện riêng (ví dụ như thêm các file heuristic.cpp...), thêm vào đây
# target_sources(engine_binding PRIVATE heuristic.cpp)