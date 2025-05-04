# CMakeLists.txt

# Dòng 1: Yêu cầu version CMake tối thiểu
cmake_minimum_required(VERSION 3.12)

# Dòng 2: Tên dự án
project(END LANGUAGES CXX)

# Cấu hình C++ Standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Tìm Python và Pybind11
find_package(Python REQUIRED COMPONENTS Interpreter Development)
find_package(pybind11 REQUIRED)

# --- Dòng này phải xuất hiện trước các target_... lệnh cho 'game_engine' ---
# Dòng N: Tạo target module Python có tên là 'game_engine'
# pybind11_add_module(Tên target Python source1.cpp source2.cpp ...)
pybind11_add_module(game_engine ComputeMove.cpp heuristic.cpp)

# --- Các target_... lệnh cho 'game_engine' sẽ nằm sau dòng N này ---

# Dòng 13 (hoặc dòng sau N): Thêm include directories cho target 'game_engine'
# target_include_directories(Tên target PHẠM VI đường dẫn include)
target_include_directories(game_engine PRIVATE ${CMAKE_SOURCE_DIR}) # Hoặc đường dẫn include thực tế của bạn

# Link thư viện cho target 'game_engine'
target_link_directories(game_engine PRIVATE C:/Users/nvtqx/AppData/Local/Programs/Python/Python313/libs/)

# ... (các lệnh khác nếu có)