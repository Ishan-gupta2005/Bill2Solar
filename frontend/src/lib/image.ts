/** Downscale a bill photo so it stays under Bedrock's image limit and uploads fast. */
export async function prepareImage(file: Blob, maxSide = 1600, quality = 0.88): Promise<{ blob: Blob; url: string; width: number; height: number }> {
  const bitmap = await createImageBitmap(file)
  const scale = Math.min(1, maxSide / Math.max(bitmap.width, bitmap.height))
  const w = Math.round(bitmap.width * scale)
  const h = Math.round(bitmap.height * scale)
  const canvas = document.createElement('canvas')
  canvas.width = w
  canvas.height = h
  const ctx = canvas.getContext('2d')!
  ctx.drawImage(bitmap, 0, 0, w, h)
  bitmap.close()
  const blob: Blob = await new Promise((res, rej) => canvas.toBlob(b => (b ? res(b) : rej(new Error('encode failed'))), 'image/jpeg', quality))
  return { blob, url: URL.createObjectURL(blob), width: w, height: h }
}

export async function fetchAsBlob(url: string): Promise<Blob> {
  const r = await fetch(url)
  if (!r.ok) throw new Error(`fetch ${url} failed`)
  return r.blob()
}
