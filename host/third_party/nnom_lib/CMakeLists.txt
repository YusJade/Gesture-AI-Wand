
project(NNoM LANGUAGES C)

file(GLOB BACKENDS_SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/src/backends/*.c)
file(GLOB CORE_SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/src/core/*.c)
file(GLOB LAYERS_SOURCES ${CMAKE_CURRENT_SOURCE_DIR}/src/layers/*.c)

add_library(NNoM 
  ${BACKENDS_SOURCES}
  ${CORE_SOURCES}
  ${LAYERS_SOURCES}
)

target_include_directories(NNoM PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/inc
  ${CMAKE_CURRENT_SOURCE_DIR}/port
)
target_compile_options(NNoM PUBLIC
  -Wno-narrowing
)