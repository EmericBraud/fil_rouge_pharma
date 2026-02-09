cmake_minimum_required(VERSION 3.16)

project(fil_rouge VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ------------------------------------------------------------------
# Threads
# ------------------------------------------------------------------
find_package(Threads REQUIRED)

# ------------------------------------------------------------------
# Options
# ------------------------------------------------------------------
option(BUILD_PYTHON "Build Python module" ON)

# ------------------------------------------------------------------
# Core library
# ------------------------------------------------------------------
file(GLOB_RECURSE CORE_SOURCES CONFIGURE_DEPENDS "src/*.cpp")
list(FILTER CORE_SOURCES EXCLUDE REGEX "main.cpp")

add_library(fil_rouge_core SHARED ${CORE_SOURCES})
target_link_libraries(fil_rouge_core PUBLIC 
    sfml-graphics 
    sfml-window 
    sfml-system
    Threads::Threads
)
target_include_directories(fil_rouge_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}       # pour les headers racine (shelf.hpp, slot.hpp, ...)
    ${CMAKE_CURRENT_SOURCE_DIR}/src   # pour les headers dans src/
)
target_compile_options(fil_rouge_core PRIVATE -Wall -Wextra)


# ------------------------------------------------------------------
# Python bindings
# ------------------------------------------------------------------

if(BUILD_PYTHON)
    find_package(Python3 COMPONENTS Interpreter Development REQUIRED)
endif()

if(BUILD_PYTHON)
    include(FetchContent)

    FetchContent_Declare(
      pybind11
      GIT_REPOSITORY https://github.com/pybind/pybind11.git
      GIT_TAG v2.11.1
    )
    FetchContent_MakeAvailable(pybind11)

    pybind11_add_module(fil_rouge_py
        bindings/python_bindings.cpp
    )

    # inclure TOUS les headers du projet
    target_include_directories(fil_rouge_py PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}       # wh_core
        ${CMAKE_CURRENT_SOURCE_DIR}/src   # src si tu as des headers là
        ${CMAKE_CURRENT_SOURCE_DIR}/wh_core # si tes headers sont dans un sous-dossier wh_core
        ${Python3_INCLUDE_DIRS}           # <-- ajoute ceci pour Python.h
    )

    target_link_libraries(fil_rouge_py PRIVATE fil_rouge_core Python3::Python pybind11::module)

    find_program(PYBIND11_STUBGEN pybind11-stubgen)
    
    if(PYBIND11_STUBGEN)
       add_custom_command(
            TARGET fil_rouge_py POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E env "PYTHONPATH=$<TARGET_FILE_DIR:fil_rouge_py>" ${PYBIND11_STUBGEN} fil_rouge_py --output-dir $<TARGET_FILE_DIR:fil_rouge_py>
            COMMENT "Génération du .pyi directement à côté du .so..."
            VERBATIM
        )
    else()
        message(WARNING "pybind11-stubgen non trouvé. L'autocomplétion Python ne fonctionnera pas parfaitement. (pip install pybind11-stubgen)")
    endif()

endif()

# ------------------------------------------------------------------
# GoogleTest
# ------------------------------------------------------------------
include(FetchContent)

FetchContent_Declare(
  googletest
  URL https://github.com/google/googletest/archive/refs/tags/release-1.12.1.zip
)

set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
FetchContent_MakeAvailable(googletest)

enable_testing()

file(GLOB_RECURSE TEST_SOURCES CONFIGURE_DEPENDS "tests/*.cpp")
add_executable(tests ${TEST_SOURCES})
target_link_libraries(tests PRIVATE
    fil_rouge_core
    gtest_main
    Threads::Threads
)
include(GoogleTest)
gtest_discover_tests(tests)
