# On Demand Integrated Search Endpoint

## ✅ Test connected to CatoVPN

### 📎 Request sample to import into Postman

```bash
curl --location 'https://azwebapp-dd-integrated-search-test.azurewebsites.net/api/search' \
--header 'systemId: 25' \
--header 'Content-Type: application/json' \
--data '{
  "document": {
    "contentQuery": "oil"
  }
}'
