#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
NAZWA: AI Project Exporter
OPIS: Skanuje cały projekt i generuje JEDEN plik tekstowy zawierający WSZYSTKIE
       informacje potrzebne AI do pełnego zrozumienia projektu.
DZIAŁANIE: 
   1. Skanuje wszystkie pliki w projekcie (lub wybrane rozszerzenia)
   2. Zapisuje ich zawartość + ścieżki + strukturę folderów
   3. Dodaje metadane (język, framework, zależności)
   4. Generuje JEDEN plik .txt możliwy do wklejenia do AI

UŻYCIE: python ai_project_exporter.py /ścieżka/do/projektu
================================================================================
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# ============================================================
# KONFIGURACJA - MOŻESZ DOSTOSOWAĆ DO SWOICH POTRZEB
# ============================================================

# Rozszerzenia plików, które chcemy uwzględnić (puste = wszystkie)
DOŁĄCZONE_ROZSZERZENIA = [
    '.py', '.js', '.ts', '.jsx', '.tsx',      # Języki programowania
    '.html', '.css', '.scss', '.sass',        # Web
    '.json', '.yaml', '.yml', '.toml', '.xml', # Konfiguracje
    '.md', '.txt', '.rst',                     # Dokumentacja
    '.cpp', '.c', '.h', '.hpp',                # C/C++
    '.java', '.kt', '.kts',                    # Java/Kotlin
    '.go', '.rs', '.rb', '.php',               # Inne języki
    '.sql',                                    # Bazy danych
    '.sh', '.bat', '.ps1',                     # Skrypty powłoki
    '.dockerfile', '.yaml',                    # Docker/K8s
]

# Rozszerzenia do IGNOROWANIA (binarki, obrazy, itp.)
IGNOROWANE_ROZSZERZENIA = [
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico',  # Obrazy
    '.exe', '.dll', '.so', '.dylib',                  # Binarki
    '.zip', '.tar', '.gz', '.rar', '.7z',             # Archiwa
    '.mp3', '.mp4', '.avi', '.mov',                   # Multimedia
    '.pyc', '.pyo', '.class', '.o',                   # Skompilowane
    '.pdf', '.doc', '.docx', '.xls', '.xlsx',         # Dokumenty (opcjonalnie)
]

# Foldery do IGNOROWANIA
IGNOROWANE_FOLDERY = [
    'node_modules', '__pycache__', '.git', '.venv', 'venv', 'env',
    'dist', 'build', 'target', 'out', '.idea', '.vscode', 
    '.cache', '.pytest_cache', 'coverage', '.mypy_cache',
    'logs', 'tmp', 'temp', 'uploads', 'downloads'
]

# Maksymalny rozmiar pliku do odczytania (w bajtach, domyślnie 500KB)
MAKSYMALNY_ROZMIAR_PLIKU = 500 * 1024

# Czy pokazywać pełną zawartość dużych plików (False = tylko podgląd)
POKAŻ_PEŁNE_DUŻE_PLIKI = False

# ============================================================
# GŁÓWNA LOGIKA SKANOWANIA
# ============================================================

def czy_plik_do_uwzględnienia(nazwa_pliku):
    """Sprawdza czy plik powinien być uwzględniony w raporcie"""
    rozszerzenie = os.path.splitext(nazwa_pliku)[1].lower()
    
    # Sprawdź czy w ignorowanych
    if rozszerzenie in IGNOROWANE_ROZSZERZENIA:
        return False
    
    # Jeśli lista dołączonych jest pusta -> dołącz wszystko
    if not DOŁĄCZONE_ROZSZERZENIA:
        return True
    
    # Sprawdź czy w dołączonych
    return rozszerzenie in DOŁĄCZONE_ROZSZERZENIA

def skanuj_projekt(ścieżka_projektu):
    """Skanuje cały projekt i zwraca listę plików z zawartością"""
    
    ścieżka_projektu = os.path.abspath(ścieżka_projektu)
    wyniki = {
        'ścieżka_projektu': ścieżka_projektu,
        'nazwa_projektu': os.path.basename(ścieżka_projektu),
        'data_skanowania': datetime.now().isoformat(),
        'struktura': [],
        'pliki': [],
        'statystyki': {
            'liczba_plików': 0,
            'liczba_folderów': 0,
            'całkowity_rozmiar': 0
        }
    }
    
    liczba_folderów = 0
    
    for root, dirs, files in os.walk(ścieżka_projektu):
        # Filtruj foldery ignorowane
        dirs[:] = [d for d in dirs if d not in IGNOROWANE_FOLDERY]
        
        rel_path = os.path.relpath(root, ścieżka_projektu)
        if rel_path == '.':
            rel_path = ''
        
        # Zapisz strukturę folderów
        if rel_path:
            wyniki['struktura'].append(f"📁 {rel_path}/")
            liczba_folderów += 1
        
        for file in files:
            if not czy_plik_do_uwzględnienia(file):
                continue
            
            ścieżka_pliku = os.path.join(root, file)
            rozmiar = os.path.getsize(ścieżka_pliku)
            
            # Pomijaj bardzo duże pliki jeśli nie chcemy ich całych
            if rozmiar > MAKSYMALNY_ROZMIAR_PLIKU and not POKAŻ_PEŁNE_DUŻE_PLIKI:
                zawartość = f"[PLIK ZA DUŻY - {rozmiar//1024}KB - POMINIĘTO. Zmień MAKSYMALNY_ROZMIAR_PLIKU aby włączyć]"
            else:
                try:
                    with open(ścieżka_pliku, 'r', encoding='utf-8') as f:
                        zawartość = f.read()
                except (UnicodeDecodeError, PermissionError, OSError):
                    zawartość = f"[NIE MOŻNA ODCZYTAĆ - plik binarny lub brak uprawnień]"
            
            rel_ścieżka = os.path.relpath(ścieżka_pliku, ścieżka_projektu)
            
            wyniki['pliki'].append({
                'ścieżka': rel_ścieżka,
                'rozmiar': rozmiar,
                'rozszerzenie': os.path.splitext(file)[1].lower(),
                'zawartość': zawartość
            })
            
            wyniki['statystyki']['liczba_plików'] += 1
            wyniki['statystyki']['całkowity_rozmiar'] += rozmiar
    
    wyniki['statystyki']['liczba_folderów'] = liczba_folderów
    return wyniki

def wykryj_typ_projektu(pliki):
    """Próbuje automatycznie wykryć typ/framework projektu"""
    
    wszystkie_ścieżki = ' '.join([p['ścieżka'].lower() for p in pliki])
    
    if 'package.json' in wszystkie_ścieżki:
        if 'next.config' in wszystkie_ścieżki:
            return 'Next.js'
        elif 'vite.config' in wszystkie_ścieżki:
            return 'Vite + React/Vue'
        else:
            return 'Node.js / npm'
    
    if 'requirements.txt' in wszystkie_ścieżki or 'setup.py' in wszystkie_ścieżki:
        return 'Python'
    
    if 'go.mod' in wszystkie_ścieżki:
        return 'Go'
    
    if 'Cargo.toml' in wszystkie_ścieżki:
        return 'Rust'
    
    if 'pom.xml' in wszystkie_ścieżki:
        return 'Java (Maven)'
    
    if 'build.gradle' in wszystkie_ścieżki:
        return 'Java/Kotlin (Gradle)'
    
    if 'Dockerfile' in wszystkie_ścieżki:
        return 'Dockerized'
    
    return 'Nieznany / Ogólny'

def generuj_raport_dla_ai(dane_projektu):
    """Generuje JEDEN plik tekstowy z pełną informacją dla AI"""
    
    raport = []
    raport.append("=" * 80)
    raport.append("PROJEKT - PEŁNY EKSPORT DLA SZTUCZNEJ INTELIGENCJI")
    raport.append("=" * 80)
    raport.append("")
    raport.append("【INFORMACJE PODSTAWOWE】")
    raport.append(f"Nazwa projektu: {dane_projektu['nazwa_projektu']}")
    raport.append(f"Ścieżka: {dane_projektu['ścieżka_projektu']}")
    raport.append(f"Data skanowania: {dane_projektu['data_skanowania']}")
    raport.append(f"Typ projektu: {wykryj_typ_projektu(dane_projektu['pliki'])}")
    raport.append("")
    
    raport.append("【STATYSTYKI PROJEKTU】")
    raport.append(f"Liczba plików: {dane_projektu['statystyki']['liczba_plików']}")
    raport.append(f"Liczba folderów: {dane_projektu['statystyki']['liczba_folderów']}")
    raport.append(f"Całkowity rozmiar: {dane_projektu['statystyki']['całkowity_rozmiar']//1024} KB")
    raport.append("")
    
    raport.append("【STRUKTURA FOLDERÓW】")
    for folder in dane_projektu['struktura'][:50]:  # max 50 linii
        raport.append(f"  {folder}")
    if len(dane_projektu['struktura']) > 50:
        raport.append(f"  ... i {len(dane_projektu['struktura'])-50} więcej folderów")
    raport.append("")
    
    raport.append("=" * 80)
    raport.append("ZAWARTOŚĆ WSZYSTKICH PLIKÓW")
    raport.append("=" * 80)
    raport.append("")
    
    for plik in dane_projektu['pliki']:
        raport.append("-" * 60)
        raport.append(f"📄 PLIK: {plik['ścieżka']}")
        raport.append(f"Rozmiar: {plik['rozmiar']} bajtów ({plik['rozmiar']//1024} KB)")
        raport.append(f"Rozszerzenie: {plik['rozszerzenie']}")
        raport.append("-" * 60)
        raport.append("")
        raport.append(plik['zawartość'])
        raport.append("")
        raport.append("")
    
    raport.append("=" * 80)
    raport.append("KONIEC EKSPORTU PROJEKTU")
    raport.append(f"Łączna liczba plików: {dane_projektu['statystyki']['liczba_plików']}")
    raport.append("=" * 80)
    
    return '\n'.join(raport)

def main():
    """Główna funkcja"""
    
    if len(sys.argv) < 2:
        print("UŻYCIE: python ai_project_exporter.py /ścieżka/do/projektu")
        print("")
        print("PRZYKŁADY:")
        print("  python ai_project_exporter.py .                    # bieżący folder")
        print("  python ai_project_exporter.py /home/user/mójprojekt")
        print("")
        print("Wynik: Plik 'projekt_NAZWA_DATA.txt' z pełnym eksportem")
        sys.exit(1)
    
    ścieżka = sys.argv[1]
    
    if not os.path.isdir(ścieżka):
        print(f"BŁĄD: '{ścieżka}' nie jest folderem lub nie istnieje")
        sys.exit(1)
    
    print(f"📂 Skanowanie projektu: {ścieżka}")
    print("⏳ To może potrwać chwilę (szczególnie przy dużej liczbie plików)...")
    
    # Skanuj projekt
    dane = skanuj_projekt(ścieżka)
    
    print(f"✅ Znaleziono {dane['statystyki']['liczba_plików']} plików")
    
    # Generuj raport
    raport = generuj_raport_dla_ai(dane)
    
    # Zapisz do pliku
    nazwa_pliku = f"projekt_{dane['nazwa_projektu']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(nazwa_pliku, 'w', encoding='utf-8') as f:
        f.write(raport)
    
    rozmiar_mb = len(raport) / (1024 * 1024)
    print(f"\n✅ RAPORT GOTOWY!")
    print(f"📄 Plik: {nazwa_pliku}")
    print(f"📏 Rozmiar: {rozmiar_mb:.2f} MB")
    print(f"\n💡 Teraz możesz:")
    print(f"   1. Otworzyć plik {nazwa_pliku}")
    print(f"   2. Skopiować CAŁĄ zawartość")
    print(f"   3. Wkleić do dowolnej AI (ChatGPT, Claude, itp.)")
    print(f"   4. AI będzie wiedzieć o projekcie WSZYSTKO")

if __name__ == "__main__":
    main()