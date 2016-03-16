import re
from typing import NamedTuple, List

RowSpec = NamedTuple('RowSpec', [
    ('variable', str),
    ('should_quote', bool),
])

def to_vcl_str(spec: RowSpec) -> str:
    if spec.should_quote:
        return '{{"""}} regsuball({},{{"""}},{{"\\""}}) {{"""}}'.format(spec.variable)
    return spec.variable

Columns = [
    RowSpec('fastly_info.state', True),
    RowSpec('obj.hits', False),
    RowSpec('obj.lastuse', True),
    RowSpec('resp.body_bytes_written', False),
    RowSpec('time.elapsed', False),
    RowSpec('geoip.latitude', False),
    RowSpec('geoip.longitude', False),
    RowSpec('geoip.city', True),
    RowSpec('geoip.country_name', True),
    RowSpec('geoip.postal_code', False),
    RowSpec('geoip.region', True),
    RowSpec('client.ip', True),
    RowSpec('req.http.X-FastlySessionID', False),
    RowSpec('resp.status', False),
    RowSpec('req.request', False),
    RowSpec('req.url', True),
    RowSpec('req.http.Referer', True),
    RowSpec('req.http.User-Agent', True),
]

def main(columns: List[RowSpec]) -> None:
    print(' "," '.join(map(to_vcl_str, columns)))

if __name__ == '__main__':
    main(Columns)
