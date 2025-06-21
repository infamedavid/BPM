# 🎬 Blender Project Management Addon (BPM)
Blender 4.0+

Una serie de herramientas para el manejo de projectos audiovisuales dirigido a artistas, técnicos y creativos que trabajan con múltiples archivos `.blend`, texturas externas, assets linkeados y mas. Organiza, limpia, automatiza y rescata archivos corruptos.

---
### 📁 Gestión de Proyecto
- Crea una estructura de carpetas organizada desde Blender (Available on "File" Menu)
- Define la **carpeta raíz** del proyecto (`Project Root Folder`).
- Guarda archivos temporales dentro del árbol del proyecto.

### 🖼️ Administración de Texturas
- Mueve todas las texturas utilizadas a la carpeta activa (`//textures`) con un clic.
- Actualiza automáticamente los paths en el archivo `.blend`.
- Opción para guardar automáticamente tras mover texturas (`Save File`).

### 🔗 Gestión de Librerías Linkeadas
- Lista completa de librerías `.blend` linkeadas en la escena.
- Iconos de estado:
  - ✅ OK (dentro del proyecto)
  - ❓ Fuera del proyecto
  - ❌ Ruta rota (archivo no encontrado)
- Genera reportes por asset.

### ➕ Linkeado de nuevos `.blend`
- Selector interactivo de archivos `.blend` con filtro por tipo de datos (`OBJECT`, `COLLECTION`, etc.).
- Botón `Link a .blend File` para importar contenido limpio y organizado.
- Botón directo para **hacer override** a objetos linkeados.

---

## 🧯 Safe Mode – Recuperación de Archivos Corruptos

Archivos `.blend` que hacen crashear Blender al abrirse.

### 🔄 `Load .blend in Safe Mode`
- Lanza directamente el explorador de archivos para cargar un `.blend`.

### ✅ `Disable Safe Mode`

---

## 📍 Ubicación en Blender

- Menú superior: `File > Project Management`
- Panel lateral (`N`): pestaña **BPM** en el `3D Viewport`

---

## 🛠 Instalación

1. Abre **Edit > Preferences > Add-ons**
2. Haz clic en **Install...**
3. Selecciona el archivo `BPM_2_2_3.py`
4. Activa el addon en la lista

---

