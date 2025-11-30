# Justificación de la estructura del clúster de contenedores

La arquitectura del clúster se ha diseñado con los siguientes objetivos: disponibilidad, replicación simple para pruebas, y demostración de persistencia compartida mediante un volumen.

- Réplicas (tres contenedores): se usan tres instancias idénticas de la aplicación para demostrar escalado horizontal y tolerancia a fallos a nivel de servicio. Tener múltiples réplicas facilita pruebas locales y permite mostrar cómo varias instancias pueden atender solicitudes de forma independiente.

- Contenedor de datos (data-only): un contenedor cuyo único propósito es poseer y exponer un volumen nombrado compartido por las réplicas. Esto ilustra el patrón donde un volumen persistente está separado de las imágenes de aplicación y sirve para compartir ficheros o datos no transaccionales entre instancias.

- Consistencia de imagen: todas las réplicas se construyen desde el mismo `Dockerfile` para garantizar que la imagen que se despliega es idéntica en cada contenedor; así se evita desviaciones entre instancias y se facilita la trazabilidad de versiones.

Consideraciones y limitaciones:

- Compartir un volumen entre réplicas es adecuado para demostraciones y datos no críticos (logs, artefactos). No es una solución adecuada para datos transaccionales; en producción se recomienda usar una base de datos gestionada o almacenamiento distribuido y un balanceador para enrutar tráfico.
- No se ha incluido un balanceador en esta topología por simplicidad y por necesidades de la práctica; las réplicas exponen puertos distintos para facilitar pruebas individuales.

En resumen: la combinación de tres réplicas idénticas y un contenedor de datos permite demostrar escalado horizontal básico, persistencia compartida y consistencia de despliegue sin introducir complejidad de orquestadores completos, lo cual es suficiente para los objetivos pedagógicos de la práctica.
