# WatchNet

## Trabajo Práctico Final Integrador: Desarrollo de una API RESTful

Integrantes: Tomas Gomez y Victoria Arrudi

### Idea

WatchNet es una plataforma social en línea centrada en series y películas, donde los usuarios pueden llevar un registro de las series y películas que han visto, escribir reseñas y puntuar títulos. Además, los usuarios pueden seguir a otros para ver lo que están viendo, leer sus reseñas y participar en discusiones. 

Algunas de las estrategias pensadas para generar ingresos con WatchNet: 

- Anuncios Patrocinados: vender espacios publicitarios a productoras, plataformas de streaming y marcas relacionadas con el cine y la televisión. 
- Contenido Patrocinado: las productoras pueden pagar para promocionar sus series o películas directamente en la plataforma a través de reseñas destacadas.
- Planes de suscripción: ofrecer una versión gratuita con funciones básicas y una versión premium con características adicionales, como la eliminación de anuncios, acceso a contenido exclusivo, o funciones avanzadas de seguimiento y análisis.

### Requerimientos

- Los usuarios podrán registrarse.
- Los usuarios podrán seguir a otros usuarios.
- Los usuarios podrán dar una puntuación numérica a cada serie y película que vieron.
- Los usuarios podrán hacer reseñas de las series y películas que vieron.
- Los usuarios podrán crear una lista de seguimiento de series y películas que han visto, están viendo, o desean ver. 
- Los usuarios podrán hacer un seguimiento de los capítulos que han visto de cada serie. 
- Los usuarios podrán crear listas de reproducción personalizadas con cualquier conjunto de series y películas. 
- Los usuarios podrán interactuar con reseñas de otros usuarios.
- Las productoras podrán crear sus propias cuentas, distintas a las cuentas de usuario, para crear un catálogo con su contenido.
- Los usuarios podrán seguir a las productoras para ser notificados de contenido nuevo que publiquen.
- Los usuarios podrán ver todo el contenido de una productora en su perfil. 
- Los usuarios podrán ver la actividad de otros usuarios en su perfil.
- Los usuarios podrán ver las listas de seguimiento y reproducción de otros usuarios en su perfil.
- Los usuarios podrán ver las reseñas y puntuaciones de otros usuarios en su perfil.

### Diagrama de Clases
[Haz click aquí para ver el diagrama de clases.](https://drive.google.com/file/d/1iH6wuY-s6IVWiUWIAT1q8GHiB0jkwWfv/view?usp=sharing)

# Instalación

## Python
Descargar Python 3.8 o superior. 
### Windows
Se puede descargar Python desde [aquí](https://www.python.org/downloads/).
### Linux
Utiliza el comando correspondiente a tu distribución para instalar programas. Por ejemplo, para distribuciones basadas en Debian, usa:
```bash
sudo apt install python3
```

## Poetry
Descargar e instalar Poetry con el siguiente comando:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
Una vez instalado, se puede verificar la instalación con:
```bash
poetry --version
```
En caso de no funcionar, quizá necesite añadir Poetry al PATH. Lo puede hacer con:
```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Clonar repositorio
Clona el repositorio desde tu terminal con:
```bash
git clone https://github.com/TomasGomez02/WatchNet.git
```

## Instalar dependencias
Con la terminan en la carpeta raiz del proyecto, usa
```bash
poetry install
```
para instalar todas las dependencias del proyecto.

## Correr app
Utilizar el comando
```bash
py run.py
```
desde el directorio raiz de la app para comenzar a correrla. 