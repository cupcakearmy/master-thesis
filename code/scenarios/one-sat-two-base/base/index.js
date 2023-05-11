import Fastify from 'fastify'

const app = Fastify({ logger: { base: false } })

app.post('/transmit', async (request) => {
  request.log.info({ data: request.body })
})

app.get('/time', async () => {
  return new Date().toISOString()
})

try {
  process.on('SIGINT', () => app.close())
  process.on('SIGTERM', () => app.close())
  await app.listen({ port: 3000, host: '0.0.0.0' })
} catch (err) {
  app.log.error(err)
  process.exit(1)
}
