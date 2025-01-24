# IPHandler Project

## Overview

This project provides a solution for managing and querying tags associated with IP addresses using a Patricia trie for efficient lookups. The system is designed to handle large IP tag databases and provides an API for retrieving tags for specific IP addresses.

## Features

- **IP Tagging**: Retrieves tags associated with specific IP addresses based on predefined IP ranges.
- **High Performance**: Uses a Patricia trie for efficient prefix matching, even with millions of entries.
- **REST API**: Provides endpoints for querying tags via HTTP requests.
- **HTML Reports**: Generates user-friendly HTML reports for IP tags.

## How It Works

The project loads a JSON database containing IP ranges and associated tags. Each range is inserted into a Patricia trie, allowing fast lookups (thanks to [pytricia](https://github.com/jsommers/pytricia)). 

### Example Database

With a knowledge base (JSON file) containing:
```json
[
    {"tag": "foo", "ip_network": "192.0.2.0/24"}, 
    {"tag": "bar", "ip_network": "192.0.2.8/29"}, 
    {"tag": "bar", "ip_network": "10.20.0.0/16"}, 
    {"tag": "SPAM", "ip_network": "10.20.30.40/32"}
]
```

We want to return appropriate tags for the following IPs:
- 192.0.2.7 -> "foo" 
- 192.0.2.9 -> "foo" and "bar" 
- 10.20.30.40 -> "SPAM" and "bar" 
- 10.20.30.41 -> "bar" 
- 10.20.130.40 -> "bar" 
- 10.120.30.40 -> None
(similarly for: 0.0.0.0, 192.0.3.9, 203.0.113.187, and 255.255.255.255)

## Installation

Configure the JSON database file path in main.py.
Ensure the file contains the necessary IP and tag mappings. You already have a sample base `knowledge_base.json`.

Build and start the application using Docker:

`docker compose up --build`

## API Endpoints

All endpoints are available here `http://0.0.0.0:8000/docs#/`

`GET /ip-tags/{ip}`
Retrieves a list of tags associated with the specified IP address.

Parameters:
ip (IPv4Address): The IP address to query. Example:

`curl -X 'GET' http://0.0.0.0:8000/ip-tags/192.0.2.9'`

Response:

```json
["foo", "bar"]
```
`GET /ip-tags-report/{ip}`
Generates an HTML table with tags associated with the specified IP address.

Parameters:
ip (IPv4Address): The IP address to query.

curl -X 'GET' 'http://0.0.0.0:8000/ip-tags-report/192.0.2.9'

Response:


<table border="1">
    <tr>
        <th>Adres IP</th>
        <th>Pasujące tagi</th>
    </tr>
    <tr>
        <td rowspan="2">192.0.2.9</td>
        <td>foo</td>
    </tr>
    <tr>
        <td>bar</td>
    </tr>
</table>

## Testing

`docker exec -it <container_name> pytest test.py`

## Performance
 
Database with 21 dictionaries, repeated 100,000 times:

- Current algo: 0.18437 seconds
- Brute force algo: 10.18827 seconds


Database with 400,000 dictionaries, repeated 100 times:

- Current algo: 0.00010 seconds
- Brute force algo: 60.68723 seconds


Database with 4,000,000 dictionaries, repeated 100 times:

- Current algo: 0.00011 seconds
- Brute force algo: No data

Brute force algo that helped me compare performance:
```py
    def get_tags_for_ip_brute_force(self, ip: IPv4Address) -> List[str]:
        tags = set()
        for prefix in self.trie:
            if IPv4Address(ip) in IPv4Network(prefix):
                tags.add(self.trie[prefix])
        return sorted(tags)
```

## Acknowledgements
The project was completed according to the requirements specified during the recruitment process. It was a great opportunity to try using a trie in a real-world scenario, reflect on performance, and refresh my knowledge about IP addresses. Thank you! It was the best recruitment task I have ever worked on.