# Analizador Léxico - AigisC

## Alumnos
| Nombre | Código |
| :--- | :--- |
| Cristian Alejandro Flores Rosales | 222966375 |
| Roberto Daniel Iñiguez Martinez de Castro | 222362437 |
| Emmanuel Leonardo Bautista Rico | 218625253 |
| Juan Alejandro Sánchez Vázquez | 223991861 |
 
## Descripción del proyecto
Este proyecto implementa un **Analizador Léxico** para un lenguaje de programación con una **Interfaz Gráfica de Usuario (UI)**, desarrollado en Python. Su función principal es tomar un código fuente, descomponerlo en componentes léxicos (tokens) y reportar cualquier error encontrado.

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)

***
## Estructura del Proyecto

El proyecto se divide en tres archivos principales:

| Archivo | Responsabilidad | Descripción |
| :--- | :--- | :--- |
| **`Lexico.py`** | **Lógica del Analizador** | Define las clases `Token` y `Lexico`, incluyendo las expresiones regulares para el reconocimiento de tokens y el método `tokenize()`. |
| **`LexicoUI.py`** | **Interfaz de Usuario** | Define la clase `LexicalAnalyzerGUI`, construye la ventana (`tkinter`) y maneja la interacción (editor, botón, visualización de resultados). |
| **`main.py`** | **Inicialización** | Inicializa la aplicación y arranca el bucle principal de la UI. |

***

## Tecnologías y Requisitos

Este proyecto utiliza **únicamente librerías estándar** de Python 3.x.

| Librería | Propósito | Usado en |
| :--- | :--- | :--- |
| **`tkinter`** | Construcción de la Interfaz Gráfica de Usuario (UI). | `LexicoUI.py`, `main.py` |
| **`re`** | Módulo de **Expresiones Regulares** (`import re`) para el reconocimiento de patrones léxicos. | `Lexico.py` |
| **`typing`** | Para la definición de tipos de datos (e.g., `List` en `from typing import List`). | `Lexico.py` |

### Requisitos

Solo es necesario tener instalado **Python 3.x** en el dispostivo y las **anteriores librerias**.

***

## Instalación y Ejecución

Sigue estos pasos para poner en marcha el analizador:
### 1. Descargar o clonar el Repositorio
Debemos estar en la página de **GitHub** del repositorio:

    https://github.com/xCrisFlores/AigisC/tree/main

Al estar en el repositorio, se puede descargar en .zip con la carpeta y archivos correspondientes. También se puede clona el proyecto desde GitHub:

    git clone https://github.com/xCrisFlores/AigisC.git

### 2. Ejecutar el programa
Ubicar el **archivo main.py** en la **carpeta**. Se puede ejecutar el programa desde la consola o en un IDLE (ya viene incluido el IDLe de Python al descargarlo), ejecutar el main.py y debería mostrar la interfaz de la aplicación. 

Comando para ejecutar desde consola:
    
    python main.py


## Mini Manual de la Interfaz de Usuario (UI)

La interfaz de la aplicación se divide en cuatro partes principales para facilitar su uso:

1.  **Editor de Código (Panel Izquierdo)**:
    - Es el área de texto grande a la izquierda. Aquí puedes escribir directamente tu código o pegar código desde otro editor.

2.  **Tabla de Símbolos (Panel Derecho)**:
    - A la derecha del editor, esta tabla muestra el resultado del análisis. Por cada token válido que encuentra, lista su número de línea, el token (lexema) y una descripción de su tipo (Ej: `Reservada`, `Identificador`, `Aritmetico`).

3.  **Botón "Compilar"**:
    - Ubicado debajo de los paneles principales. Al hacer clic en este botón, el programa analiza el texto que se encuentra en el **Editor de Código**. Los resultados aparecerán inmediatamente en la **Tabla de Símbolos** y en el **Área de Errores**.

4.  **Errores Léxicos (Panel Inferior)**:
    - En la parte de abajo de la ventana, esta sección de color rojo mostrará cualquier error léxico detectado durante el análisis. Informa qué token no fue reconocido y en qué línea y columna se encontró. Si no hay errores, mostrará el mensaje "No se encontraron errores léxicos."

***

## Gramática Léxica (AigisC)

## 📋 Documentación de la Gramática Léxica (AigisC)

Esta tabla documenta los tipos de tokens, las palabras reservadas o patrones, su función, y un ejemplo de código válido, sino son correctos en el programa, se marcará un error con un token no identificado.

| Tipo de Token | Palabras Reservadas / Patrón | Función | Ejemplo Válido |
| :--- | :--- | :--- | :--- |
| **Reservada** | `if`, `else`, `for`, `while`, `return`, `const`, `int`, `string`, `function`, etc. | Palabras clave con un significado fijo en el lenguaje. | `if (a > 10) { return; }` |
| **Identificador** | `[a-zA-Z_][a-zA-Z0-9_]*` | Nombres definidos por el usuario (variables, funciones, modelos). | `calcular_total`, `x`, `_indice` |
| **Numero** | `[+-]?(\d+\.\d+|\d+\.|\.\d+|\d+)\b` | Valores numéricos enteros o de punto flotante. | `15`, `-3.14`, `+0.5`, `.25` |
| **Cadena** | `"(?:[^"\\]|\\.)*"` | Secuencia de caracteres encerrada en comillas dobles. | `"Hola Mundo"`, `"Error: \\n"` |
| **Relacional** | `==`, `!=`, `<=`, `>=`, `<`, `>` | Operadores para la comparación lógica de valores. | `a == b`, `x <= 5` |
| **Incremental** | `++`, `--`, `//`, `**` | Operadores de incremento, decremento y potencia. | `i++`, `valor--` |
| **Aritmetico** | `+`, `-`, `*`, `/`, `%` | Operadores matemáticos básicos. | `a + b`, `c / 2` |
| **Logico** | `&&`, `\|\|`, `!` | Operadores para combinar expresiones booleanas (AND, OR, NOT). | `a && b`, `!c` |
| **Delimitador** | `{`, `}`, `(`, `)`, `[`, `]`, `,`, `;`, `.` | Símbolos de puntuación para estructurar el código. | `{}`, `(x)`, `[0]`, `func(x,y);` |
| **Comentario** | `//`, `///.*?///` | Líneas o bloques de texto que deben ser ignorados. | `// línea`, `/// bloque ///` |
| **Error** | N/A | Captura cualquier secuencia de caracteres no válida o mal formada. | N/A |

***
