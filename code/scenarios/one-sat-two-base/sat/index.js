import pino from 'pino'

const logger = pino({ base: false })

const interval = setInterval(async () => {
  const ips = await fetch('http://localhost:42069/discoverable')
    .then((res) => res.json())
    .catch(() => [])

  if (!ips.length) {
    logger.info('no peers found')
    return
  }

  for (const ip of ips) {
    // Sync some data
    // Don't await on purpose
    fetch(`http://${ip}:3000/time`)
      .then((res) => res.text())
      .then((time) => logger.info({ peer: ip }, `time from peer: ${time}`))
      .catch(logger.error)
    fetch(`http://${ip}:3000/transmit`, { method: 'POST', body: `Observation: ${Math.random()}` }).catch(logger.error)
  }
}, 1000)

function exit() {
  clearInterval(interval)
  process.exit(0)
}
process.on('SIGINT', exit)
process.on('SIGTERM', exit)
