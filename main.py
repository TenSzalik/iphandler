from fastapi import Depends, FastAPI
from fastapi.responses import HTMLResponse
from ipaddress import IPv4Address
from typing import List
from iphandler import IPHandler, get_iphandler


app = FastAPI(
    title="IP Handler",
    description="IP Handler API 🚀",
    version="1.0.0",
)


@app.get("/ip-tags/{ip}", response_model=List[str])
def ip_tags(ip: IPv4Address, iphandler: IPHandler = Depends(get_iphandler)):
    """
    Retrieve a list of tags associated with the given IP address.

    This endpoint checks the knowledge base and returns all tags
    corresponding to IP ranges that match the given IP.

    Parameters
    ----------
    - ip : IPv4Address
        An IPv4 address in string format, e.g., "112.66.5.244".
    - iphandler : IPHandler
        An instance of the IPHandler class, which handles the Patricia trie.

    Returns
    -------
    - List[str] : A list of unique tags associated with the given IP address, sorted alphabetically, ex.:

        ["just a tag", "zażółć ♥", "{$(a-tag)$}"]
    """
    return iphandler.get_tags_for_ip(ip)


@app.get("/ip-tags-report/{ip}", response_class=HTMLResponse)
def ip_tags_report(ip: IPv4Address, iphandler: IPHandler = Depends(get_iphandler)):
    """
    Retrieve a list of tags associated with the given IP address in HTML format.

    This endpoint checks the knowledge base and returns all tags corresponding 
    to IP ranges that match the given IP, formatted as an HTML table.

    Parameters
    ----------
    - ip : IPv4Address
        An IPv4 address in string format, e.g., "112.66.5.244".
    - iphandler : IPHandler
        An instance of the IPHandler class, which handles the Patricia trie.

    Returns
    -------
    str : a table of HTML with IPs and tags, example:

        +==============+===============+
        |   Adres Ip   | Pasujące tagi |
        +--------------+---------------+
        | 112.66.5.244 | just a tag    |
        |              +---------------+
        |              | zażółć ♥      |
        |              +---------------+
        |              | {$(<br>       |
        |              |  a-tag        |
        |              | <br>)$}       |
        +==============+===============+
    """
    tags = iphandler.get_tags_for_ip(ip)
    tags_html = "".join(f"<tr><td>{tag}</td></tr>" for tag in tags[1:]) or ""
    rowspan = len(tags)
    if len(tags) > 0:
        tags = tags[0]
    else:
        tags = ""

    html_content = f"""
        <table border="1">
            <tr>
                <th>Adres IP</th>
                <th>Pasujące tagi</th>
            </tr>
            <tr>
                <td rowspan="{rowspan}">{ip}</td>
                <td>{tags}</td>
            </tr>
            {tags_html}
        </table>
    """
    return HTMLResponse(content=html_content)
