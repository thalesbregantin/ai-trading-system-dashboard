import pandas as pd
import numpy as np
from pathlib import Path

print("🧪 Simple Data Test")
print("=" * 40)

# Diretório dos dados
data_dir = Path(__file__).parent / "data"
print(f"📂 Data directory: {data_dir}")
print(f"📂 Exists: {data_dir.exists()}")

if data_dir.exists():
    csv_files = list(data_dir.glob("*.csv"))
    print(f"📄 CSV files found: {len(csv_files)}")
    
    # Testa carregamento dos arquivos principais
    main_files = {
        'equity': 'equity_momentum_optimized.csv',
        'trades': 'trades_momentum_optimized.csv'
    }
    
    for name, filename in main_files.items():
        filepath = data_dir / filename
        print(f"\n📊 Testing {name} ({filename}):")
        
        if filepath.exists():
            try:
                df = pd.read_csv(filepath)
                print(f"   ✅ Loaded: {len(df)} rows, {len(df.columns)} columns")
                print(f"   📋 Columns: {list(df.columns)}")
                
                # Verifica se tem data
                date_cols = [col for col in df.columns if 'date' in col.lower()]
                if date_cols:
                    print(f"   📅 Date columns: {date_cols}")
                    df[date_cols[0]] = pd.to_datetime(df[date_cols[0]])
                    print(f"   📅 Date range: {df[date_cols[0]].min()} to {df[date_cols[0]].max()}")
                
                # Mostra amostra dos dados
                print(f"   📝 Sample row: {dict(df.iloc[0]) if len(df) > 0 else 'No data'}")
                
            except Exception as e:
                print(f"   ❌ Error loading: {e}")
        else:
            print(f"   ❌ File not found: {filepath}")

print("\n" + "=" * 40)
print("✅ Data test completed!")
