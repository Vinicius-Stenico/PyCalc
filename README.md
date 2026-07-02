# PyCalc

PyCalc e uma calculadora em Python/Tkinter inspirada na Calculadora do Windows, com modos padrao, cientifico, programador, calculo de data, representacao grafica e conversores.

## Executar no codigo-fonte

```powershell
python calculadora.py
```

## Dependencias

```powershell
pip install -r requirements.txt
```

## Testes

```powershell
python -m unittest discover
```

## Gerar executavel

```powershell
.\scripts\build_exe.ps1
```

O executavel fica em:

```text
dist\PyCalc\PyCalc.exe
```

## Gerar instalador

```powershell
.\scripts\build_installer.ps1
```

O instalador fica em:

```text
release\PyCalc_Setup.exe
```

Os arquivos em `build/`, `dist/` e `release/` sao gerados automaticamente e ficam fora do Git por padrao. Para publicar uma versao, suba o codigo-fonte no GitHub e anexe o instalador em uma GitHub Release.
