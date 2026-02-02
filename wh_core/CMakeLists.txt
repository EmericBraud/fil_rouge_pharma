cmake_minimum_required(VERSION 3.14)

project(fil_rouge VERSION 1.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)


# -------------------------------------------------------------------
# Threads (needed for Threads::Threads)
# -------------------------------------------------------------------
find_package(Threads REQUIRED)

# -------------------------------------------------------------------
# Sources
# -------------------------------------------------------------------
file(GLOB_RECURSE SOURCES "src/*.cpp")
list(FILTER SOURCES EXCLUDE REGEX "main.cpp")

add_library(fil_rouge_core STATIC ${SOURCES})
target_include_directories(fil_rouge_core PUBLIC src)

target_compile_options(fil_rouge_core PUBLIC
    $<$<COMPILE_LANGUAGE:CXX>:-Wall;-Wextra;-flto;-O3;-DNDEBUG;-march=native;-mbmi2;-fno-omit-frame-pointer;-mpopcnt>
)

# -------------------------------------------------------------------
# Executable fil_rouge
# -------------------------------------------------------------------
add_executable(fil_rouge src/main.cpp)
target_link_libraries(fil_rouge PRIVATE
    fil_rouge_core
    sfml-graphics
    sfml-window
    sfml-system
)

target_link_options(fil_rouge PRIVATE 
    $<$<CONFIG:Release>:-O3;-flto;-march=native>
    $<$<NOT:$<CONFIG:Release>>:-O3;-flto;-march=native>
)

# -------------------------------------------------------------------
# GoogleTest
# -------------------------------------------------------------------
include(FetchContent)
FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/tags/release-1.12.1.zip
)
set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

enable_testing()

file(GLOB_RECURSE TEST_SOURCES "tests/*.cpp")
add_executable(tests ${TEST_SOURCES})

target_include_directories(tests PRIVATE include)

target_link_libraries(tests PRIVATE
    fil_rouge_core
    gtest_main
    gtest
    Threads::Threads
)


include(GoogleTest)
gtest_discover_tests(tests)

