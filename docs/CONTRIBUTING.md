# Guía de Contribución

¡Gracias por tu interés en contribuir a este proyecto!

## Cómo contribuir

1. **Haz un fork** del repositorio y **crea una rama** para tu funcionalidad o corrección:
   ```bash
   git checkout -b feature/mi-nueva-funcionalidad
   ```
2. **Realiza tus cambios** siguiendo las buenas prácticas y la estructura del proyecto.
3. **Asegúrate de que el código pase las pruebas** y no rompa la funcionalidad existente.
4. **Haz commit** de tus cambios:
   ```bash
   git commit -am "Agrega nueva funcionalidad X"
   ```
5. **Haz push** a tu rama:
   ```bash
   git push origin feature/mi-nueva-funcionalidad
   ```
6. **Abre un Pull Request** describiendo claramente tus cambios y relacionando issues si corresponde.
7. Espera la revisión de los administradores y responde a los comentarios o sugerencias.

## Recomendaciones

- Sigue la estructura y convenciones del proyecto.
- Documenta y comenta el código donde sea necesario.
- Si agregas nuevas dependencias, actualiza `requirements.txt` y los scripts SQL correspondientes. Si modificas la base de datos, documenta los cambios en `DATA_MODEL.md`.
- Si agregas nuevos módulos (notificaciones, inversiones, auditoría), actualiza la documentación técnica y los archivos de referencia.
- Incluye ejemplos o documentación si tu cambio lo requiere.
- Añade o actualiza pruebas automáticas si es posible.
- Verifica que tu código pase los linters y pruebas antes de enviar el Pull Request.

## Código de conducta

Este proyecto promueve un ambiente colaborativo y respetuoso. Por favor, sé cordial y profesional en todas las interacciones.
Consulta el archivo `CODE_OF_CONDUCT.md` para más detalles.

---

¡Esperamos tus contribuciones!