from typing import Optional


class License:
    product: str
    owner: str
    type: str
    url: Optional[str]
    text: str


    def __init__(self, product: str, owner: str, type: str, url: Optional[str], text: str):
        self.product = product
        self.owner = owner
        self.type = type
        self.url = url
        self.text = text


class MITLicense(License):
    def __init__(self, product: str, owner: str, url: Optional[str], year: str | int):
        super().__init__(product, owner, "MIT License", url, """MIT License

Copyright (c) {YEAR} {OWNER}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.""".replace("{YEAR} {OWNER}", f"{year} {owner}"))


LICENSES: list[License] = [
    MITLicense("Kliko's modloader", "TheKliko", r"https://github.com/klikos-modloader/klikos-modloader", 2024),
    MITLicense("CustomTkinter", "Tom Schimansky", r"https://github.com/TomSchimansky/CustomTkinter", 2023),
    MITLicense("Fluent UI System Icons", "Microsoft Corporation", r"https://github.com/microsoft/fluentui-system-icons", 2020),
    MITLicense("pypresence", "qwertyquerty", r"https://github.com/qwertyquerty/pypresence", 2022),
    MITLicense("BloxstrapRPC SDK", "pizzaboxer", r"https://github.com/pizzaboxer/bloxstrap/wiki/Integrating-Bloxstrap-functionality-into-your-game", 2023)
]