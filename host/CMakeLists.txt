cmake_minimum_required(VERSION 3.12)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_BUILD_TYPE DEBUG)

project(SpellingHost
  VERSION 0.1
  LANGUAGES CXX
)

add_subdirectory(third_party)

set(SOURCES 
  ${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp
)
add_executable(InferOnHost ${SOURCES})
target_link_libraries(InferOnHost PUBLIC
  NNoM
)
target_include_directories(InferOnHost PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include
)