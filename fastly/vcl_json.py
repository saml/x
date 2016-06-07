class String:
    def __init__(self, var, escape=False):
        self.var = var
        self.escape = escape

    def to_json(self):
        if self.escape:
            return r'{"""} regsuball(%s, {"""}, {"\""}) {"""}' % (self.var,)
        return r'{"""} %s {"""}' % (self.var,)

class Number:
    def __init__(self, var):
        self.var = var

    def to_json(self):
        return self.var


class Object:
    def __init__(self, o):
        self.o = o

    def to_json(self):
        segments = [
            r'{"{"}',
        ]
        key_vals = []
        for k, v in self.o.items():
            key_vals.append(r'{""%s":"} %s' % (k, v.to_json()))
        segments.append(r' {","} '.join(key_vals))
        segments.append(r'{"}"}')
        return ''.join(segments)


LogObject = Object({
    'Cache': Object({
        'Status': String('fastly_info.state'),
        'Hits': Number('obj.hits'),
        'LastUse': Number('obj.lastuse'),
    }),
    'Bytes': Number('resp.body_bytes_written'),
    'T': String('time.start'),
    'Elapsed': Number('time.elapsed'),
    'Geo': Object({
        'Lat': Number('geoip.latitude'),
        'Long': Number('geoip.longitude'),
        'City': String('geoip.city', True),
        'Country': String('geoip.country_name', True),
        'Postal': String('geoip.postal_code'),
        'Region': String('geoip.region', True),
    }),
    'IP': String('client.ip'),
    'Session': String('req.http.X-FastlySessionID'),
    'ClientID': String('req.http.X-ClientID'),
    'Status': Number('resp.status'),
    'Method': String('req.request'),
    'Host': String('req.http.Host'),
    'Path': String('req.url', True),
    'Referrer': String('req.http.Referer', True),
    'UA': String('req.http.User-Agent', True),
})

VCLTemplate = '''
sub vcl_deliver {
  if (req.http.Tmp-Set-Cookie != "") {
    set resp.http.Set-Cookie = req.http.Tmp-Set-Cookie;
  } 
  set resp.http.X-FastlySessionID = req.http.X-FastlySessionID;

#FASTLY deliver
}

sub vcl_log {
  log {"%(log_name)s :: "} %(log_format)s;
}

sub vcl_recv {
  set req.http.X-ClientID = req.http.Cookie:clientid;
  set req.http.X-FastlySessionID = req.http.Cookie:fastlysid;
  if (req.http.X-FastlySessionID != "") {
    set req.http.Tmp-Set-Cookie = "";
  } else {
    set req.http.X-FastlySessionID = digest.hash_md5(now randomstr(32) client.ip);
    set req.http.Tmp-Set-Cookie = "fastlysid=" + req.http.X-FastlySessionID + "; Expires=" + time.add(now, 87600h);
  }
 
#FASTLY recv
}
'''

def write_fastly_vcl(log_format, log_name = 'syslog 7c8d3Wi3OpxNiRk5PkRF8A syslog'):
    print(VCLTemplate % {'log_format': log_format, 'log_name': log_name})    


def main() -> None:
    write_fastly_vcl(LogObject.to_json())

if __name__ == '__main__':
    main()

