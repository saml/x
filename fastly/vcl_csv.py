import re
from typing import NamedTuple, List

RowSpec = NamedTuple('RowSpec', [
    ('variable', str),
    ('should_quote', bool),
])

def to_vcl_str(spec: RowSpec) -> str:
    if spec.should_quote:
        return '{{"""}} regsuball({}, {{"""}}, {{"\\""}}) {{"""}}'.format(spec.variable)
    return spec.variable


Columns = [
    RowSpec('fastly_info.state', True),
    RowSpec('obj.hits', False),
    RowSpec('obj.lastuse', False),
    RowSpec('resp.body_bytes_written', False),
    RowSpec('time.elapsed', False),
    RowSpec('geoip.latitude', False),
    RowSpec('geoip.longitude', False),
    RowSpec('geoip.city', True),
    RowSpec('geoip.country_name', True),
    RowSpec('geoip.postal_code', False),
    RowSpec('geoip.region', True),
    RowSpec('client.ip', True),
    RowSpec('req.http.X-FastlySessionID', True),
    RowSpec('resp.status', False),
    RowSpec('req.request', False),
    RowSpec('req.url', True),
    RowSpec('req.http.Referer', True),
    RowSpec('req.http.User-Agent', True),
]

VCLTemplate = '''
sub vcl_deliver {
  if (req.http.Tmp-Set-Cookie) {
    set resp.http.Set-Cookie = req.http.Tmp-Set-Cookie;
  } 
  set resp.http.X-FastlySessionID = req.http.X-FastlySessionID;

#FASTLY deliver
}

sub vcl_log {
  log {"%(log_name)s :: "} %(log_format)s;
}

sub vcl_recv {
  set req.http.X-FastlySessionID = regsub(req.http.Cookie, "^.*(?:; )?fastlysid=([0-9a-z]+)(?:; )?.*$", "\\1");
  if (req.http.X-FastlySessionID ~ "^[0-9a-z]+$") {
    set req.http.Tmp-Set-Cookie = req.http.Cookie;
  } else {
    set req.http.X-FastlySessionID = digest.hash_md5(now randomstr(32) client.ip);
    set req.http.Tmp-Set-Cookie = if(req.http.Cookie, req.http.Cookie "; ", "")  "fastlysid="  req.http.X-FastlySessionID  "; Expires="  time.add(now, 87600h);
  }
  unset req.http.Cookie;
 
#FASTLY recv
}
'''

def write_fastly_vcl(log_format: str, log_name: str = 'syslog 7c8d3Wi3OpxNiRk5PkRF8A syslog') -> None:
    print(VCLTemplate % {'log_format': log_format, 'log_name': log_name})    


def main(columns: List[RowSpec]) -> None:
    write_fastly_vcl(' {","} '.join(map(to_vcl_str, columns)))

if __name__ == '__main__':
    main(Columns)
