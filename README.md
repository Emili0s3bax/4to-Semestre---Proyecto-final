# 4to-Semestre---Proyecto-final

# Engineering Visual Hub 📌

An elegant, Pinterest-inspired repository and portal designed specifically for engineering documentation, architectural blueprints, and collaborative visual workflows. This project bridges full-stack web engineering, enterprise identity infrastructure, and scalable cloud services into a single, cohesive ecosystem.

---

## 🚀 Características Principales

* **Interfaz Dinámica Estilo Pinterest:** Visualización en cuadrícula (*masonry grid*) fluida y responsiva para explorar diagramas técnicos, manuales y recursos de ingeniería de forma puramente visual.
* **Autenticación Centralizada con Active Directory:** Integración nativa a nivel empresarial utilizando LDAP/Active Directory de Windows Server, garantizando un control de acceso seguro basado en roles para estudiantes y docentes.
* **Infraestructura en la Nube (AWS Cloud):** Almacenamiento seguro y de alta disponibilidad para archivos multimedia y documentos técnicos mediante servicios integrados de AWS (como Amazon S3) y políticas estrictas de IAM.
* **Arquitectura API Full-Stack robusta:** Backend optimizado de alto rendimiento para la gestión ágil de colecciones, pines y metadatos estructurados, acoplado a un frontend interactivo y limpio.
* **Organización Avanzada:** Permite categorizar proyectos, crear tableros de documentación visual y añadir etiquetas técnicas para agilizar las búsquedas dentro del entorno de desarrollo.

---

## 🛠️ Stack Tecnológico

| Componente | Tecnologías Utilizadas |
| :--- | :--- |
| **Frontend** | HTML5, CSS3 Moderno, JavaScript (ES6+), Masonry Layouts |
| **Backend & APIs** | Python (FastAPI) / Go |
| **Autenticación & Directorio** | Windows Server, Active Directory (AD DS), Protocolo LDAP |
| **Servicios Cloud** | Amazon Web Services (AWS), AWS S3, IAM Policies |
| **Metodología de Trabajo** | Scrum / CRV |

---

## 📐 Arquitectura de la Solución

El ecosistema está estructurado en tres capas fundamentales que garantizan escalabilidad, seguridad y modularidad:

1.  **Capa de Presentación (Frontend):** Consume servicios REST de manera asíncrona, renderizando paneles visuales dinámicos que no comprometen la fluidez de la experiencia del usuario.
2.  **Capa de Lógica y Control (Backend API):** Administra la lógica de negocio, realiza la traducción y validación de credenciales hacia el servidor de identidad y gestiona los tokens de sesión.
3.  **Capa de Infraestructura y Servicios:** Centraliza los directorios de usuarios en un entorno virtualizado local y delega el almacenamiento pesado a buckets optimizados y seguros en AWS.

---

## ⚙️ Configuración e Instalación

### Prerrequisitos
* **Servidor de Identidad:** Instancia configurada de Windows Server con Active Directory habilitado y usuarios mapeados en Unidades Organizativas (OUs).
* **Credenciales Cloud:** Cuenta activa de AWS con un usuario IAM que posea permisos de lectura/escritura sobre el bucket S3 asignado.
* **Entorno Local:** Python 3.10+ o entorno de ejecución Go instalado.

### Pasos para el despliegue

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/tu-usuario/engineering-visual-hub.git
    cd engineering-visual-hub
    ```

2.  **Configurar Variables de Entorno (`.env`):**
    Crea un archivo `.env` en la raíz del backend con los siguientes parámetros esenciales:
    ```env
    # Configuración de Active Directory
    AD_SERVER=ldap://tu-servidor-ad.local
    AD_DOMAIN=tu-dominio.local
    AD_BASE_DN=OU=Usuarios,DC=tu-dominio,DC=local

    # Configuración de AWS Cloud
    AWS_ACCESS_KEY_ID=tu_access_key
    AWS_SECRET_ACCESS_KEY=tu_secret_key
    AWS_REGION=us-east-1
    AWS_S3_BUCKET_NAME=engineering-visual-hub-storage
    ```

3.  **Instalar dependencias e iniciar el servicio:**
    ```bash
    # Ejemplo para entorno Python
    pip install -r requirements.txt
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```

---

## 👥 Colaboradores y Autores

Este proyecto ha sido diseñado, desarrollado e implementado con un enfoque riguroso de ingeniería por:

* **Emilio Sebastian Granda España**
* **Zahid Mathias Rivera Agila**

---

## 📄 Licencia

Este proyecto se distribuye bajo fines estrictamente académicos e institucionales. Todos los derechos de infraestructura y código fuente pertenecen a los autores.