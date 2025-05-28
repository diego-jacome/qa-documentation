# On Demand Integrated Search Endpoint

##  

> [!WARNING]  
> Test connected to CatoVPN

### Request sample to import into Postman

curl --location 'https://azwebapp-dd-integrated-search-test.azurewebsites.net/api/search' \
--header 'systemId: 25' \
--header 'Content-Type: application/json' \
--data '{
  "document": {
    "contentQuery": "oil"
  }
}'


<details>
<summary>View FULL Request Body</summary>
  
```json
{
  "document": {
    "content_id": "string",
    "fileRef": "string",
    "contentQuery": "string",
    "contentVersion": "string",
    "creationDateFrom": "2025-05-28T14:25:03.189Z",
    "creationDateTo": "2025-05-28T14:25:03.189Z",
    "lastModificationDateFrom": "2025-05-28T14:25:03.189Z",
    "lastModificationDateTo": "2025-05-28T14:25:03.189Z",
    "minFileSize": 0,
    "maxFileSize": 0,
    "extension": "string",
    "templates": [
      "string"
    ],
    "hashtags": [
      "string"
    ],
    "comments": [
      {
        "userId": "string",
        "comment": "string"
      }
    ],
    "primaryLocationId": "string",
    "secondaryLocationId": "string",
    "tertiaryLocationId": "string",
    "linkedTo": [
      {
        "terciaryId": "string",
        "name": "string"
      }
    ],
    "attributes": [
      {
        "attributeId": "string",
        "name": "string",
        "value": "string"
      }
    ],
    "packetIds": [
      "string"
    ]
  },
  "location": {
    "locationId": "string",
    "locationType": "string",
    "parentId": "string",
    "name": "string",
    "properties": [
      {
        "attributeId": "string",
        "name": "string",
        "value": "string"
      }
    ]
  },
  "packet": {
    "projectId": "string",
    "name": "string",
    "packetEntities": [
      {
        "attributeId": "string",
        "name": "string",
        "value": "string"
      }
    ]
  }
}
```
</details>

</details>

<details>
  
![image](https://github.com/user-attachments/assets/19e217ce-08ef-4f87-8921-f1e89a5d0fee)
![image](https://github.com/user-attachments/assets/d8c4ef37-567a-4384-8fc9-5be0117bdb19)

</details>
