import { check } from 'k6';
import http from 'k6/http';


export default function () {
  const foo = `${Math.random()}`;
  const res = http.get('http://localhost:5000');
  const res2 = http.get(`http://localhost:5000?foo=${foo}`);
  check(res, {
    'is bar': (r) => r.json('foo') === 'bar'
  })
  check(res2, {
    'is foo': (r) => r.json('foo') === foo
  })
}