@echo off
title Удаление DFDS
echo ================================================
echo          УДАЛЕНИЕ ПРОГРАММЫ DFDS
echo ================================================
echo.
echo Программа будет удалена из системы.
echo Будут удалены:
echo   - C:\Windows\System32\dfds.exe
echo   - Папка с паролями: %APPDATA%\dfds
echo.
set /p confirm="Вы уверены? (введите YES для продолжения): "
if /i not "%confirm%"=="YES" (
    echo Операция отменена.
    pause
    exit /b
)

echo.
echo Удаление исполняемого файла...
if exist "C:\Windows\System32\dfds.exe" (
    del /f /q "C:\Windows\System32\dfds.exe" >nul 2>&1
    if errorlevel 1 (
        echo Ошибка: не удалось удалить dfds.exe. Возможно, требуются права администратора.
    ) else (
        echo Файл dfds.exe удалён.
    )
) else (
    echo Файл dfds.exe не найден.
)

echo.
echo Удаление папки с данными...
if exist "%APPDATA%\dfds" (
    rmdir /s /q "%APPDATA%\dfds" >nul 2>&1
    echo Папка %APPDATA%\dfds удалена.
) else (
    echo Папка %APPDATA%\dfds не найдена.
)

echo.
echo Удаление завершено.
pause