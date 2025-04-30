
# Consulta de Tarifas de Transporte

Esta aplicación permite consultar tarifas de transporte interurbano entre distintas localidades, mostrando las empresas que ofrecen el servicio y el tipo de servicio.

## 📦 Contenido del repositorio

- `app.py`: Código fuente de la app en Streamlit.
- `tarifas_demo.csv`: Base de datos de ejemplo con origen, destino, empresa, tarifa y tipo de servicio.
- `README.md`: Este archivo con instrucciones de uso.

## 🚀 Cómo ejecutar la app

1. Clonar este repositorio o descargar los archivos.
2. Instalar Streamlit si aún no lo tenés:

```
pip install streamlit
```

3. Ejecutar la app desde la terminal o consola:

```
streamlit run app.py
```

## 📝 Cómo usar

1. Seleccionar un **origen** y un **destino** desde las listas desplegables.
2. Presionar el botón **Buscar tarifa**.
3. Verás los resultados con la tarifa correspondiente, empresa y tipo de servicio.

## 🔧 Personalización

Podés reemplazar el archivo `tarifas_demo.csv` por tu propia base de datos con la misma estructura de columnas:

- `Origen`
- `Destino`
- `Empresa`
- `Tarifa`
- `Tipo de Servicio`

---

© 2025 – Proyecto de demostración
