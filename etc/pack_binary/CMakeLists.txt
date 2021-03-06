cmake_minimum_required(VERSION 2.8)

#
# CPack Package Properties
#
set(CPACK_INCLUDE_TOPLEVEL_DIRECTORY 0)
IF (NOT PYTHON_ONLY_CLIENT)
    set(CPACK_PACKAGE_NAME "CVAC_binary")
    set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "CVAC binary install package")
ELSE (NOT PYTHON_ONLY_CLIENT)
    set(CPACK_PACKAGE_NAME "CVAC_client")
    set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "CVAC client install package")
ENDIF (NOT PYTHON_ONLY_CLIENT)

set(CPACK_PACKAGE_VENDOR "NPS Vision Lab")

IF( NOT DEFINED CVAC_VERSION_MAJOR )
    MESSAGE( FATAL_ERROR "Could not determine CVAC version" )
ENDIF( NOT DEFINED CVAC_VERSION_MAJOR )
set(CPACK_PACKAGE_VERSION_MAJOR ${CVAC_VERSION_MAJOR})
set(CPACK_PACKAGE_VERSION_MINOR ${CVAC_VERSION_MINOR})
set(CPACK_PACKAGE_VERSION_PATCH ${CVAC_VERSION_PATCH})
set(CPACK_PACKAGE_VERSION "${CPACK_PACKAGE_VERSION_MAJOR}.${CPACK_PACKAGE_VERSION_MINOR}.${CVAC_VERSION_PATCH}")
set( CVAC_VERSION_DIR ${CPACK_PACKAGE_NAME}-${CVAC_VERSION} )

# If devel branch, add -devel to version number
if( NOT EXISTS "${CMAKE_SOURCE_DIR}/.git" )
  MESSAGE( SEND_ERROR "Cannot create package without git repository" )
endif()
EXECUTE_PROCESS( COMMAND git rev-parse --abbrev-ref HEAD
    OUTPUT_VARIABLE CVAC_GIT_BRANCH
    OUTPUT_STRIP_TRAILING_WHITESPACE
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    )
IF ( NOT CVAC_GIT_BRANCH )
  MESSAGE( SEND_ERROR "Error obtaining git branch name; cannot create package" )
ENDIF()
set(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}-${CPACK_PACKAGE_VERSION}")

IF ( ${CVAC_GIT_BRANCH} STREQUAL "devel" )
  set(CPACK_PACKAGE_FILE_NAME ${CPACK_PACKAGE_FILE_NAME}-devel)
ENDIF()

# If Windows 8 then add -W8 to version
IF ( ${CMAKE_SYSTEM} STREQUAL "Windows-6.2" )
MESSAGE ("windows 8")
set(CVAC_VERSION_DIR ${CVAC_VERSION_DIR}-Win8)
set(CPACK_PACKAGE_VERSION ${CPACK_PACKAGE_VERSION}-Win8)
set(CPACK_PACKAGE_FILE_NAME ${CPACK_PACKAGE_FILE_NAME}-Win8)
ELSE ( ${CMAKE_SYSTEM} STREQUAL "Windows-6.2" )
IF (WIN32)
set(CVAC_VERSION_DIR ${CVAC_VERSION_DIR}-Win7)
set(CPACK_PACKAGE_VERSION ${CPACK_PACKAGE_VERSION}-Win7)
set(CPACK_PACKAGE_FILE_NAME ${CPACK_PACKAGE_FILE_NAME}-Win7)
ENDIF (WIN32)
ENDIF ( ${CMAKE_SYSTEM} STREQUAL "Windows-6.2" )

#Force the install directory (Required since windows will put spaces in name
set( CPACK_PACKAGE_INSTALL_DIRECTORY ${CVAC_VERSION_DIR} )

set( CPACK_RESOURCE_FILE_LICENSE ${CMAKE_SOURCE_DIR}/LICENSE.txt )
set(CPACK_COMPONENTS_ALL Runtime data ThirdParty doc)
set(CPACK_COMPONENT_CORE_DISPLAY_NAME "CVAC core runtime components")
set(CPACK_COMPONENT_3RDPARTY_DISPLAY_NAME "CVAC 3rd Party" )
set(CPACK_COMPONENT_DATA_DISPLAY_NAME "CVAC sample data" )
set(CPACK_COMPONENT_DOC_DISPLAY_NAME "CVAC documentation" )

IF (WIN32) 
    set(CPACK_PACKAGE_FILE_NAME ${CPACK_PACKAGE_FILE_NAME}-win32)
ELSE (WIN32)
    set(CPACK_PACKAGE_FILE_NAME ${CPACK_PACKAGE_FILE_NAME}-${CMAKE_SYSTEM_NAME})
ENDIF (WIN32)

# change the install prefix to CVAC-version, since CPack will install into a zip-style archive
# set(CPACK_SET_DESTDIR true)
# set(CPACK_INSTALL_PREFIX ${CVAC_VERSION_DIR} ) 
# Binary distribution of CVAC: only built files, binary dependencies, 
# python install distribution (containing ice, easy, and cvac, python client 
# files), c++ client files (detectorClient and trainerClient).  
# Everything required to run CVAC without building from source.  
# We need to copy cvac, Ice, and easy to the build directory for packing 
# python distribution.  
# Select Generator by OS
IF(WIN32)
    SET( SCRIPT_EXT bat )
    SET(CPACK_GENERATOR "NSIS")
    # Specify the default location to install CVAC.  It will install it
    # in this and a version directory underneath this.
    SET(CPACK_NSIS_INSTALL_ROOT "c:\\\\EasyCV")
    # install gui.py startup script
    INSTALL(FILES ${CMAKE_CURRENT_SOURCE_DIR}/winstart.bat ${CMAKE_CURRENT_SOURCE_DIR}/EasyComputerVision.ico
        DESTINATION bin
        COMPONENT Runtime
        )
ELSEIF(APPLE)
    SET( SCRIPT_EXT sh )
    SET(CPACK_GENERATOR "Bundle")
    SET(CPACK_BUNDLE_NAME "EasyComputerVision")
    INSTALL(FILES ${CMAKE_CURRENT_SOURCE_DIR}/installNumpy.py  ${CMAKE_CURRENT_SOURCE_DIR}/startup.py
       DESTINATION ../MacOS
       COMPONENT Runtime 
    )
    SET(CPACK_BUNDLE_PLIST ${CMAKE_CURRENT_BINARY_DIR}/Info.plist)
    # CMake renames the startup command file to ${CPACK_BUNDLE_NAME}
    SET(CPACK_BUNDLE_STARTUP_COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/startup.sh)
    SET(CPACK_BUNDLE_ICON ${CMAKE_CURRENT_SOURCE_DIR}/EasyComputerVision.icns)
    SET(CPACK_PACKAGE_ICON ${CMAKE_CURRENT_SOURCE_DIR}/EasyComputerVision.icns)
    CONFIGURE_FILE( ${CMAKE_CURRENT_SOURCE_DIR}/Info.plist.in
      ${CMAKE_CURRENT_BINARY_DIR}/Info.plist)
ELSE()
    SET( SCRIPT_EXT sh )
    SET(CPACK_GENERATOR "TGZ")
ENDIF()

SET (PYTHON_BUILD_DIR "${CMAKE_CURRENT_BINARY_DIR}/../python")
INSTALL(DIRECTORY ${PYTHON_BUILD_DIR}
       DESTINATION .
       COMPONENT Runtime 
      )

INSTALL(DIRECTORY ${CMAKE_SOURCE_DIR}/data/corpus
       DESTINATION data
       COMPONENT data
      )
      
INSTALL(DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/../../doc
       DESTINATION .
       COMPONENT doc
      )
      
SET (DDATA ${CMAKE_SOURCE_DIR}/data/detectors )
INSTALL(FILES ${DDATA}/bowCorporateLogoModel.zip ${DDATA}/bowUSKOCA.zip ${DDATA}/OpencvFaces.zip ${DDATA}/haarcascade_frontalface_alt.xml
       DESTINATION data/detectors
       COMPONENT data
      )
      
INSTALL(DIRECTORY ${CMAKE_SOURCE_DIR}/data/trainImg/ca
       DESTINATION data/trainImg
       COMPONENT data
      )

INSTALL(DIRECTORY ${CMAKE_SOURCE_DIR}/data/trainImg/kr
       DESTINATION data/trainImg
       COMPONENT data
      )

INSTALL(DIRECTORY ${CMAKE_SOURCE_DIR}/data/trainImg/us
       DESTINATION data/trainImg
       COMPONENT data
      )
      
      
INSTALL(DIRECTORY ${CMAKE_SOURCE_DIR}/data/testImg
       DESTINATION data
       COMPONENT data
      )
      
INSTALL(DIRECTORY ${CMAKE_SOURCE_DIR}/data/corporate_logos
       DESTINATION data
       COMPONENT data
      )
      
INSTALL(FILES ${CMAKE_SOURCE_DIR}/include/version.h
       DESTINATION include
       COMPONENT Runtime
      )

INSTALL(FILES ${CMAKE_SOURCE_DIR}/test/run_demos.py 
       DESTINATION test
       COMPONENT Runtime
      )

# ThirdParty dependencies for building CVAC

IF (WIN32)

  INSTALL(DIRECTORY   ${ICE_ROOT}/bin
        DESTINATION 3rdparty/ICE
        USE_SOURCE_PERMISSIONS
        COMPONENT ThirdParty
        PATTERN icestorm* EXCLUDE
        PATTERN icegrid* EXCLUDE
        PATTERN *d.dll EXCLUDE
        PATTERN *.exe EXCLUDE
        PATTERN *.pdb EXCLUDE
        )
  IF (NOT PYTHON_ONLY_CLIENT)
    INSTALL(DIRECTORY   ${ICE_ROOT}/lib
        DESTINATION 3rdparty/ICE
        USE_SOURCE_PERMISSIONS
        COMPONENT ThirdParty
        PATTERN *.pdb EXCLUDE
        PATTERN *.lib EXCLUDE
       )
  ENDIF (NOT PYTHON_ONLY_CLIENT)


  INSTALL(FILES ${CMAKE_SOURCE_DIR}/3rdparty/numpy-1.8.1-sse3.exe
       DESTINATION 3rdparty
       COMPONENT Runtime 
      )

  INSTALL(FILES ${CMAKE_SOURCE_DIR}/3rdparty/python-2.7.8.msi
       DESTINATION 3rdparty
       COMPONENT Runtime 
      )

  INSTALL(DIRECTORY ${CMAKE_SOURCE_DIR}/3rdparty/virtualenv-1.11.6
       DESTINATION 3rdparty
       COMPONENT Runtime 
      )

  INSTALL(FILES ${CMAKE_SOURCE_DIR}/3rdparty/Pillow-2.6.0-cp27-none-win32.zip
       DESTINATION 3rdparty
       COMPONENT Runtime 
      )

IF (NOT PYTHON_ONLY_CLIENT)
  INSTALL(DIRECTORY ${CMAKE_SOURCE_DIR}/3rdparty/libsvm
       DESTINATION 3rdparty
       COMPONENT Runtime 
       PATTERN *.py
       PATTERN *.${CMAKE_SHARED_LIBRARY_SUFFIX}
      )
ENDIF (NOT PYTHON_ONLY_CLIENT)

ELSE (WIN32)

  IF (APPLE)
      INSTALL(FILES ${CMAKE_SOURCE_DIR}/3rdparty/numpy-1.8.1-cp27-none-any.whl
           DESTINATION 3rdparty
           COMPONENT Runtime 
      )

      INSTALL(DIRECTORY ${CMAKE_SOURCE_DIR}/3rdparty/virtualenv-1.11.6
           DESTINATION 3rdparty
           COMPONENT Runtime 
      )
      INSTALL(FILES ${CMAKE_SOURCE_DIR}/3rdparty/Pillow-2.6.0-cp27-none-macosx.zip
           DESTINATION 3rdparty
           COMPONENT Runtime 
      )
      IF (NOT PYTHON_ONLY_CLIENT)
        INSTALL(DIRECTORY ${CMAKE_SOURCE_DIR}/3rdparty/libsvm
           DESTINATION 3rdparty
           COMPONENT Runtime 
           PATTERN *.py
           PATTERN *.${CMAKE_SHARED_LIBRARY_SUFFIX}
        )
      ENDIF (NOT PYTHON_ONLY_CLIENT)

  ENDIF (APPLE)

  INSTALL(DIRECTORY   ${ICE_ROOT}/lib
        DESTINATION 3rdparty/ICE
        USE_SOURCE_PERMISSIONS
        COMPONENT ThirdParty
        PATTERN *.pdb EXCLUDE
       )

ENDIF (WIN32)

#Need ice python for everyone
INSTALL(DIRECTORY   ${ICE_ROOT}/python
        DESTINATION 3rdparty/ICE
        USE_SOURCE_PERMISSIONS
        COMPONENT ThirdParty
        PATTERN *.pyc EXCLUDE
       )

IF (NOT PYTHON_ONLY_CLIENT)
    INSTALL(PROGRAMS ${CMAKE_SOURCE_DIR}/3rdparty/ICE/bin/icebox${CMAKE_EXECUTABLE_SUFFIX}
                 ${ICE_BOX_ADMIN}
        DESTINATION 3rdparty/ICE/bin
        COMPONENT ThirdParty
       )

    # libarchive is a symlink, but we want the file:
    # CONFIGURE_FILE( ${LIBARCHIVE_LIBRARY} ${CMAKE_CURRENT_BINARY_DIR}/tmp/ COPYONLY)
    GET_FILENAME_COMPONENT( LIBARCHIVE_LIBRARY_REALPATH ${LIBARCHIVE_LIBRARY} REALPATH )
    IF (WIN32)
    INSTALL(DIRECTORY ${CMAKE_SOURCE_DIR}/3rdparty/libarchive/bin
       DESTINATION 3rdparty/libarchive
       COMPONENT ThirdParty
      )
    ELSEIF (NOT APPLE)
    INSTALL(FILES ${LIBARCHIVE_LIBRARY} ${LIBARCHIVE_LIBRARY_REALPATH}
       DESTINATION 3rdparty/libarchive/lib
       COMPONENT ThirdParty
      )
    ENDIF (WIN32)

    # OpenCV needs to be isolated in some staging area.  You need
    # to configure this CMake to pull OpenCV from there.
    # OpenCV_DIR points to the shared/OpenCV subdirectory.
    IF( WIN32 )
      GET_FILENAME_COMPONENT( OpenCV_INSTALL_PATH "${OpenCV_DIR}" REALPATH)
    ELSE( WIN32 )
      GET_FILENAME_COMPONENT( OpenCV_INSTALL_PATH "${OpenCV_DIR}/../.." REALPATH)
    ENDIF( WIN32 )
    MESSAGE( STATUS "OpenCV will be 3rd-party archived from this path: ${OpenCV_INSTALL_PATH}" )

ENDIF (NOT PYTHON_ONLY_CLIENT)

# First copy over cvac.  Need to wait for build time since these files
# are created by slicing at build time.  Since FILE commands work at
# cmake time we add a custom target that will copy each of the slice generated
# .py files to the python build cvac directory (which is required for 
# setup py).  The ALL causes the copySlice target 
# to be executed for all targets but we really only need them
# for the package target so we limit this to building
# the binary package and the install copies them with the install script
IF (BUILD_BINARY_PACKAGE)

    WRAP_SLICE2PY( SLICE_FILES
        ${CMAKE_SOURCE_DIR}/src/Files.ice
        ${CMAKE_SOURCE_DIR}/src/Data.ice
        ${CMAKE_SOURCE_DIR}/src/Services.ice
        ${CMAKE_SOURCE_DIR}/src/Corpus.ice
    )
    SET (SLICE_OUTPUT_PATH "${SLICE_OUTPUT_PYTHONDIR}")
    add_custom_target(copyslice ALL
        COMMAND ${CMAKE_COMMAND} -E copy "${SLICE_OUTPUT_PATH}/Corpus_ice.py" "${PYTHON_BUILD_DIR}/easyPkg/cvac"
        COMMAND ${CMAKE_COMMAND} -E copy "${SLICE_OUTPUT_PATH}/Data_ice.py" "${PYTHON_BUILD_DIR}/easyPkg/cvac"
        COMMAND ${CMAKE_COMMAND} -E copy "${SLICE_OUTPUT_PATH}/Files_ice.py" "${PYTHON_BUILD_DIR}/easyPkg/cvac"
        COMMAND ${CMAKE_COMMAND} -E copy "${SLICE_OUTPUT_PATH}/Services_ice.py" "${PYTHON_BUILD_DIR}/easyPkg/cvac"
        COMMAND ${CMAKE_COMMAND} -E copy "${SLICE_OUTPUT_PATH}/cvac/__init__.py" "${PYTHON_BUILD_DIR}/easyPkg/cvac"
        COMMAND ${CMAKE_COMMAND} -E copy "${SLICE_OUTPUT_PATH}/cvac/__init__.py" "${PYTHON_BUILD_DIR}/easyPkg/cvac"
        DEPENDS ${SLICE_OUTPUT_PATH}/Corpus_ice.py ${SLICE_OUTPUT_PATH}/Data_ice.py ${SLICE_OUTPUT_PATH}/Files_ice.py ${SLICE_OUTPUT_PATH}/Services_ice.py 
    )
    add_dependencies(copyslice doc)

ENDIF (BUILD_BINARY_PACKAGE)

INCLUDE (UserCMakeLists.txt OPTIONAL)

include(CPack)
