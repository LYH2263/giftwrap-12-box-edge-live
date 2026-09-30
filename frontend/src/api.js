async function request(method, path, body) {
  const r = await fetch(path, {
    method,
    headers: body !== undefined ? { 'Content-Type': 'application/json' } : {},
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  if (!r.ok) throw new Error(await r.text())
  return r.status === 204 ? null : r.json()
}
export const getJSON = (path) => request('GET', path)
export const postJSON = (path, body) => request('POST', path, body)
export const patchJSON = (path, body) => request('PATCH', path, body)
