cmake_minimum_required(VERSION 3.15)
project(NeuralBlitz VERSION 50.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -O3 -march=native")
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -g -O0 -fsanitize=address,undefined")
set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -O3 -DNDEBUG")

option(BUILD_SHARED_LIBS "Build shared libraries" ON)
option(ENABLE_OPENSSL "Enable OpenSSL crypto support" ON)
option(ENABLE_TESTS "Build test suite" ON)

find_package(Threads REQUIRED)
find_package(OpenSSL)

include_directories(${CMAKE_CURRENT_SOURCE_DIR}/include)

set(NEURALBLITZ_SOURCES
    src/main.cpp
)

add_executable(neuralblitz ${NEURALBLITZ_SOURCES})

target_link_libraries(neuralblitz
    PRIVATE
        Threads::Threads
        $<$<BOOL:${ENABLE_OPENSSL}>:OpenSSL::SSL>
        $<$<BOOL:${ENABLE_OPENSSL}>:OpenSSL::Crypto>
)

target_compile_definitions(neuralblitz PRIVATE
    $<$<BOOL:${ENABLE_OPENSSL}>:NEURALBLITZ_CRYPTO_ENABLED>
)

install(TARGETS neuralblitz DESTINATION bin)

file(GLOB_RECURSE HEADERS 
    "${CMAKE_CURRENT_SOURCE_DIR}/include/*.hpp"
)

install(FILES ${HEADERS} DESTINATION include/neuralblitz)

if(ENABLE_TESTS)
    enable_testing()
    
    add_executable(test_neuralblitz 
        tests/test_agent.cpp
        tests/test_task.cpp
        tests/test_governance.cpp
    )
    
    target_link_libraries(test_neuralblitz
        PRIVATE
            Threads::Threads
            $<$<BOOL:${ENABLE_OPENSSL}>:OpenSSL::SSL>
            $<$<BOOL:${ENABLE_OPENSSL}>:OpenSSL::Crypto>
    )
    
    add_test(NAME NeuralBlitzTests COMMAND test_neuralblitz)
endif()

message(STATUS "NeuralBlitz v50.0 Configuration")
message(STATUS "  Version: ${PROJECT_VERSION}")
message(STATUS "  C++ Standard: ${CMAKE_CXX_STANDARD}")
message(STATUS "  OpenSSL: ${ENABLE_OPENSSL}")
message(STATUS "  Build Tests: ${ENABLE_TESTS}")
