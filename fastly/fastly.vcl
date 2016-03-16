sub vcl_deliver {
  if (req.http.Tmp-Set-Cookie) {
    set resp.http.Set-Cookie = req.http.Tmp-Set-Cookie;
  } 
  set resp.http.X-FastlySessionID = req.http.X-FastlySessionID;

#FASTLY deliver
}

sub vcl_log {
  log {"syslog 7c8d3Wi3OpxNiRk5PkRF8A syslog :: "} {"""} regsuball(fastly_info.state,{"""},{"\""}) {"""} "," obj.hits "," {"""} regsuball(obj.lastuse,{"""},{"\""}) {"""} "," resp.body_bytes_written "," time.elapsed "," geoip.latitude "," geoip.longitude "," {"""} regsuball(geoip.city,{"""},{"\""}) {"""} "," {"""} regsuball(geoip.country_name,{"""},{"\""}) {"""} "," geoip.postal_code "," {"""} regsuball(geoip.region,{"""},{"\""}) {"""} "," {"""} regsuball(client.ip,{"""},{"\""}) {"""} "," req.http.X-FastlySessionID "," resp.status "," req.request "," {"""} regsuball(req.url,{"""},{"\""}) {"""} "," {"""} regsuball(req.http.Referer,{"""},{"\""}) {"""} "," {"""} regsuball(req.http.User-Agent,{"""},{"\""}) {"""}
}

sub vcl_recv {
  set req.http.X-FastlySessionID = regsub(req.http.Cookie, "^.*[; ]?fastlysid=([0-9a-z]+)[; ]?.*$", "\1");
  if (req.http.X-FastlySessionID ~ "[0-9a-z]+") {
    set req.http.Tmp-Set-Cookie = req.http.Cookie;
  } else {
    set req.http.X-FastlySessionID = digest.hash_md5(now randomstr(32) client.ip);
    set req.http.Tmp-Set-Cookie = if(req.http.Cookie, req.http.Cookie "; ", "")  "fastlysid="  req.http.X-FastlySessionID  "; Expires="  time.add(now, 87600h);
  }
  unset req.http.Cookie;
 
#FASTLY recv
}

