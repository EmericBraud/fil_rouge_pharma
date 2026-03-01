cmake_minimum_required(VERSION 3.16)

# Supprime le warning lié à FetchContent (CMP0135)
if(POLICY CMP0135)
  cmake_policy(SET CMP0135 NEW)
endif()

project(fil_rouge VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ------------------------------------------------------------------
# Dépendances Externes
# ------------------------------------------------------------------
find_package(Threads REQUIRED)
find_package(nlohmann_json REQUIRED)
# On cherche SFML explicitement
find_package(SFML 2.5 COMPONENTS graphics window system REQUIRED)

# ------------------------------------------------------------------
# Ressources (Data)
# ------------------------------------------------------------------
set(DATA_SRC "${CMAKE_CURRENT_SOURCE_DIR}/data")
if(EXISTS ${DATA_SRC})
    file(COPY ${DATA_SRC} DESTINATION ${CMAKE_CURRENT_BINARY_DIR})
endif()

# ------------------------------------------------------------------
# Core Library (fil_rouge_core)
# ------------------------------------------------------------------
file(GLOB_RECURSE CORE_SOURCES CONFIGURE_DEPENDS "src/*.cpp")

# Exclusion propre de main.cpp de la librairie pour éviter les doublons de symbole 'main'
foreach(_source ${CORE_SOURCES})
    if(_source MATCHES "main\\.cpp$")
        list(REMOVE_ITEM CORE_SOURCES ${_source})
    endif()
endforeach()

add_library(fil_rouge_core SHARED ${CORE_SOURCES})

target_link_libraries(fil_rouge_core PUBLIC 
    sfml-graphics 
    sfml-window 
    sfml-system
    Threads::Threads
    nlohmann_json::nlohmann_json
)

target_include_directories(fil_rouge_core PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_CURRENT_SOURCE_DIR}/src
)

target_compile_options(fil_rouge_core PRIVATE -Wall -Wextra)

# ------------------------------------------------------------------
# Main Application (L'exécutable principal)
# ------------------------------------------------------------------
# On s'assure que src/main.cpp existe bien à cet endroit
add_executable(app_exe src/main.cpp)
target_link_libraries(app_exe PRIVATE fil_rouge_core)

# Définit le nom final du fichier (./fil_rouge au lieu de ./app_exe)
set_target_properties(app_exe PROPERTIES OUTPUT_NAME "fil_rouge")

# ------------------------------------------------------------------
# Python Bindings
# ------------------------------------------------------------------
option(BUILD_PYTHON "Build Python module" ON)

if(BUILD_PYTHON)
    find_package(Python3 COMPONENTS Interpreter Development.Module REQUIRED)
    include(FetchContent)

    FetchContent_Declare(
      pybind11
      GIT_REPOSITORY https://github.com/pybind/pybind11.git
      GIT_TAG v2.11.1
    )
    FetchContent_MakeAvailable(pybind11)

    pybind11_add_module(fil_rouge_py bindings/python_bindings.cpp)

    target_include_directories(fil_rouge_py PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
        ${CMAKE_CURRENT_SOURCE_DIR}/src
    )

    target_link_libraries(fil_rouge_py PRIVATE fil_rouge_core)

    # Génération des stubs (.pyi) pour l'autocomplétion
    find_program(PYBIND11_STUBGEN pybind11-stubgen)
    if(PYBIND11_STUBGEN)
       add_custom_command(
            TARGET fil_rouge_py POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E env "PYTHONPATH=$<TARGET_FILE_DIR:fil_rouge_py>" 
                    ${PYBIND11_STUBGEN} fil_rouge_py --output-dir $<TARGET_FILE_DIR:fil_rouge_py>
            COMMENT "Génération des fichiers de stub Python (.pyi)"
            VERBATIM
        )
    endif()
endif()

# ------------------------------------------------------------------
# Tests (GoogleTest)
# ------------------------------------------------------------------
option(BUILD_TESTING "Build tests" ON)

if(BUILD_TESTING)
    include(FetchContent)
    FetchContent_Declare(
      googletest
      URL https://github.com/google/googletest/archive/refs/tags/release-1.12.1.zip
    )
    set(gtest_force_shared_crt ON CACHE BOOL "" FORCE)
    FetchContent_MakeAvailable(googletest)

    enable_testing()

    file(GLOB_RECURSE TEST_SOURCES CONFIGURE_DEPENDS "tests/*.cpp")
    
    if(TEST_SOURCES)
        add_executable(tests ${TEST_SOURCES})
        target_link_libraries(tests PRIVATE
            fil_rouge_core
            gtest_main
            Threads::Threads
        )
        include(GoogleTest)
        gtest_discover_tests(tests)
    endif()
endif()