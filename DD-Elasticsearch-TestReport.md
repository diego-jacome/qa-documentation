# 🔍 Elasticsearch Test Report

**QA Analyst**: Diego Jácome  
**Date**: 2025-05-19  
**Environment**: QA  
**Objective**: Index validation, mappings and query results in the Elastic Search cluster used by DD.

---

## 1. 🔧 Initial Configuration

| Parameter | Value |
|----------|-------|
| Base Url | `https://dd-integrated-search-test.kb.southcentralus.azure.elastic-cloud.com/app/dev_tools#/console` |
| Tenant | `25` |
| Evaluated Index | `25_documents` |
| Tool Used | Elasticsearch console |
| Authentication| User and password |

---

## 2. ✅ Executed test cases

### TC01 - Validate the existance of the index

- **Query**:
  ```http
  GET /_cat/indices?v



## Migrated tenants as of May 19th
![image](https://github.com/user-attachments/assets/df05bacb-eb58-4492-b8c0-8db560ca4402)


### List of indexes: 
- **Query**:
  ```http
  GET /_cat/indices?v
![image](https://github.com/user-attachments/assets/0d220519-411e-461f-8942-0ac57f37a09d)

### Documents mapping:
- **Query**:
  ```http
  GET /25_documents/_mapping

<details>
<summary>View Documents Mapping</summary>

```json
{
  "25_documents" : {
    "mappings" : {
      "properties" : {
        "attributes" : {
          "properties" : {
            "attribute_id" : {
              "type" : "long"
            },
            "name" : {
              "type" : "text",
              "fields" : {
                "keyword" : {
                  "type" : "keyword",
                  "ignore_above" : 256
                }
              }
            },
            "value" : {
              "type" : "text",
              "fields" : {
                "keyword" : {
                  "type" : "keyword",
                  "ignore_above" : 256
                }
              }
            }
          }
        },
        "comments" : {
          "properties" : {
            "comment" : {
              "type" : "text",
              "fields" : {
                "keyword" : {
                  "type" : "keyword",
                  "ignore_above" : 256
                }
              }
            },
            "user_id" : {
              "type" : "long"
            }
          }
        },
        "content" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "content_id" : {
          "type" : "long"
        },
        "content_version" : {
          "type" : "long"
        },
        "creation_date" : {
          "type" : "long"
        },
        "document_id" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "extension" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "file_size" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "hashtags" : {
          "properties" : {
            "name" : {
              "type" : "text",
              "fields" : {
                "keyword" : {
                  "type" : "keyword",
                  "ignore_above" : 256
                }
              }
            }
          }
        },
        "last_modification_date" : {
          "type" : "long"
        },
        "linked_to" : {
          "properties" : {
            "name" : {
              "type" : "text",
              "fields" : {
                "keyword" : {
                  "type" : "keyword",
                  "ignore_above" : 256
                }
              }
            },
            "terciary_id" : {
              "type" : "long"
            }
          }
        },
        "packet" : {
          "properties" : {
            "packet_id" : {
              "type" : "long"
            }
          }
        },
        "primary_location" : {
          "properties" : {
            "id" : {
              "type" : "long"
            },
            "name" : {
              "type" : "text",
              "fields" : {
                "keyword" : {
                  "type" : "keyword",
                  "ignore_above" : 256
                }
              }
            }
          }
        },
        "secondary_location" : {
          "properties" : {
            "id" : {
              "type" : "long"
            },
            "name" : {
              "type" : "text",
              "fields" : {
                "keyword" : {
                  "type" : "keyword",
                  "ignore_above" : 256
                }
              }
            }
          }
        },
        "template" : {
          "type" : "text",
          "fields" : {
            "keyword" : {
              "type" : "keyword",
              "ignore_above" : 256
            }
          }
        },
        "tertiary_location" : {
          "properties" : {
            "id" : {
              "type" : "long"
            },
            "name" : {
              "type" : "text",
              "fields" : {
                "keyword" : {
                  "type" : "keyword",
                  "ignore_above" : 256
                }
              }
            }
          }
        }
      }
    }
  }
}
```
</details>

## Some Queries

### File Size = 1 MB
![image](https://github.com/user-attachments/assets/9e6eafdc-0d07-4537-bea9-f2d81050ecc9)
![image](https://github.com/user-attachments/assets/f2a8791a-e92a-4a6e-8e14-433083115c2e)
![image](https://github.com/user-attachments/assets/f72e6c7f-1c18-4f83-92a3-be2072c59fbb)

### File size = 10.00 MB
![image](https://github.com/user-attachments/assets/059b4e5f-cab3-4279-bd96-20914f34c243)
![image](https://github.com/user-attachments/assets/7ae59200-c768-48bb-bb41-efe9180b4c4a)











