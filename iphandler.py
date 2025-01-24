"""
This module is responsible for handling IP.

Example
-------
With a knowledge base (JSON file) containing:
[
    {"tag": "foo", "ip_network": "192.0.2.0/24"}, 
    {"tag": "bar", "ip_network": "192.0.2.8/29"}, 
    {"tag": "bar", "ip_network": "10.20.0.0/16"}, 
    {"tag": "SPAM", "ip_network": "10.20.30.40/32"}
]

We want to return appropriate tags for the following IPs:
- 192.0.2.7 -> "foo" 
- 192.0.2.9 -> "foo" and "bar" 
- 10.20.30.40 -> "SPAM" and "bar" 
- 10.20.30.41 -> "bar" 
- 10.20.130.40 -> "bar" 
- 10.120.30.40 -> None
(similarly for: 0.0.0.0, 192.0.3.9, 203.0.113.187, and 255.255.255.255)

IPHandler performs this job via the get_tags_for_ip() method.

Decisions:
1. All IP-related operations are performed using an instance of the IPHandler class, 
specifically through the get_iphandler() function. This approach allows for easy mocking 
of the trie in testing scenarios.
    The singleton pattern was chosen because initializing the IPHandler instance is 
computationally expensive, particularly when working with a large database.
For example, on my machine, it takes several seconds to load a database containing 4 million rows.
By maintaining a single instance, we avoid repeated initialization costs and ensure efficient
handling of IP queries.

2. While it can be argued that loading the JSON database represents a distinct responsibility
that should be handled by a separate class, I believe doing so would unnecessarily increase
the complexity of the design in this specific case.
    The IPHandler class already encapsulates the core functionality of managing the Patricia
trie and processing IP-related queries, and separating the database loading logic would not
provide significant benefits. Instead, it would fragment the code and make the overall
system harder to maintain.

3. I have decided not to log an incorrect database path, because 
I don't see any benefits in doing so. The requirements also state that the database is always correct,
which is why I did not handle errors due to incorrect rows.
"""

from ipaddress import IPv4Address
import pytricia
from typing import List
import orjson


class IPHandler:
    """
    A class for efficiently managing and retrieving tags associated with IP addresses.

    Attributes
    ----------
    trie : pytricia.PyTricia
        A Patricia trie for storing IP networks and their corresponding tags.
    knowledge_base_file : str
        Path to the JSON file containing the IP knowledge base.
    knowledge_base : List[dict]
        Parsed knowledge base loaded from the JSON file.

    Methods
    -------
    get_tags_for_ip(ip: IPv4Address) -> List[str]
        Returns sorted and unique tags that match the given IP address.
    """

    def __init__(self, knowledge_base_file: str):
        """
        Initializes the IPHandler instance.

        Parameters
        ----------
        knowledge_base_file : str
            Path to the JSON file containing the IP knowledge base.
        """
        self.trie = pytricia.PyTricia()
        self.knowledge_base_file = knowledge_base_file
        self.knowledge_base = self._open_base()

    def _open_base(self) -> List[dict]:
        """
        Opens and parses the knowledge base JSON file.

        Returns
        -------
        List[dict]
            A list of dictionaries representing IP networks and their associated tags.
        """
        with open(self.knowledge_base_file, "rb") as f:
            return orjson.loads(f.read())

    def _prepare_trie(self) -> None:
        """
        Populates the Patricia trie with data from the knowledge base.

        This method ensures that multiple tags for THE SAME IP (not in the network) are
        concatenated using a unique delimiter "[*!UNIQUE_GLUE!*]".

        Example
        -------
        For the data:
            {"tag": "zażółć ♥", "ip_network": "192.0.2.8/29"},
            {"tag": "bak", "ip_network": "192.0.2.8/29"},

        Normally, the tag "zażółć ♥" would be overwritten by "bak",
        which is not accurate. To preserve both tags, one of the options
        is to concatenate them using a delimiter, like this:
            "zażółć ♥[*!UNIQUE_GLUE!*]bak"
        """
        seen_networks = set()
        for entry in self.knowledge_base:
            ip_network = entry["ip_network"]
            tag = entry["tag"]
            if ip_network in seen_networks:
                self.trie[ip_network] = f"{self.trie[ip_network]}[*!UNIQUE_GLUE!*]{tag}"
            else:
                self.trie[ip_network] = tag
                seen_networks.add(ip_network)
        return None

    def get_tags_for_ip(self, ip: IPv4Address) -> List[str]:
        """
        Retrieves unique and sorted tags for a given IP address.

        The method traverses the trie to find all IP networks containing the given IP address
        and collects the corresponding tags.

        Parameters
        ----------
        ip : IPv4Address
            The IP address for which tags are to be retrieved.

        Returns
        -------
        List[str]
            A sorted list of unique tags associated with the IP address.
        """
        tags = set()
        try:
            current_prefix = self.trie.get_key(str(ip))
            while current_prefix:
                tags.add(self.trie[current_prefix])
                current_prefix = self.trie.parent(current_prefix)
                # if len(tags) >= 10: # This limit could be useful for performance optimization,
                #     break           # but it has not been tested yet.

        except KeyError:
            return []

        processed_tags = set()
        for tag in tags:
            if "[*!UNIQUE_GLUE!*]" in tag:
                processed_tags.update(tag.split("[*!UNIQUE_GLUE!*]"))
            else:
                processed_tags.add(tag)

        return sorted(processed_tags)


# Create a singleton instance of IPHandler
iphandler = IPHandler(knowledge_base_file="bigdata.json")
iphandler._prepare_trie()


def get_iphandler() -> IPHandler:
    """
    Provides the singleton IPHandler instance.

    This function is designed to facilitate mocking during testing.

    Returns
    -------
    IPHandler
        The singleton instance of IPHandler.
    """
    return iphandler
