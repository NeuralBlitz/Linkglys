cmake_minimum_required(VERSION 3.12)
project(NeuralBlitzC VERSION 1.0.0 LANGUAGES C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

# Compiler warnings
if(CMAKE_C_COMPILER_ID MATCHES "GNU|Clang")
    add_compile_options(-Wall -Wextra -Wpedantic -Wshadow -Wconversion)
endif()

# ── Library ──
set(SOURCES
    src/precision.c
    src/intent.c
    src/free_energy.c
    src/cognitive.c
    src/lens.c
    src/registry.c
    src/agent.c
    src/multi_agent.c
    src/plugin.c
    src/api.c
)

add_library(neuralblitz STATIC ${SOURCES})
target_include_directories(neuralblitz
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/src
)
target_link_libraries(neuralblitz PRIVATE m)

# ── Test executable ──
add_executable(test_neuralblitz tests/test_neuralblitz.c)
target_include_directories(test_neuralblitz PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(test_neuralblitz PRIVATE neuralblitz m)

# ── Test target ──
add_custom_target(test
    COMMAND test_neuralblitz
    DEPENDS test_neuralblitz
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
)

# ── Installation ──
include(GNUInstallDirs)
install(TARGETS neuralblitz
    ARCHIVE DESTINATION ${CMAKE_INSTALL_LIBDIR}
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
)
install(DIRECTORY include/neuralblitz
    DESTINATION ${CMAKE_INSTALL_INCLUDEDIR}
)

# ── Summary ──
message(STATUS "NeuralBlitz C ${PROJECT_VERSION}")
message(STATUS "  Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "  Compiler:   ${CMAKE_C_COMPILER_ID} ${CMAKE_C_COMPILER_VERSION}")
message(STATUS "  Install:    ${CMAKE_INSTALL_PREFIX}")
