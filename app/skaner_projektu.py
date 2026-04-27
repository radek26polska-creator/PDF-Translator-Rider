import os
import sys
from pathlib import Path
from datetime import datetime

def scan_project(start_path, output_file="raport_projektu.txt"):
    """Skanuje strukturę projektu i zapisuje do pliku tekstowego"""
    
    start_path = Path(start_path)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"RAPORT PROJEKTU PDF RIDER NEX\n")
        f.write(f"Data skanowania: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        
        # 1. Gdzie jesteśmy
        f.write("1. LOKALIZACJA PROJEKTU\n")
        f.write("-" * 40 + "\n")
        f.write(f"Bieżący katalog: {os.getcwd()}\n")
        f.write(f"Skrypt uruchomiony z: {sys.executable}\n")
        f.write(f"Python wersja: {sys.version}\n\n")
        
        # 2. Struktura katalogów i pliki
        f.write("2. STRUKTURA KATALOGÓW\n")
        f.write("-" * 40 + "\n")
        
        # Idziemy o jeden katalog wyżej (bo skrypt jest w folderze PDF Rider Nex)
        search_path = start_path.parent if start_path.name == "PDF Rider Nex" else start_path
        
        for root, dirs, files in os.walk(search_path):
            level = root.replace(str(search_path), '').count(os.sep)
            indent = '│   ' * level
            folder_name = os.path.basename(root)
            if level == 0:
                f.write(f"{folder_name}/\n")
            else:
                f.write(f"{indent}├── {folder_name}/\n")
            
            subindent = '│   ' * (level + 1)
            for file in sorted(files):
                if file.endswith(('.py', '.txt', '.md', '.json', '.pyc', '.exe')):
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    f.write(f"{subindent}├── {file} ({file_size} bajtów)\n")
        
        # 3. Pliki Python - zawartość
        f.write("\n\n3. ZAWARTOŚĆ PLIKÓW PYTHON\n")
        f.write("-" * 40 + "\n")
        
        python_files = []
        for root, dirs, files in os.walk(search_path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        for py_file in sorted(python_files):
            rel_path = os.path.relpath(py_file, search_path)
            f.write(f"\n\n=== PLIK: {rel_path} ===\n")
            f.write("=" * 60 + "\n")
            try:
                with open(py_file, 'r', encoding='utf-8') as pf:
                    content = pf.read()
                    f.write(content)
                    f.write("\n")
            except Exception as e:
                f.write(f"Błąd odczytu pliku: {e}\n")
        
        # 4. Zainstalowane paczki Python
        f.write("\n\n4. ZAINSTALOWANE PAKIETY PYTHON\n")
        f.write("-" * 40 + "\n")
        try:
            import subprocess
            result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                                  capture_output=True, text=True, timeout=30)
            f.write(result.stdout)
        except Exception as e:
            f.write(f"Nie udało się pobrać listy pakietów: {e}\n")
        
        f.write("\n" + "=" * 80 + "\n")
        f.write("KONIEC RAPORTU\n")
        f.write("=" * 80 + "\n")
    
    print(f"✅ Raport został zapisany do pliku: {output_file}")
    print(f"📁 Pełna ścieżka: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    # Skanujemy bieżący katalog
    scan_project(os.getcwd())