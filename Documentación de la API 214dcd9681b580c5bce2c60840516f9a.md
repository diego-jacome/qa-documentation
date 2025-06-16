# Documentación de la API

<aside>
❗ **Consejo de Notion:** usa esta página como ejemplo de cómo puedes estructurar tu documentación de la API y alojarla en Notion.
La base de datos Endpoints también incluye una plantilla de endpoint para documentación adicional.

</aside>

> [!IMPORTANT]  
> Crucial information necessary for users to succeed.

# Genérico

## Introducción

La documentación es la clave para comprender a fondo la API de Notion.

<aside>
❗ Necesitas un token de integración para interactuar con la API de Notion. Encontrarás un token de integración después de crear una integración en la página de configuración de la integración. Si es la primera vez que usas la API de Notion, te recomendamos que empieces por la [guía de introducción](https://developers.notion.com/docs/getting-started) (inglés) para aprender a crear una integración.

</aside>

### Convenciones

La URL base para enviar todas las solicitudes de API es `https://api.notion.com`. Se requiere HTTPS para todas las solicitudes de API.

La API de Notion sigue las convenciones RESTful en la medida de lo posible, y la mayoría de las operaciones se realizan mediante solicitudes `GET`, `POST`, `PATCH` y `DELETE` en recursos de páginas y bases de datos. Los cuerpos de solicitud y respuesta se codifican como JSON.

**CONVENCIONES JSON**

- Los recursos de nivel superior tienen una propiedad `"object"`. Esta propiedad puede usarse para determinar el tipo de recurso (por ejemplo, `"database"`, `"user"`, etc.).
- Los recursos de nivel superior son direccionables mediante una propiedad `"id"` UUIDv4. Puedes omitir los guiones del ID al realizar solicitudes a la API, por ejemplo, al copiar el ID de una URL de Notion.
- Los nombres de las propiedades están en `snake_case` (no en `camelCase` o `kebab-case`).
- Los valores temporales (fechas y horas) se codifican en cadenas [ISO 8601](https://es.wikipedia.org/wiki/ISO_8601). Las fechas incluirán el valor de la hora (`2020-08-12T02:12:33.231Z`), mientras que las fechas sólo incluirán la fecha (`2020-08-12`).
- La API de Notion no admite cadenas vacías. Para anular un valor de cadena para propiedades como un `url`[Property value object](https://developers.notion.com/reference/property-value-object), por ejemplo, usa un `null` explícito en lugar de `""`.

### Ejemplos de código y SDK

Se muestran ejemplos de solicitudes y respuestas para cada punto final. Las solicitudes se muestran usando Notion [JavaScript SDK](https://github.com/makenotion/notion-sdk-js) y [cURL](https://curl.se/). Estos ejemplos hacen que sea fácil de copiar, pegar y modificar a medida que construyes la integración.

Los SDKs de Notion son proyectos de código abierto que puedes instalar para empezar a construir fácilmente. También puedes elegir cualquier otro lenguaje o librería que te permita realizar peticiones HTTP.

### Paginación

Los endpoints que devuelven listas de objetos admiten solicitudes de paginación basadas en el cursor. Por defecto, Notion devuelve diez elementos por llamada a la API. Si el número de elementos en una respuesta de un endpoint de soporte supera el valor predeterminado, entonces una integración puede usar la paginación para solicitar un conjunto específico de los resultados y/o limitar el número de elementos devueltos.

**ENDPOINTS SOPORTADOS**

| **Método HTTP** | **Endpoint** |
| --- | --- |
| GET | [Listar todos los usuarios](https://developers.notion.com/reference/get-users) |
| GET | [Recuperar hijos de bloque](https://developers.notion.com/reference/get-block-children) |
| GET | [Recuperar un comentario](https://developers.notion.com/reference/retrieve-a-comment) |
| GET | [Recuperar un elemento de propiedad de página](https://developers.notion.com/reference/retrieve-a-page-property) |
| POST | [Consultar una base de datos](https://developers.notion.com/reference/post-database-query) |
| POST | [Buscar](https://developers.notion.com/reference/post-search) |

**RESPUESTAS**

| **Campo** | **Tipo** | **Descripción** |
| --- | --- | --- |
| `has_more` | `booleano` | Si la respuesta incluye el final de la lista. `false` si no hay más resultados. En caso contrario, `true`. |
| `next_cursor` | `cadena` | Una cadena que puede usarse para recuperar la siguiente página de resultados pasando el valor como [parámetro](https://developers.notion.com/reference/intro#parameters-for-paginated-requests) `start_cursor` al mismo endpoint. Sólo disponible cuando `has_more` es `true`. |
| `object` | `"lista"` | La cadena constante `"lista"`. |
| `results` | `matriz de objetos` | La lista, o lista parcial, de resultados específicos de los endpoints. Para más detalles, consulta la documentación individual de cada [endpoint compatible](https://developers.notion.com/reference/intro#supported-endpoints). |

## Límites de solicitud

Para garantizar una experiencia de desarrollo coherente para todos los usuarios de la API, la API de Notion tiene una tasa limitada y se aplican límites de tamaño básicos a los parámetros de solicitud.

### Límites de la tasa

Las solicitudes de tasa limitada devolverán un código de error `"rate_limited"` (estado de respuesta HTTP 429). **El límite de tasa para las solicitudes entrantes por integración es una media de tres solicitudes por segundo.** Se permiten algunas ráfagas por encima de la tasa media.

<aside>
❗ **Los límites de las tasas pueden cambiar**

En el futuro, tenemos previsto ajustar los límites de las tasas para equilibrar la demanda y la fiabilidad. También es posible que introduzcamos límites de tarifa distintos para espacios de trabajo en planes de precios diferentes.

</aside>

### Límite de tamaño

Notion limita el tamaño de ciertos parámetros, y la profundidad de los hijos en las peticiones. Una petición que exceda cualquiera de estos límites devolverá el código de error `"validation_error"` (estado de respuesta HTTP 400) y contendrá detalles más específicos en la propiedad `"message"`.

| **Tipo de valor de la propiedad** | **Propiedad interior** | **Límite de tamaño** |
| --- | --- | --- |
| [Rich text object](https://developers.notion.com/reference/rich-text) | `text.content` | 2000 caracteres |
| [Rich text object](https://developers.notion.com/reference/rich-text) | `text.link.url` | 2000 caracteres |
| [Rich text object](https://developers.notion.com/reference/rich-text) | `equation.expression` | 1000 caracteres |
| Cualquier matriz de [rich text objects](https://developers.notion.com/reference/rich-text) |  | 100 elementos |

## Códigos de estado

Los códigos de respuesta HTTP se usan para indicar clases generales de éxito y error.

### Código de éxito

| **Cuota de estado HTTP** | **Descripción** |
| --- | --- |
| 200 | Solicitud procesada con éxito. |

### Códigos de error

Las respuestas de error contienen más detalles sobre el error en el cuerpo de la respuesta, en las propiedades `"code"` y `"message"`.

| **Cuota de estado HTTP** | `code` | `message` |
| --- | --- | --- |
| 400 | invalid_json | El cuerpo de la petición no ha podido ser decodificado como JSON. |
|  | invalid_request_url | Esta URL de solicitud no es válida. |
|  | invalid_request | No se admite esta solicitud. |
| 401 | unauthorized | El token de portador no es válido. |

## Versiones

Las versiones de nuestra API se denominan según la fecha de publicación de la versión. Por ejemplo, nuestra última versión es 28-06-2022.

La versión se establece incluyendo una cabecera `Notion-Version`. La cabecera `Notion-Version` es **obligatoria**.

```jsx
curl https://api.notion.com/v1/users/01da9b00-e400-4959-91ce-af55307647e5 \
  -H "Authorization: Bearer secret_t1CdN9S8yicG5eWLUOfhcWaOscVnFXns"
  -H "Notion-Version: 2022-06-28"
```

# Objetos

## Usuarios

### Dónde aparecen los objetos de usuario en la API

Los objetos de usuario aparecen en casi todos los objetos devueltos por la API, incluyendo:

- [Block object](https://developers.notion.com/reference/block) bajo `created_by` y `last_edited_by`.
- [Page object](https://developers.notion.com/reference/page) bajo `created_by` y `last_edited_by` y en los elementos de la propiedad `people`.
- [Database object](https://developers.notion.com/reference/database) bajo `created_by` y `last_edited_by`.
- [Rich text object](https://developers.notion.com/reference/rich-text), como menciona el usuario.
- [Property object](https://developers.notion.com/reference/property-object) cuando la propiedad es de tipo `people`.

Los objetos de usuario siempre contendrán las claves `object` e `id`, como se describe a continuación. El resto de propiedades pueden aparecer si el usuario está siendo renderizado en un contexto de texto enriquecido o de propiedades de página, y el bot tiene las capacidades correctas para acceder a esas propiedades. Para obtener más información sobre las capacidades, consulte la [guía Capacidades](https://developers.notion.com/reference/capabilities) (inglés) y la [guía Autorización](https://developers.notion.com/docs/authorization) (inglés).

### Todos los usuarios

Estos campos son compartidos por todos los usuarios, incluyendo personas y bots. Los campos marcados con * están siempre presentes.

| **Propiedad** | **Actualizable** | **Tipo** | **Descripción** | **Valor de ejemplo** |
| --- | --- | --- | --- | --- |
| `object`* | Sólo en pantalla | `"user"` | Siempre "user" | `"user"` |
| `id`* | Sólo en pantalla | `string`(UUID) | Identificador único para este usuario. | `"e79a0b74-3aba-4149-9f74-0bb5791a6ee6"` |
| `type` | Sólo en pantalla | `string`(opcional, enum) | Tipo de usuario. Los valores posibles son `"person"` y `"bot"`. | `"person"` |
| `name` | Sólo en pantalla | `string`(opcional) | Nombre del usuario, tal y como aparece en Notion. | `"Aguacate cool"` |
| `avatar_url` | Sólo en pantalla | `string`(opcional) | Imagen de avatar elegida. | `"https://secure.notion-static.com/e6a352a8-8381-44d0-a1dc-9ed80e62b53d.jpg"` |

## Archivo

Los objetos de archivo contienen datos sobre un archivo que se carga en Notion, o datos sobre un archivo externo al que se enlaza en Notion.

```jsx
{
  "type": "file",
  "file": {
    "url": "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/7b8b0713-dbd4-4962-b38b-955b6c49a573/My_test_image.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20221024%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20221024T205211Z&X-Amz-Expires=3600&X-Amz-Signature=208aa971577ff05e75e68354e8a9488697288ff3fb3879c2d599433a7625bf90&X-Amz-SignedHeaders=host&x-id=GetObject",
    "expiry_time": "2022-10-24T22:49:22.765Z"
  }
}
```

Los [tipos de bloque](https://developers.notion.com/reference/block) (inglés) página, adjunto, imagen, video, archivo, pdf y marcador contienen objetos de archivo. Los [valores objeto de la página](https://developers.notion.com/reference/page#all-pages) (inglés) de ícono y portada también contienen objetos de archivo.

Cada objeto de fichero incluye los siguientes campos:

| **Campo** | **Tipo** | **Descripción** | **Valor de ejemplo** |
| --- | --- | --- | --- |
| `type` | `string` (enum) | El tipo del objeto de archivo. Los posibles valores de tipo son: `"external"`, `"file"`. | `"external"` |
| `external`| `file` | `object` | Un objeto que contiene la configuración específica del tipo. La clave del objeto es `external` para los archivos externos, y `file` para los archivos alojados en Notion. Consulta las secciones de tipo a continuación para obtener más información sobre los valores específicos de cada tipo. | Consulta los ejemplos en las secciones específicas de cada tipo. |

# Endpoints

[Endpoints](Endpoints%20214dcd9681b581cba8aacea6916f6d46.csv)
