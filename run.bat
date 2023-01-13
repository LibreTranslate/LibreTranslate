@ECHO OFF

SETLOCAL

SET LT_PORT=5000

:loop
IF NOT "%1"=="" (
    IF "%1"=="--port" (
        SET LT_PORT=%2
        SHIFT
    )
    IF "%1"=="--help" (
        echo Usage: run.bat [--port N]
        echo:
        echo Run LibreTranslate using docker.
        echo:
        GOTO :done
    )
    IF "%1"=="--api-keys" (
        SET DB_VOLUME=-v lt-db:/app/db
        SHIFT
    )
    SHIFT
    GOTO :loop
)

WHERE /Q docker
IF %ERRORLEVEL% NEQ 0 GOTO :install_docker

docker run -ti --rm -p %LT_PORT%:%LT_PORT% %DB_VOLUME% -v lt-local:/home/libretranslate/.local libretranslate/libretranslate %*

GOTO :done

:install_docker
ECHO Cannot find docker! Go to https://docs.docker.com/desktop/install/windows-install/ and install docker before running this script (pressing Enter will open the page)
pause
start "" https://docs.docker.com/desktop/install/windows-install/
GOTO :done

:done
